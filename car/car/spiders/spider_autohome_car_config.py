from scrapy import Spider, Request
from scrapy_splash import SplashRequest
from scrapy.conf import settings
from bs4 import BeautifulSoup
from ..items import CarConfigItem
import re
from pymongo import MongoClient


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

    def parse(self, response):
        bs = BeautifulSoup(response.body.decode('utf-8'), 'lxml')
        print(bs.text)
        car_data = response.meta
        tables = bs.select('table > tbody')
        tables_cfg = {}
        for idx, table in enumerate(tables):

            trs = table.select('tr[id|=tr]')
            table_name_ = table.select('h3 > span')
            if table_name_:
                table_name = table_name_[0].text
            else:
                table_name = idx
            table_cfg = {}
            for tr in trs:
                key = tr.text
                value = tr.select('td')[0].text
                table_cfg[key] = value

            tables_cfg[table_name] = table_cfg

        item_config = CarConfigItem(id=car_data['id'], config=tables_cfg)

        yield item_config


        self.logger.info(car_data['id'])

