from scrapy import Spider, Request
from scrapy_splash import SplashRequest
from scrapy.conf import settings
from bs4 import BeautifulSoup
from ..items import CarConfigItem
import re
from pymongo import MongoClient
import logging
import json
import PyV8

ctx = PyV8.JSContext()
ctx.enter()

class AutoHomeCarSpider(Spider):
    name = "autohome_car_config"

    def start_requests(self):
        mongo_host = settings['MONGO_HOST']
        mongo_port = settings['MONGO_PORT']
        mongo_db = settings['MONGO_DB']
        clct_car = MongoClient(mongo_host, mongo_port)[mongo_db]['car']
        for car in clct_car.find():

            url = car['car_info_url']
            request = SplashRequest(url, callback=self.parse)
            request.meta.update(car)
            yield request


        # url = 'https://car.autohome.com.cn/config/spec/32040.html'
        # request = SplashRequest(url, callback=self.parse)
        # request.meta['id'] = '32040'
        # yield request

    def parse(self, response):
        text = response.body.decode('utf-8')
        car_data = response.meta
        config = get_config(text)['result']['paramtypeitems']

        item_config = CarConfigItem(id=car_data['id'], config=config)

        yield item_config


        self.logger.info(car_data['id'])


def get_config(text):
    alljs = makejs(text)
    config = re.findall("var config = (.*?);\n", text, re.DOTALL)[0]
    ctx.eval(alljs)
    result = str(ctx.eval('rules'))
    mapping = [extract(i) for i in result.split('#')]
    for key, value in mapping:
        config = config.replace(key, value)
    return json.loads(config)



def extract(string):
    key = "<span class='" + string[1: string.index(':')] + "'></span>"
    value = re.sub('.*content:"(.*?)".*', '\\1', string)
    return key, value

def makejs(html):
    try:
        alljs = ("var rules = '';"
                 "var document = {};"
                 "document.createElement = function() {"
                 "      return {"
                 "              sheet: {"
                 "                      insertRule: function(rule, i) {"
                 "                              if (rules.length == 0) {"
                 "                                      rules = rule;"
                 "                              } else {"
                 "                                      rules = rules + '#' + rule;"
                 "                              }"
                 "                      }"
                 "              }"
                 "      }"
                 "};"
                 "document.querySelectorAll = function() {"
                 "      return {};"
                 "};"
                 "document.head = {};"
                 "document.head.appendChild = function() {};"

                 "var window = {};"
                 "window.decodeURIComponent = decodeURIComponent;")

        js = re.findall('(\(function\([a-zA-Z]{2}.*?_\).*?\(document\);)', html)
        for item in js:
            alljs = alljs + item
        return alljs
    except:
        logging.exception('makejs function exception')
        return None