## 基于django的电影票比价网
## 在crossin的编程教室的项目上进行了一些功能的扩充，原项目地址：https://github.com/zx576/film_tickets

#### 运行效果
![首页](https://github.com/zstu-lly/film_tickets-master/blob/master/images/IMG_5276.PNG)
![](https://github.com/zstu-lly/film_tickets-master/blob/master/images/IMG_5278.PNG)
![搜索附近电影院](https://github.com/zstu-lly/film_tickets-master/blob/master/images/IMG_5279.PNG)
![词云](https://github.com/zstu-lly/film_tickets-master/blob/master/images/IMG_5281.PNG)
![查票结果](https://github.com/zstu-lly/film_tickets-master/blob/master/images/IMG_5256.PNG)

#### 更新日志
- 增加了播放预告片功能
- 增加了搜索附近影院功能
- 增加了展示电影评论词云功能
- 重新实现了时光网、猫眼电影、百度糯米爬虫
- 淘票票电影暂未实现

#### 运行环境

- python 3+
- django 1.10
- linux/windows/mac

#### 如何使用
拉取项目到本地
`https://github.com/zstu-lly/movie-tickets-comparator.git`

进入项目文件夹

安装依赖库
`pip install -r requirements.txt`



创建超级用户

`python manage.py createsuperuser`

依次输入用户名和密码即可

`python manage.py runserver`

django 自检无误后，在浏览器输入

`127.0.0.1:8000/movie`

#### 文件说明

文件结构分为三大块

1. 文件夹 douban_movie 该部分爬取豆瓣电影正在上映的电影的海报、宣传片并制作电影评论词云
2. 文件夹 movie_tickets 该部分包含了几个电影票网站的电影院信息爬虫以及某电影院某电影排片信息爬虫
3. django 项目

##### douban_movie

get_douban_in_theater.py 

包含了以下作用：

- 爬取当日上映的电影
- 比对目前数据库的上映影片，更新数据库


##### movie_tickets
  
spiders/
  
    下面 3 个文件表示不同网站的爬虫
  
    
settings.py 一些基本的设置
show.py 命令行获取电影排片信息


#### 项目思路

1. 使用爬虫爬取各电影票网站所有的电影院链接
2. 使用豆瓣 API 获取当日上映的电影信息
3. django 显示电影信息，提供给用户选择电影院的接口
4. 将电影院信息发送到 django 后台进行查询，爬取对应的排片信息显示给用户


#### 一些技术细节

1、 ajax 加载

本项目使用到了比较多的 ajax 加载技术，给出前后端的一份代码

示例：
实现功能：选择区/县，发送到后台，提取出电影院

html 代码

```html
<!--...-->
<li><a href="javascript:void(0);" class="city_">闵行区</a></li>
<!--...-->
```

js 代码

```javascript

// 选择区/县，发送到后台，提取出电影院
$(document).ready(function () {
    $(document).on('click', '.city_', function(){
        // 获取发送到后端的信息
        // 城市名 区名
        var dis = this.text;
        var city = $('#choose-city a').text();
        // ajax post 请求
        $.post('/movie/cinema', {
            // 发送信息
            'city':city,
            'district': dis,
            csrfmiddlewaretoken: '{{ csrf_token }}'
        },function (data) {
            // 回调函数， 处理后端信息
            $('#movie-choose-x').html(data);
        })
    })
});
```
views.py

```python
from django.shortcuts import render_to_response
from .models import CinemaUrl

# 根据页面返回的地区，获取该地区所有的电影院
# ajax 请求
def cinema(request):

    if request.is_ajax():
        # 获取前端信息
        city = request.POST.get('city', None)
        district = request.POST.get('district')
        # 查询数据库
        query = CinemaUrl.objects.filter(city__contains=city).filter(district__startswith=district)
        # 包装数据
        content = {
            'cinemas': query
        }
        # 使用 render_to_response 函数处理模板数据并发送到前端
        return render_to_response('movie/cinema.html', content)

```

template/cinema.html

```djangotemplate

    <ul class="nav nav-pills">
        {% for cine in cinemas %}
        <li>
            <a href="javascript:void(0);" id="{{ cine.id }}" class="cinema">
                {{ cine.cinema_name }}  
            </a>
        </li>
        {% endfor %}

    </ul>

```

如此，就是一份完整的 django-js-html 协同完成 ajax 加载的代码。在页面触发点击事件，将必要的信息发送到后端查找，最后在页面显示查找结果。


2、使用 django 环境运行代码

在使用豆瓣 API 部分，获取数据后需通过 django models 对数据库进行更新。所以需要一个运行在一个独立的 django 环境中。
添加以下代码可以完成此功能：

```python

import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_tickets.settings")
django.setup()

# 这样可以正常的导入 .models 中的类的
from movie.models import Movie

# your code here
```

3、difflib


在初期的电影院信息的爬取过程中，各家的信息分别在数据库中不同的表内，接入到 django 后，产生了合并 表 的需求，但各家网站可能对于同一电影院显示的名称有细微差别。
所以使用了 difflib 自然语言处理库对电影院名甚至电影院地点进行比对，根据结果判断是否为同一家影院。

```

>>> import difflib
>>> difflib.SequenceMatcher(None, '下沙横店影城', '宝龙横店影城').quick_ratio()
0.6666666666666666
>>> difflib.SequenceMatcher(None, '时代影城', '保利江川影院').quick_ratio()
0.2
```
