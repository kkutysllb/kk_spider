#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# @Author kkutysllb

import requests
import random
import time
from lxml import etree
from fake_useragent import UserAgent
import pymysql


def get_headers():
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    return headers


def get_html(url, headers):
    res = requests.get(url=url, headers=headers).text
    return res


def parser_html(html):
    xpath_root = '//div[@class="article"]/ol[@class="grid_view"]/li/div[@class="item"]'
    par_html = etree.HTML(html)
    datas = par_html.xpath(xpath_root)
    movies_datas = []
    for item in datas:
        data = dict()
        # 排名
        data['ranking'] = item.xpath('.//div[@class="pic"]/em/text()')[0]
        # 图片
        data['img'] = item.xpath('.//div[@class="pic"]/a/img/@src')[0]
        # 片名
        data['name'] = item.xpath('.//div[@class="pic"]/a/img/@alt')[0]
        # 导演&主演
        data['members'] = item.xpath('.//div[@class="info"]/div[@class="bd"]/p/text()')[0].strip().replace(u'\xa0',
                                                                                                           u' ')
        # 影片信息
        data['infos'] = item.xpath('.//div[@class="info"]/div[@class="bd"]/p/text()')[1].strip().replace(u'\xa0', u' ')
        # 评分
        data['rating_num'] = \
            item.xpath('.//div[@class="info"]/div[@class="bd"]/div[@class="star"]/span[@class="rating_num"]/text()')[0]

        movies_datas.append(data)
    return movies_datas


def save_mysqldb(movies_infos):
    sql_list = []
    for item in movies_infos:
        sql_list.append(tuple(item.values()))

    db = pymysql.connect(host='localhost',
                         user='root',
                         password='Oms_2600',
                         db='kk_movies',
                         port=3306)
    cursor = db.cursor()
    sql = 'insert into t_douban_movies (ranking, img, name, members, infos, rating_num) values(%s,%s,%s,%s,%s,%s)'
    cursor.executemany(sql, sql_list)
    db.commit()
    cursor.close()
    db.close()


if __name__ == '__main__':
    url = 'https://movie.douban.com/top250?start={}'
    start_time = time.time()
    for page in range(1, 11):
        pn = (page - 1) * 25
        url = url.format(pn)
        headers = get_headers()
        html = get_html(url, headers)
        data_lst = parser_html(html)
        save_mysqldb(data_lst)
        time.sleep(random.randint(1, 2))
    end_time = time.time()
    print('总用时: %.2f秒' % (end_time - start_time))
