import datetime

from django.shortcuts import render, render_to_response
from django.http import Http404
# Create your views here.

import re

from .models import Cover, CinemaUrl, Movie
from movie.movie_tickets.spiders.my_nuomi import NuoMi
from movie.movie_tickets.spiders.my_time import Time
from movie.movie_tickets.spiders.my_meituan import MaoYan
from django.db.models import Q

from .utils import get_all_cinemas


# 首页
def index(request):
    # ~Q(rating=0)去掉得分是0的
    movies = Movie.objects.filter(is_in_theater=True).filter(is_top=False).filter(~Q(rating=0)).order_by('-created_time')[:10]    # 除了top的所有正自上映的电影
    # top_movie = Movie.objects.get(is_top=True)
    top_movie = Movie.objects.filter(~Q(rating=0)).order_by('-created_time')[0]
    cover = Cover.objects.get(is_alive=True)
    context = {
        'movies': movies,
        'top': top_movie,
        'cover': cover,
    }

    return render(request, 'movie/index.html', context)


# 某一电影详情页面
def movie(request, movie_id):

    m = Movie.objects.get(pk=movie_id)
    # 查询 ID 返回地址
    content = {
        'item': m
    }
    return render(request, 'movie/display.html', content)


# 根据页面返回的地区，获取该地区所有的电影院
# ajax 请求
def cinema(request):

    if request.is_ajax():
        # print(request.POST)
        city = request.POST.get('city', None)
        district = request.POST.get('district', None).replace('区', '').replace('县', '').replace('市', '')

        if not city and not district:
            return Http404('not enough parameters')
        query = CinemaUrl.objects.filter(city__contains=city).filter(district__contains=district)    # 获取CinemaUrl对象

        content = {
            'cinemas': query
        }
        return render_to_response('movie/cinema.html', content)


# 根据页面返回的地区，获取该地区附近的电影院
# ajax 请求
def search(request):

    if request.is_ajax():
        print(request.POST)
        city = request.POST.get('city', None).replace('市', '')
        district = request.POST.get('district', None).replace('区', '').replace('县', '').replace('市', '')
        location = request.POST.get('location', None)
        if not city and not district and not location:
            return Http404('not enough parameters')

        nearby_cinemas = get_all_cinemas(city=city, district=district, location=location)    # 在输入地址附近的电影院
        query = []
        for cinema_pk, distance in nearby_cinemas:
            cinema_url_obj = CinemaUrl.objects.get(pk=cinema_pk)
            query.append(cinema_url_obj)
        # query = CinemaUrl.objects.filter(city__contains=city).filter(district__contains=district)    # 获取CinemaUrl对象
        
        content = {
            'cinemas': query
        }
        return render_to_response('movie/cinema.html', content)


# 根据页面返回的电影院索引值，获取票价
# ajax　请求
def tickets(request):

    if request.is_ajax():
        # 给淘票票的时间参数直接为 str_date
        str_date = request.POST.get('date')    # 2019-07-08
        if not str_date:
            return Http404('need parameter "date"')
        # 给时光网的时间参数
        date_ = datetime.datetime.strptime(str_date, "%Y-%m-%d").date()
        # 给糯米的时间参数
        delta = (date_ - datetime.date.today()).days

        time_date = ''.join(str_date.split('-'))    # 20190708
        pk = request.POST.get('pk')    # 电影院的id
        film = request.POST.get('film')    # 电影名字
        if not pk and not film:
            return Http404('lack of parameters "pk" or "film" or both')
        else:
            print(f"电影院id:{pk},电影名称:{film}, 观影日期:{time_date}")

        res_data = []
        cine = CinemaUrl.objects.get(pk=pk)    # 获取电影院对象
        # 糯米网 url
        url = cine.nuomi_url    # 糯米电影院主页
        cinemaId = re.search("cinemaId=(.*?)$", url).groups()[0]

        if url:
            print(f"百度糯米链接{url}")
            dct = {}
            nm = NuoMi()
            # print(str_date, delta, "糯米电影日期")
            """
            将网页版的链接变成手机端的链接
            """
            url = f"https://mdianying.baidu.com/cinema/detail?cinemaId={cinemaId}&sfrom=wise_shoubai&from=webapp&sub_channel=wise_shoubai_movieScheduleWeb&source=&c=179&cc=179&kehuduan="

            res = nm.get_timetable_from_nuomi(date_mark=delta, cinema_url=url, movie_name=film)    # delta表示和今天的时间差 0表示今天
            dct['website'] = '糯米'
            if res:
                dct['timetable'] = res
                dct['url'] = cine.nuomi_url
                res_data.append(dct)

        # 时光网
        time_url = cine.time_url
        if time_url:
            print(f"时光网链接{time_url}")
            dct = {}
            ti = Time()
            res = ti.get_timetable_from_time(cinema_url=time_url, movie_name=film, date_mark=delta)
            dct['website'] = '时光'
            if res:
                # print("时光", res)
                dct['timetable'] = res
                dct['url'] = cine.time_url
                res_data.append(dct)

        # 猫眼网
        meituan_url = cine.meituan_url
        if meituan_url:
            print(f"猫眼网链接{meituan_url}")
            dct = {}
            ti = MaoYan()
            res = ti.get_timetable_from_maoyan(cinema_url=meituan_url, movie_name=film, date_mark=delta)
            dct['website'] = '猫眼'
            if res:
                dct['timetable'] = res
                dct['url'] = cine.meituan_url
                res_data.append(dct)

        # # 淘票票未制作完成
        # tpp = cine.taopp_url
        # print("淘票票影院链接:", tpp)
        # if tpp:
        #     dct = {}
        #     taopp = TaoPiaoPiao()
        #     res = taopp.get_timetable_from_taopp(tpp, film, str_date)
        #     dct['website'] = '淘票票'
        #     if res:
        #         dct['timetable'] = res
        #         dct['url'] = cine.taopp_url
        #         res_data.append(dct)
        #

        content = {
            'data': res_data
        }

        return render_to_response('movie/timetable.html', content)
