
from django.db import models
from django.core.files import File

class CinemaUrl(models.Model):

    # 城市名
    city = models.CharField('城市', max_length=50)
    # 区、县、等二级地址
    district = models.CharField('区/县', max_length=255)
    # 详细地址
    location = models.CharField('详细地址', max_length=255, default='')
    # 电影院名
    cinema_name = models.CharField('电影院名', max_length=255, default='')
    # 美团地址
    meituan_url = models.URLField('美团地址', default='')
    # 时光网地址
    time_url = models.URLField('时光地址', default='')
    # 淘票票地址
    taopp_url = models.URLField('淘票票地址', default='')
    # 糯米地址
    nuomi_url = models.URLField('糯米地址', default='')
    # 创建时间
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 是否有效
    is_active = models.BooleanField('是否有效', default=True)
    # 访问次数
    view_count = models.IntegerField('访问次数', default=0)
    # 索引码
    # code = models.IntegerField('索引码', default=0)

    def __str__(self):
        return f"{self.city} {self.district} {self.cinema_name} {self.location}"


class Movie(models.Model):

    name = models.CharField(verbose_name='电影名', max_length=255)
    rating = models.FloatField('评分', default=0)
    poster = models.ImageField('海报', upload_to='poster/')
    WordCloud = models.ImageField('词云图', upload_to='wordcloud/', null=True, blank=True)
    trailer = models.FileField('豆瓣预告片地址', upload_to='trailer/', null=True)
    # 由于可能有多名导演和演员，单个之间以 "|" 连接，以备后用
    directors = models.CharField('导演', max_length=255, default='')
    casts = models.CharField('演员', max_length=255, default='')
    genes = models.CharField('类型', max_length=255, default='')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    is_top = models.BooleanField('是否评分最高', default=False)
    is_in_theater = models.BooleanField('正在上映', default=True)

    def __str__(self):
        return self.name


class Cover(models.Model):

    name = models.CharField('封面名', max_length=100, default='cover')
    cover_img = models.ImageField('封面图片', upload_to='cover/', default='cover/default.jpg')
    is_alive = models.BooleanField('正在使用', default=False)












