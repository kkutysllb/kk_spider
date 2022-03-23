#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# @Author kkutysllb
import pymysql
import requests
import random
import time
from lxml import etree
from fake_useragent import UserAgent


class LianjiaSecondHouseInfos(object):
    def __init__(self):
        self.base_url = 'https://xa.lianjia.com/ershoufang/pg{}'
        self.ua = {'User-Agent': UserAgent().random}

    def get_html(self, url):
        html = requests.get(url=url, headers=self.ua).text
        parser_html = etree.HTML(html)
        return parser_html

    def parser_html(self, html):
        xpath_root = '//ul[@class="sellListContent"]/li[@class="clear LOGVIEWDATA LOGCLICKDATA"]'
        datas = html.xpath(xpath_root)
        house_infos = []
        # 网页数据解析
        for item in datas:
            house_data = dict()
            # 图片
            house_data['img'] = item.xpath('.//a/img[@class="lj-lazy"]/@src')[0]
            # 行政区
            house_data['area'] = item.xpath('.//a/img[@class="lj-lazy"]/@alt')[0]
            # 名称
            house_data['name'] = item.xpath('.//div[@class="info clear"]/div[@class="title"]/a/text()')[0]
            # 社区
            house_data['community'] = item.xpath(
                './/div[@class="info clear"]/div[@class="flood"]/div[@class="positionInfo"]/a[@data-el="region"]/text()')[
                0].strip()
            # 信息
            house_data['info'] = \
                item.xpath('.//div[@class="info clear"]/div[@class="address"]/div[@class="houseInfo"]/text()')[
                    0].strip()
            # 总价
            house_data['total_price'] = '￥' + item.xpath(
                './/div[@class="info clear"]/div[@class="priceInfo"]/div[@class="totalPrice totalPrice2"]/span/text()')[
                0].strip() + '万元'
            # 单价
            house_data['unit_price'] = '￥' + item.xpath(
                './/div[@class="info clear"]/div[@class="priceInfo"]/div[@class="unitPrice"]/span/text()')[0].strip()
            house_infos.append(house_data)

        return house_infos

    def save_db(self, data_list):
        sql_list = []
        for item in data_list:
            sql_list.append(tuple(item.values()))

        db = pymysql.connect(host='localhost',
                             user='root',
                             password='Oms_2600',
                             db='lianjia_second_handhouse',
                             port=3306)

        cursor = db.cursor()
        sql = 'insert into t_lianjia_secondhouse_xa (img,area,name,community,info,total_price,unit_price) values(%s,%s,%s,%s,%s,%s,%s)'
        cursor.executemany(sql, sql_list)

        db.commit()
        cursor.close()
        db.close()

    def run(self):
        """入口函数"""
        for page in range(1, 101):
            url = self.base_url.format(page)
            html = self.get_html(url)
            houuse_list = self.parser_html(html)
            self.save_db(houuse_list)
            time.sleep(random.randint(1, 2))


if __name__ == '__main__':
    house_obj = LianjiaSecondHouseInfos()
    start_time = time.time()
    house_obj.run()
    end_time = time.time()
    print('总用时: %.2f秒' % (end_time - start_time))
