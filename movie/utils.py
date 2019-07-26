#http://api.map.baidu.com/routematrix/v2/driving?  //GET请求
#https://api.map.baidu.com/routematrix/v2/driving?  //GET请求
#KHfXkZ5W9KOt6Xnyj6bkOTdnLdVHFWjb

# 徐政辉负责部分，计算两个地点之间的距离
import json
import urllib.parse
import urllib
import requests
import os
import django
import sys
from threading import Thread
import re

result = []    # 查询结果
dis_threshold = 5000    # 距离阈值 大于这个距离的都不要


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_tickets.settings")
django.setup()

from movie.models import CinemaUrl


def getDistance(start_location, end_location):
    start_lnglat = start_location[0].split(',')
    end_lnglat = end_location[0].split(',')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }
    main_url = 'https://www.amap.com/dir'
    res = requests.get(main_url, headers=headers)
    pattern = re.compile('<script src=".*?key=(.*?)"></script>')
    key = re.findall(pattern, res.text)[0]

    params = {
        'usepoiquery': 'true',
        'coor_need': 'true',
        'rendertemplate': '1',
        'invoker': 'plan',
        'engine_version': '3',
        'start_types': '1',
        'end_types': '1',
        'viapoint_types': '1',
        'policy2': '1',
        'fromX': start_lnglat[0],
        'fromY': start_lnglat[1],
        'start_poiid': start_location[1],
        'start_poitype': start_location[2],
        'start_poiname': start_location[3],
        'toX': end_lnglat[0],
        'toY': end_lnglat[1],
        'end_poiid': end_location[1],
        'end_poitype': end_location[2],
        'end_poiname': end_location[3],
        'key': key,
        'callback': 'jsonp_990327_'
    }
    url = 'https://www.amap.com/service/autoNavigat?'
    res = requests.get(url, params=params)
    dic = json.loads(
        res.text.replace("/**/ typeof jsonp_990327_ === 'function' && jsonp_990327_(", "").replace(");", ""))

    return dic['data']['distance'].split(',')[0]


def get_location(location):
    wd = {
        'words': location
    }
    url = 'https://www.amap.com/service/poiTipslite?&city=330100&type=dir&' + urllib.parse.urlencode(wd)
    # print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    dic = json.loads(response.text)
    # print(dic)
    return [dic['data']['tip_list'][0]['tip']['lnglat'], dic['data']['tip_list'][0]['tip']['id'],
            dic['data']['tip_list'][0]['tip']['category'], dic['data']['tip_list'][0]['tip']['name']]


def calculate_distance(cinema_pk, ori="浙江理工大学", dis="杭州电子科技大学"):
    """

    :param cinema_pk: 电影院的pk
    :param ori: 起点
    :param dis: 终点
    :return:
    """
    global result
    try:
        start_location = get_location(ori)
        end_location = get_location(dis)
        distance = float(getDistance(start_location, end_location))
        print(ori, dis, start_location, end_location, distance)
        if distance < dis_threshold:
            result.append([cinema_pk, distance])    # 保存小于距离阈值的电影院pk和距离
    except Exception as e:
        print(ori, dis, e)


def get_all_cinemas(city="杭州", district="江干", location="浙江财经大学"):
    global result
    result = []
    query = CinemaUrl.objects.filter(city__contains=city).filter(district__contains=district)  # 获取CinemaUrl对象
    ths = []
    for cinema in query:
        original_cinema_location = cinema.location

        new_cinema_location = clean_location(original_cinema_location)
        print(original_cinema_location, new_cinema_location)
        thread = Thread(target=calculate_distance, args=(cinema.pk, new_cinema_location, location, ))
        thread.start()
        ths.append(thread)
    for th in ths:
        th.join()

    print(result)
    return result

        # print(cinema_location)
        # calculate_distance(dis=cinema_location)


# 对地址进行清洗
def clean_location(location):
    """

    :param location:
    :return:
    """
    indexes = []    # 分隔符的索引
    if "路" in location:
        indexes.append(location.index("路"))

    if "街" in location:
        indexes.append(location.index("街"))

    if "广场" in location:
        indexes.append(location.index("广场")+1)

    if indexes:
        return location[:min(indexes)+1]
    else:
        return location

    # return location


if __name__ == '__main__':
    get_all_cinemas()
    # calculate_distance()calculate_distance