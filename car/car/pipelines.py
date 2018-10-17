# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.conf import settings
from .items import *
import warnings


class CarPipeline(object):
    def __init__(self):
        mongo_host = settings['MONGO_HOST']
        mongo_port = settings['MONGO_PORT']
        mongo_db = settings['MONGO_DB']
        self.clct_brand = MongoClient(mongo_host, mongo_port)[mongo_db]['brand']
        self.clct_sub_brand = MongoClient(mongo_host, mongo_port)[mongo_db]['sub_brand']
        self.clct_car_train = MongoClient(mongo_host, mongo_port)[mongo_db]['car_train']
        self.clct_car = MongoClient(mongo_host, mongo_port)[mongo_db]['car']
        self.clct_car_config = MongoClient(mongo_host, mongo_port)[mongo_db]['car_config']
        # self.clct_brand.drop()
        # self.clct_sub_brand.drop()
        # self.clct_car_train.drop()
        # self.clct_car.drop()
        self.clct_car_config.drop()
        #
        # self.clct_brand.create_index('id')
        # self.clct_sub_brand.create_index('id')
        # self.clct_car_train.create_index('id')
        # self.clct_car.create_index('id')
        self.clct_car_config.create_index('id')


    def process_item(self, item, spider):
        if spider.name == 'autohome_brand':
            if isinstance(item, BrandItem):
                self.save_brand(item, spider)
            elif isinstance(item, SubBrandItem):
                self.save_sub_brand(item, spider)
            elif isinstance(item, CarTrainItem):
                self.save_cartrain(item, spider)
            else:
                warnings.warn('can not deal %s : %s'%(item.__class__.__name__, str(item)))
        if spider.name == 'autohome_car':
            if isinstance(item, CarItem):
                self.save_car(item, spider)
            else:
                warnings.warn('can not deal %s : %s'%(item.__class__.__name__, str(item)))

        if spider.name == 'autohome_car_config':
            if isinstance(item, CarConfigItem):
                self.save_car_config(item, spider)

        return item

    def save_brand(self, item, spider):
        self.clct_brand.insert_one(dict(item))

    def save_sub_brand(self, item, spider):
        self.clct_sub_brand.insert_one(dict(item))

    def save_cartrain(self, item, spider):
        self.clct_car_train.insert_one(dict(item))


    def save_car(self, item, spider):
        self.clct_car.insert_one(dict(item))

    def save_car_config(self, item, spider):
        self.clct_car_config.insert_one(dict(item))