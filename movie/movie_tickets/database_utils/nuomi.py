"""
百度糯米
"""
import time
import os
import sys
import requests
import json
import re
from queue import Queue
from threading import Thread
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_tickets.settings")
django.setup()

from movie.models import CinemaUrl


class NuoMiSpider:

    def __init__(self):
        self.cityListUrl = "http://dianying.nuomi.com/common/city/citylist?hasLetter=false&isjson=false&channel=&client="
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"}
        self.city_queue = self.get_city_queue()  # a queue of dict like {'id': 320, 'name': '鞍山', 'pinyin': 'anshan'}
        self.cinema_info_list = list()  # a list of dict like { 'city': 城市名, 'district': 区县名, 'cinema_name': 电影院名字, 'url': '电影院主页'}
        self.city_district_dict = dict()  # map from cityId to a list of district id

    def add_district(self):
        """
        添加所有的区/县的id
        :return:
        """
        while not self.city_queue.empty():
            city = self.city_queue.get()
            cityId = city['id']
            timestamp = int(time.time() * 1000)
            url = f"http://dianying.nuomi.com/cinema?pagelets[]=pageletCinema&reqID=0&cityId={cityId}&pageSize=6&pageNum=0&date={timestamp}&sortType=2&t={timestamp}"
            try:
                response = requests.get(url, headers=self.headers)
                pattern = r"""data-id=\\"(.*?)\\" data-log=\\"{'da_src':'webCinemaPg.filterBk.areaLnk'}\\"><span>(.*?)</span>"""
                district_ids = re.findall(pattern, response.text, re.S)  # 所有区的id
                self.city_district_dict[cityId] = district_ids  # 从cityId映射到这个city所有district的id
                print(cityId, district_ids)
            except Exception as e:
                print(e)
                self.city_queue.put(city)

    def get_city_queue(self):
        """
        获取所有的city, 用队列存储,
        :return: a queue of elements like {'id': 320, 'name': '鞍山', 'pinyin': 'anshan'}
        """
        response = requests.get(self.cityListUrl, headers=self.headers)
        response.raise_for_status()
        json_dict = json.loads(response.text)
        cities = json_dict['data']['all']
        print(cities)
        queue = Queue()
        for city in cities:
            queue.put(city)
        return queue

    def add_cinema_url(self):
        """
        添加全国的电影院的{'city': cityName, 'district': areaId[1], 'cinema_name': cinemaName,
                               'location': cinemaAddress, 'url': cinema_url}
        :return:
        """
        while not self.city_queue.empty():
            city = self.city_queue.get()
            cityId = city['id']
            cityName = city['name']
            for district_id_name in self.city_district_dict[cityId]:  # 取出每个城市所有区的id
                self.get_cinema_list(cityName=cityName, cityId=cityId, areaId=district_id_name)

    def get_cinema_list(self, cityName, cityId, areaId, pageNum=0, pageSize=6):
        """
        传入city Id,获取该城市所有的电影院的url
        :return:
        """
        url = "http://dianying.nuomi.com/cinema"

        params = {'pagelets[]': 'pageletCinemalist@pageletCinema',
                  'reqID': pageNum,
                  'cityId': cityId,
                  'pageSize': pageSize,
                  'pageNum': pageNum,
                  'date': int(time.time() * 1000),
                  'sortType': '2',
                  'areaId': areaId[0],
                  't': int(time.time() * 1000),
                  }
        try:
            response = requests.get(url, params=params, headers=self.headers)
            pattern = r'{\\"cinemaId\\":(\d*?)}'
            cinemaIdList = re.findall(pattern, response.text)[::2]

            cinemaNameList = re.findall(r"""nameLnk\'}\\">(.*?)</span>""", response.text)  # 名字
            cinemaAddressList = re.findall(r"""<span class=\\"fl text\\">(.*?)</span>""", response.text)  # 地址

            for cinemaId, cinemaName, cinemaAddress in zip(cinemaIdList, cinemaNameList, cinemaAddressList):
                cinema_url = f"http://dianying.nuomi.com/cinema/cinemadetail?cityId={cityId}&cinemaId={cinemaId}"

                cinema_data = {'city': cityName, 'district': areaId[1], 'cinema_name': cinemaName,
                               'location': cinemaAddress, 'url': cinema_url}

                cinema_url_obj, created = CinemaUrl.objects.get_or_create(city=cityName, district=areaId[1],
                                                                          cinema_name=cinemaName,
                                                                          defaults={"location": cinemaAddress,
                                                                                    "nuomi_url": cinema_url})
                print(cinema_url_obj, created)
                self.cinema_info_list.append(cinema_data)
            if len(cinemaIdList) >= pageSize:
                self.get_cinema_list(cityName, cityId, areaId, pageNum + 1, pageSize)
        except Exception as e:
            print(e)
            self.get_cinema_list(cityName, cityId, areaId, pageNum, pageSize)

    def run(self):
        ths = []
        for i in range(5):
            thread = Thread(target=self.add_district)
            thread.start()
            ths.append(thread)
        for th in ths:
            th.join()
        print("地区添加成功")

        self.city_queue = self.get_city_queue()
        ths = []
        for i in range(5):
            thread = Thread(target=self.add_cinema_url)
            thread.start()
            ths.append(thread)
        for th in ths:
            th.join()
        print("电影院添加成功")


if __name__ == '__main__':
    spider = NuoMiSpider()
    spider.run()
