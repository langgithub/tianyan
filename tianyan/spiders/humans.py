# -*- coding: utf-8 -*-
import scrapy
from ..pipelines import *
from scrapy_redis.spiders import RedisSpider
import json
import time
from ..items import *
import re
from urllib.parse import unquote
import threading


class HumansSpider(RedisSpider):
    name = 'humans'
    allowed_domains = ['www.tianyancha.com']
    start_urls = ['https://www.tianyancha.com/humans']
    redis_key = "tianyan:humans"
    mongo = MongoPipeline()
    redis = RedisPipeline()
    buzhou = 2

    def mongo_to_redis(self):
        while True:
            if self.redis.list_len(self.redis_key) ==0:
                seeds = self.mongo.humans_page_seed_find()
                print("查到人员(复数)列表种子=======》" + str(seeds.count()) + "个")
                for seed in seeds:
                    self.redis.set_seed(self.redis_key, seed["url"])
                seeds = self.mongo.human_page_seed_find()
                print("查到人名（单数）列表种子=======》" + str(seeds.count()) + "个")
                for seed in seeds:
                    self.redis.set_seed(self.redis_key, seed["url"])
            print("redis 装入完毕，休息10s")
            time.sleep(10)

    def start_requests(self):
        if self.buzhou==1:
            for url in self.start_urls:
                yield scrapy.Request(url,callback=self.parse_humans_page)
        elif self.buzhou==2:
            t = threading.Thread(target=self.mongo_to_redis)
            t.start()
        elif self.buzhou==3:
            url="https://www.tianyancha.com/humans/100/p1"
            yield scrapy.Request(url)
        elif self.buzhou==4:
            url="https://www.tianyancha.com/human/2191699923?pn=1"
            yield scrapy.Request(url)
        elif self.buzhou==5:
            url="https://www.tianyancha.com/humans/487/p6"
            yield scrapy.Request(url,callback=self.parse_humans_name)
        elif self.buzhou==30:
            seedList=self.mongo.find_people_seed(1)
            for seed in seedList:
                if 'curNum' in seed.keys():
                    url = "{0}?pn={1}".format(seed['url'], seed['curNum'])
                else:
                    url = "{0}?pn=1".format(seed['url'])
                print("fetch------>",url)
                yield scrapy.Request(url,cookies={"auth_token":self.cookieValue})

    def parse_humans_page(self,response):
        if self.check_page(response.url)==False:
            return
        html = scrapy.Selector(text=response.body)
        all_a = html.css("div.pl20 div.pt15 a.c9::attr(href)").extract()
        for a in all_a:
            yield scrapy.Request(url=a,callback=self.parse_humans_name)

    def parse_humans_name(self, response):
        if self.check_page(response.url)==False:
            return
        html=scrapy.Selector(text=response.body)
        total_page=html.css("#web-content > div > div > div.pl20.pr20.f14 > div.company_pager > div::text").extract()
        if len(total_page)!=0:
            pages = int(total_page[0])+1
            for page in range(1,pages):
                url=response.url+"/p"+str(page)
                seed={"url":url,"formUrl":response.url,"status":0,
                      "ts":time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))}
                self.mongo.humans_page_seed_insert(seed)
            print(response.url + "------------------>" + total_page[0])
        else:
            url = response.url + "/p1"
            seed = {"url": url, "formUrl": response.url, "status": 0,
                    "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}
            self.mongo.humans_page_seed_insert(seed)
            print(response.url + "------------------>1")

    def parse_human_page(self,response):
        if self.check_page(response.url)==False:
            return
        html = scrapy.Selector(text=response.body)
        total_page = html.css("div.total::text").extract()
        if len(total_page) != 0:
            pages = int(total_page[0]) + 1
            for page in range(1, pages):
                url = response.url + "?pn=" + str(page)
                seed = {"url": url, "formUrl": response.url, "status": 0,
                        "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}
                self.mongo.human_page_seed_insert(seed)
            print(response.url + "------------------>" + total_page[0])
        else:
            url = response.url + "?pn=1"
            seed = {"url": url, "formUrl": response.url, "status": 0,
                    "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}
            self.mongo.human_page_seed_insert(seed)



    def parse(self, response):
        if self.check_page(response.url)==False:
            return
        html = scrapy.Selector(text=response.body)
        if "?pn=" in response.url:
            item=HumanCompany()
            human_box=html.css("div.human-box")
            for human in human_box:
                json_flag=re.search("onclick='nextPartners\(event,this,(\{.*\})\)'?",human.extract())
                if json_flag is not None:
                    json_data=json.loads(json_flag.group(1))
                    for office in json_data["office"]:
                        item["cid"]=str(office["cid"])
                        item["hid"]=str(json_data["hid"])
                        item["cname"]=office["companyName"]
                        item["hname"]=json_data["name"]
                        item["ts"]=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        item["status"]=0
                        item["hid_cid"]=item["hid"]+"-c"+item["cid"]
                        yield item
                else:
                    item["cname"]=html.css("div.human-bottom span.human-prov-company-lg::text").extract()[0]
                    item["hname"] = html.css("span.chineseText span.new-err::text").extract()[0]
                    item["cid"] = re.search("onclick=\"toHumanDetail\(event,(.*),(.*),.*\)\"", human.extract()).group(2)
                    item["hid"] = re.search("onclick=\"toHumanDetail\(event,(.*),(.*),.*\)\"", human.extract()).group(1)
                    item["ts"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    item["status"] = 0
                    item["hid_cid"] = item["hid"] + "-c" + item["cid"]
                    yield item
        else:
            human_a=html.css(".new-c2::attr(href)").extract()
            for url in human_a:
                yield scrapy.Request(url=url, callback=self.parse_human_page)

    def check_page(self,url):
        check = re.search(r'(.*login\?.*)', url)
        check1 = re.search(r'(.*captcha/verify\?.*)', url)
        if check is not None:
            print("需要登录，请检查")
            return False
        if check1 is not None:
            print("验证码识别，请检查")
            return False
        return True

