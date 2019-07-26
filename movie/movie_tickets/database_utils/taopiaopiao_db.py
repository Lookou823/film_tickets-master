"""
将时光网的电影院导入数据库
"""

import django
import os
import sys
import time
import difflib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_tickets.settings")
django.setup()

from movie.models import CinemaUrl

count = 0
with open("taopiaopiao.txt", 'r', encoding='gbk') as f:
    for line in f:
        line = line.strip('\n')
        try:
            city, district, cinema_name, cinema_url = line.split(' ')

            city = city.replace('市', '')
            district = district.replace('市', '').replace('区', '').replace('县', '')
            # print(city, district, cinema_name, cinema_url)
            ratios = []
            cinema_list = list(CinemaUrl.objects.filter(city__contains=city).filter(district__contains=district))
            # print(cinema_list)
            for cinema in cinema_list:
                # print(cinema)
                similarity_ratio = difflib.SequenceMatcher(None, cinema.cinema_name, cinema_name).quick_ratio()
                ratios.append(similarity_ratio)
                # print(cinema.cinema_name, cinema_name, similarity_ratio)
            if ratios and np.max(ratios) > 0.65:
                selected_index = int(np.argmax(ratios))
                print("选中的下标是:", selected_index, ratios[selected_index], cinema_list[selected_index].cinema_name, cinema_name)
                cinema_list[selected_index].taopp_url = cinema_url
                cinema_list[selected_index].save()

        except Exception as e:
            print(e)
            # print(e)
            # with open("fail.txt", 'a') as fail_file:
            #     fail_file.write(line+'\n')
            # print(line, len(line.split(' ')), e)
    print(count)