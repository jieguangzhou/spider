from scrapy import Spider, Request
from scrapy.conf import settings
from bs4 import BeautifulSoup
from ..items import CarItem
import re
from pymongo import MongoClient
import json

RE_config = re.compile('(spec/\d+)')


class AutoHomeCarSpider(Spider):
    name = "autohome_car"

    def start_requests(self):
        mongo_host = settings['MONGO_HOST']
        mongo_port = settings['MONGO_PORT']
        mongo_db = settings['MONGO_DB']
        clct_car_train = MongoClient(mongo_host, mongo_port)[mongo_db]['car_train']
        for car_train in clct_car_train.find():
            url = car_train['url']
            request = Request(url, callback=self.parse)
            request.meta.update(car_train)
            yield request

    def parse(self, response):
        bs = BeautifulSoup(response.body.decode('gbk'), 'lxml')
        car_train_data = response.meta
        dls = bs.select('div[class=spec-wrap\ active] > dl')
        n = 0
        for dl in dls:
            dds = dl.select('dd')
            group = dl.select('dt > div.spec-name > span')[0].text
            for dd in dds:
                car_ = dd.select('div.spec-name > div > p[data-gcjid]')
                if car_:
                    car_ = car_[0]
                    car_id = car_.get('id', '')
                    car_ = car_.select('a')
                else:
                    self.logger.error(str(response.meta))
                    continue
                if car_:
                    car_name = car_[0].text
                    car_url = self.add_url_prefix(car_[0].get('href').split('#')[0], 'https://www.autohome.com.cn')
                    car_info_url = 'https://car.autohome.com.cn/config/spec/{}.html'.format(car_id.split('_')[1])
                else:
                    continue

                tags = [i.text for i in dd.select('div.spec-name > div > p > span')]

                item_car = CarItem(name=car_name,
                                   url=car_url,
                                   id=car_id,
                                   Transmission=tags[1],
                                   DrivingMode=tags[0],
                                   group=group,
                                   sub_brand=car_train_data['sub_brand'],
                                   brand=car_train_data['brand'],
                                   car_train=car_train_data['id'],
                                   car_info_url=car_info_url)
                yield item_car
                n += 1

        for year_ in bs.select('#haltList > li > a'):
            year_id = year_.get('data-yearid')
            request = Request(
                'https://www.autohome.com.cn/ashx/series_allspec.ashx?s={}&y={}'.format(car_train_data['id'][1:],
                                                                                        year_id),
                callback=self.parse_other_years)
            request.meta.update(car_train_data)
            yield request

        self.logger.info('%s  %s' % (car_train_data['name'], n))

    def parse_other_years(self, response):
        datas = json.loads(response.body.decode('gbk'))
        car_train_data = response.meta
        for spec in datas['Spec']:
            car_name = spec['Name']
            car_url = 'https://www.autohome.com.cn/spec/{}/'.format(spec['Id'])
            car_id = 'spec_' + str(spec['Id'])
            car_info_url = self.get_config_url(car_id)
            item_car = CarItem(name=car_name,
                               url=car_url,
                               id=car_id,
                               Transmission=spec.get('Transmission', ''),
                               DrivingMode=spec.get('DrivingModeName', ''),
                               group=spec.get('GroupName', ''),
                               sub_brand=car_train_data['sub_brand'],
                               brand=car_train_data['brand'],
                               car_train=car_train_data['id'],
                               car_info_url=car_info_url)
            yield item_car


    @staticmethod
    def add_url_prefix(url, prefix=''):
        url = prefix + url if url else ''
        return url

    @staticmethod
    def get_config_url(car_id):
        return 'https://car.autohome.com.cn/config/spec/{}.html'.format(car_id.split('_')[1])