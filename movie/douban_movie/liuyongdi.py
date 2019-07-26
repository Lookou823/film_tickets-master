# 留雍迪负责部分，爬取豆瓣电影评论并制作词云
import requests
import warnings
import random
from wordcloud import WordCloud
from urllib import request
warnings.filterwarnings("ignore")
import jieba  # 分词包
import numpy  # numpy计算包
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['figure.figsize'] = (4.0, 6.0)#图片大小


#随机获取user-agent
def randomGetAgent():
    userdictionaries = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36'
    ]
    user_agent = random.choice(userdictionaries)
    return user_agent




# 分析网页函数
def getNowPlayingMovie_list():
    requests.get('https://movie.douban.com', verify=False)

    url = 'https://movie.douban.com/nowplaying/hangzhou/'

    agentname = randomGetAgent()
    header = {'User-Agent': agentname,
              'Connection': 'close'}  # 随机获得user-agent
    req = request.Request(url,headers=header)
    resp = request.urlopen(req)
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, 'html.parser')                     #分析html
    nowplaying_movie = soup.find_all('div', id='nowplaying') #获得现在播放的电影的id
    nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_='list-item')
    nowplaying_list = []
    for item in nowplaying_movie_list:#将正在放映的电影进行列表的存储
        nowplaying_dict = {}
        nowplaying_dict['id'] = item['data-subject']
        for tag_img_item in item.find_all('img'):
            nowplaying_dict['name'] = tag_img_item['alt']
            nowplaying_list.append(nowplaying_dict)
    return nowplaying_list


# 爬取评论函数
def getCommentsById(movieId, pageNum):
    requests.get('https://movie.douban.com', verify=False)

    eachCommentList = [];
    if pageNum > 0:
        start = (pageNum - 1) * 20
    else:
        return False
    agentname = randomGetAgent()
    header = {'User-Agent': agentname,
              'Connection': 'close'}#随机获得user-agent
    requrl = 'https://movie.douban.com/subject/' + movieId + '/comments' + '?' + 'start=' + str(start) + '&limit=20'
    req = request.Request(requrl, headers=header)#分装url
    resp = request.urlopen(req)
    try:
        # print(resp.getcode())#判断请求有效
        html_data = resp.read().decode('utf-8')
        soup = bs(html_data, 'html.parser')
        comment_div_lits = soup.find_all('div', class_='comment')#有效获取comment
        # print(comment_div_lits)
        for item in comment_div_lits:
            comment_str = str(item.find_all('p')[0])
            comment_str = comment_str.replace('<span class="short">','')
            comment_str = comment_str.replace('</span>','')
            comment_str = comment_str.replace('<p class="">','')
            comment_str = comment_str.replace('</p>','')

            if comment_str is not None:
                eachCommentList.append(comment_str)#数据清理

        return eachCommentList
    except Exception as e:
        print(e)

def getwordcloudImage(name):
    # 循环获取第一个电影的前10页评论
    # 参数是电影名称
    commentList = []
    NowPlayingMovie_list = getNowPlayingMovie_list()
    # print("NowPlayingMovie_list's type:")#type is list
    # print(type(NowPlayingMovie_list))
    count = 0
    # name = re.(r'[a-zA-Z|')
    name = re.findall(r'[\u4e00-\u9fff|a-zA-Z]+', name)

    if name[0]:
        for temp in NowPlayingMovie_list:#在list中匹配相应的电影名字

            if name[0] in temp['name']:
                break
            count+=1


    try:
        for i in range(10):
            num = i + 1
            commentList_temp = getCommentsById(NowPlayingMovie_list[count]['id'], num)
            commentList.append(commentList_temp)
    except Exception as e:#防止评论不到十页而报错导致程序出错
        print(e)

    # 将列表中的数据转换为字符串
    comments = ''
    for k in range(len(commentList)):
        comments = comments + (str(commentList[k])).strip()
    # print(comments)#内容好像有问题待修改

    # 使用正则表达式去除标点符号
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filterdata = re.findall(pattern, comments)
    cleaned_comments = ''.join(filterdata)
    # print(cleaned_comments)
    # 使用结巴分词进行中文分词
    segment = jieba.lcut(cleaned_comments)
    # stopwords = {}.fromkeys([line.rstrip() for line in open('stopwords.txt')])
    words_df = pd.DataFrame({'segment': segment})

    # 去掉停用词
    stopwords = pd.read_csv("stopwords.txt", index_col=False, quoting=3, sep="\t", names=['stopword'],encoding='utf-8')  # quoting=3全不引用
    words_df = words_df[~words_df.segment.isin(stopwords.stopword)]
    # 统计词频
    words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数": numpy.size})
    words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)
    # print(words_stat)
    # 用词云进行显示

    wordcloud = WordCloud(scale=16,font_path="simhei.ttf", background_color="white", max_font_size=80)
    word_frequence = {x[0]: x[1] for x in words_stat.head(1000).values}

    word_frequence_list = []
    for key in word_frequence:
        temp = (key, word_frequence[key])
        word_frequence_list.append(temp)
        # print(temp)
        # print(type(temp))
    # word_frequence = {'罗梦': 125, '土话西施': 97, '史努比': 100, '贪吃鸠': 55, '白': 88, '可爱': 77, '省政府奖学金': 55, '魔鬼身材': 66,
    #                   '素质高': 55, '社会主义接班人': 56, '摄影大师': 65, '大奶': 55, '李霖烨老婆': 77, 'gorgeous': 60, 'beautiful': 66,
    #                   'pretty': 30, '温岭': 55, '横峰': 23, '仰天湖': 44, 'cute': 34, '善良': 11, '努力': 23,  '青春': 23, }
    wordcloud = wordcloud.fit_words(word_frequence)
    plt.imshow(wordcloud)
    name1 = 'picture/'
    name = NowPlayingMovie_list[count]['name']
    name+='.png'
    name1 += name
    # 路径就是picture/电影名称.png
    plt.axis('off')  # 关闭坐标轴

    # plt.savefig(name1, dpi=300, bbox_inches='tight')
    return plt
    # plt.show()

# 主函数
x = getwordcloudImage('蜘蛛侠？DFsdfsdfsdf|***dfw==1231--')

x.savefig('xxx.jpg', dpi=300, bbox_inches='tight')
