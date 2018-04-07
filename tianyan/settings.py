# -*- coding: utf-8 -*-

# Scrapy settings for tianyan project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'tianyan'

SPIDER_MODULES = ['tianyan.spiders']
NEWSPIDER_MODULE = 'tianyan.spiders'


#禁用root规则
ROBOTSTXT_OBEY = False
#每次请求延迟时间
DOWNLOAD_DELAY =1
#请求中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware':None,
    'tianyan.middlewares.RotateUserAgentMiddleware':400,
}
#保存管道
ITEM_PIPELINES = {
    'tianyan.pipelines.MongoPipeline':1,
    #'tianyan.pipelines.ExcelPipeline':1,
}
#mongodb数据库连接
MONGO_URI="mongodb://127.0.0.1:27017/"
MONGO_DATABASE="tianyan"
#禁用cookie管理
#COOKIES_ENABLES=False

# 使用scrapy-redis里的去重组件，不使用scrapy默认的去重方式
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 使用scrapy-redis里的调度器组件，不使用默认的调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 指定数据库的主机IP
REDIS_HOST = "127.0.0.1"
# 指定数据库的端口号
REDIS_PORT = 6379

LOG_LEVEL= 'DEBUG' #INFO