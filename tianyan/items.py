# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HumanCompany(scrapy.Item):
    hid_cid=scrapy.Field()
    human_company=scrapy.Field()
    hid=scrapy.Field()
    hname=scrapy.Field()
    cid=scrapy.Field()
    cname=scrapy.Field()
    ts=scrapy.Field()
    status=scrapy.Field()



