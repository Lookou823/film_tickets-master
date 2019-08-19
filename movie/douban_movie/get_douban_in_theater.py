# 从 https://movie.douban.com 获取当前上映的电影

import os
import re
from django.conf import settings
import django
import sys
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from liuyongdi import getwordcloudImage
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_tickets.settings")
django.setup()

from movie.models import Movie


def custom_poster_path(movie_title):
    root_dir = 'poster/'
    filename = re.sub('[\/:*?"<>|]', '', movie_title) + '.jpg'
    abs_path = os.path.join(settings.MEDIA_ROOT, os.path.join(root_dir, filename))
    rel_path = os.path.join(root_dir, filename)
    return abs_path, rel_path


def custom_trailer_path(movie_title):
    root_dir = 'trailer/'
    filename = re.sub('[\/:*?"<>|]', '', movie_title) + '.mp4'
    abs_path = os.path.join(settings.MEDIA_ROOT, os.path.join(root_dir, filename))
    rel_path = os.path.join(root_dir, filename)
    print(abs_path, rel_path)
    return abs_path, rel_path


def custom_wordcloud_path(movie_title):
    root_dir = 'wordcloud/'
    filename = re.sub('[\/:*?"<>|]', '', movie_title) + '.jpg'
    abs_path = os.path.join(settings.MEDIA_ROOT, os.path.join(root_dir, filename))
    rel_path = os.path.join(root_dir, filename)
    print(abs_path, rel_path)
    return abs_path, rel_path


class DouBanMovie:

    def __init__(self):
        self.url = "https://movie.douban.com/cinema/nowplaying/hangzhou/"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                        }

    def get_movies(self):
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        movie_urls = [tag["href"] for tag in
                      soup.find_all("a", attrs={"class": "ticket-btn", "data-psource": "poster"})]
        return movie_urls

    # 解析一个电影的详情页面
    def parse_movie(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        release_date = soup.find("span", property="v:initialReleaseDate").string
        # 上映时间还没到
        if datetime.datetime.now().strftime('%Y-%m-%d') < release_date[:10]:
            return
        
        name = soup.find("span", property="v:itemreviewed").string    # 电影名
        directors = [tag.string for tag in soup.find_all("a", rel="v:directedBy")]
        casts = [tag.string for tag in soup.find_all("a", rel="v:starring")][:5]
        rating = soup.find("strong", class_="ll rating_num").string or 0  # 评分
        poster_url = soup.find("img", title="点击看更多海报")["src"]
        genre = [tag.string for tag in soup.find_all("span", property="v:genre")]  # 类型
        trailer_url = soup.find("a", class_="related-pic-video")["href"]    # 预告片主页
        trailer_video_url = self.parse_trailer_url(trailer_url)    # 预告片视频链接

        # print(f'网址:{url}, 电影名:{name}, 导演:{directors}, 演员:{casts}, 评分:{rating}, 海报:{poster_url}, 类型:{genre}, '
        #       f'预告片链接:{trailer_video_url}')

        movie, created = Movie.objects.get_or_create(name=name,
                                                     defaults={"rating": rating,
                                                               "directors": '|'.join(directors),
                                                               "casts": '|'.join(casts),
                                                               "genes": '|'.join(genre)})
        abs_path, rel_path = custom_poster_path(name)    # 保存海报的路径
        abs_video_path, rel_video_path = custom_trailer_path(name)    # 保存预告片的地址
        abs_wordcloud_path, rel_wordcloud_path = custom_wordcloud_path(name)    # 保存词云图片的路径
        # 如果图片还没下载
        if not os.path.exists(abs_path):
            urlretrieve(poster_url, abs_path)

        # 如果视频还没下载
        if not os.path.exists(abs_video_path):
            print(f"开始下载:{trailer_video_url}")
            while True:
                try:
                    response = requests.get(trailer_video_url, stream=True)
                    with open(abs_video_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)
                    print(f"{name}视频下载完成")
                    break
                except Exception as e:
                    print(f"{name}下载出错", e)

        # 保存词云
        try:
            if not os.path.exists(abs_wordcloud_path):
                wordcloud_img = getwordcloudImage(name)
                wordcloud_img.savefig(abs_wordcloud_path, dpi=300, bbox_inches='tight')
        except Exception as e:
            print(e, "%s的词云制作出错" % name)
        # 保存信息
        movie.poster = rel_path    # 一定要用相对地址
        movie.trailer = rel_video_path  # 保存视频地址
        movie.WordCloud = rel_wordcloud_path    # 词云图片的地址
        movie.save()
        print(movie, created)

    def parse_trailer_url(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")
        src = soup.find("source")["src"]
        return src


if __name__ == '__main__':

    dbSpider = DouBanMovie()
    now_playing_urls = dbSpider.get_movies()
    for url in now_playing_urls:
        dbSpider.parse_movie(url)
