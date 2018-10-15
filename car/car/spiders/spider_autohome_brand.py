from scrapy import Spider, Request
from bs4 import BeautifulSoup
from ..items import CarTrainItem, SubBrandItem, BrandItem
import re

RE_sub_brand = re.compile('brand-\d+-(\d+)\.html')


class AutoHomeBrandSpider(Spider):
    name = "autohome_brand"

    def start_requests(self):
        for char in [chr(i) for i in range(ord("A"), ord("Z") + 1)]:
            yield Request(url='https://www.autohome.com.cn/grade/carhtml/{}.html'.format(char), callback=self.parse)

    def parse(self, response):
        bs = BeautifulSoup(response.body.decode('gbk'), 'lxml')
        dls = bs.select('dl')

        for dl in dls:
            brand_data = dl.select('dt > div > a')[0]
            brand_name = brand_data.text
            brand_id = dl.get('id', '')
            brand_url = self.add_url_prefix(brand_data.get('href', '').split('#')[0], prefix='https:')
            item_brand = BrandItem(**{'name': brand_name, 'url': brand_url, 'id': brand_id})
            yield item_brand
            dd = dl.select('dd')[0]
            divs = dd.select('div.h3-tit > a')
            uls = dd.select('ul.rank-list-ul')
            brand_sub_brand_num = 0
            brand_car_num = 0
            for div, ul in zip(divs, uls):
                sub_brand_name = div.text
                sub_brand_url = self.add_url_prefix(div.get('href', '').split('#')[0], prefix='https:')
                sub_brand_id_ = RE_sub_brand.findall(sub_brand_url)
                sub_brand_id = '-'.join([brand_id, sub_brand_id_[0] if sub_brand_id_ else ''])
                item_sub_brand = SubBrandItem(**{'name': sub_brand_name,
                                                 'url': sub_brand_url,
                                                 'id': sub_brand_id,
                                                 'brand': brand_id})
                brand_sub_brand_num += 1
                yield item_sub_brand
                for li in ul.select('li'):
                    car_id = li.get('id')
                    car_ = li.select('h4 > a')
                    car = car_[0] if car_ else None
                    if car is None:
                        continue
                    car_name = car.text
                    car_url = self.add_url_prefix(car.get('href', '').split('#')[0], prefix='https:')
                    car_data = {'name': car_name,
                                'url': car_url,
                                'id': car_id,
                                'brand': brand_id,
                                'sub_brand': sub_brand_id}
                    item_car = CarTrainItem(**car_data)
                    brand_car_num += 1
                    yield item_car
            self.logger.info('%s, sub_brand_num: %s, car_num:%s' % (brand_name, brand_sub_brand_num, brand_car_num))


    @staticmethod
    def add_url_prefix(url, prefix=''):
        url = prefix + url if url else ''
        return url
