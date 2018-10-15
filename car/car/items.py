# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class BrandItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    pass

class SubBrandItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    brand = scrapy.Field()
    pass

class CarTrainItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    sub_brand = scrapy.Field()
    brand = scrapy.Field()
    pass

class CarItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    sub_brand = scrapy.Field()
    brand = scrapy.Field()
    car_train = scrapy.Field()
    car_info_url = scrapy.Field()
    group = scrapy.Field()
    DrivingMode = scrapy.Field()
    Transmission = scrapy.Field()
    pass


