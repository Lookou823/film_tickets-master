import re
import requests
import difflib
import datetime


class Time:

    @staticmethod
    def get_timetable_from_time(date_mark=0, cinema_url='', movie_name='蜘蛛侠英雄远征'):

        try:
            # ip = ''
            # ip = random.choice(getIPlist())
            # if ip == '':
            #     raise Exception('获取ip代理失败')

            # # print('choiced ip proxies:' + ip)
            stringid = re.compile('com/(.*?)/', re.S).findall(cinema_url)[0]
            index = cinema_url.rfind('/')
            cinemaid = cinema_url[index + 1:]
            date = (datetime.date.today() + datetime.timedelta(days=date_mark)).strftime("%Y%m%d")

            # print(stringid, cinemaid, date)
            data = {
                'Ajax_CallBack': 'true',
                'Ajax_CallBackType': 'Mtime.Cinema.Services',
                'Ajax_CallBackMethod': 'GetShowtimesJsonObjectByCinemaId',
                'Ajax_CrossDomain': '1',
                'Ajax_RequestUrl': 'http://theater.mtime.com/' + stringid + '/' + cinemaid + '/?d=' + date,
                't': '2019770234367486',
                'Ajax_CallBackArgument0': cinemaid,
                'Ajax_CallBackArgument1': date
            }
            baseurl = 'http://service.theater.mtime.com/Cinema.api?'
            res = requests.post(url=baseurl, params=data)
            if res.status_code != 200:
                raise Exception('第一次请求失败')
            # else:
                # print(res.url)

            # -----------------------------------------------------------------------当前电影院可放电影对应的id
            movList = []
            pattern2 = re.compile('movies.:.(.*?)...showtimes', re.S)

            movEasyinfo = pattern2.findall(res.text)
            if len(movEasyinfo) == 0:
                raise Exception('获取当前日期可放电影失败')

            pattern2 = re.compile('"movieId":(.*?),"movieTitleCn":"(.*?)".*?"year"')

            dictContent = pattern2.findall(movEasyinfo[0])
            if len(dictContent) == 0:
                raise Exception('获取当前日期可放电影失败2')

            for item in dictContent:
                movInfoDict = {
                    'id': '',
                    'title': '',
                }
                temp = movInfoDict
                temp['id'] = str(item[0])
                temp['title'] = str(item[1])
                movList.append(temp)

            # 用difflib确定我要哪个电影
            couter = 0
            maxsimi = 0
            remember = -1
            for item in movList:
                rate = difflib.SequenceMatcher(None, item['title'], movie_name).ratio()
                if rate > maxsimi:
                    maxsimi = rate
                    remember = couter
                # print(item)
                couter += 1
            if remember == -1:
                raise Exception('没有匹配到电影名')
            choiced = ''
            choiced = movList[remember]['title']  # 得到我这边的电影
            # print('输入的电影是' + choiced)

            if choiced == '':
                raise Exception('获取所搜电影名失败')

            # ---------------------------------------------------------------当前电影院可查询日期
            pattern = re.compile(',"dateUrl":"(.*?)"', re.S)
            avaliableTime = pattern.findall(res.text)
            # ****
            avaliableTimeList = []

            for item in avaliableTime:
                temp = item[len(item) - 8:len(item)]
                avaliableTimeList.append(temp)

            if len(avaliableTime) == 0:
                raise Exception('获取可查询日期失败')

            # for item in avaliableTimeList:
                # print(item)

            # -----------------------------------------------Detail Information in exact Date
            movieInformation = res.text
            timeList = []

            pattern2 = re.compile('"showtimes":\[(.*)\],"total', re.S)

            # # print('timeinfo')
            timeinfo = pattern2.findall(movieInformation)

            if len(timeinfo) == 0:
                raise Exception('获取时间信息失败')

            pattern2 = re.compile(
                '\{.*?"movieId":(.*?),.*?new Date\("(.*?)"\),.*?,"version":"(.*?)","language":"(.*?)",.*?"movieEndTime":"预计(.*?)散场",.*?,"hallName":"(.*?)",.*?"price":(.*?),.*?"mtimePrice":(.*?),.*?"seatUrl":(.*?),.*?\}',
                re.S)

            # print(timeinfo[0])

            timeDetail = pattern2.findall(timeinfo[0])

            if len(timeDetail) == 0:
                raise Exception('获取时间信息失败2')
            # movie id, start time,version,language ,end time , hall name, price ,mtime price, seaturl
            for item in timeDetail:
                if (item[8] != '"#"'):
                    timeDict = {
                        'name': '',
                        'start': '',
                        'end': '',
                        'price': '',
                        'seaturl': '',
                        'hallname': '',
                        'language': '',
                        'version': ''}
                    name = ''
                    id = item[0]
                    for item2 in movList:
                        if item2['id'] == id:
                            name = item2['title']
                    timeDict['name'] = name
                    timeDict['start'] = item[1][len(item[1]) - 8:]
                    timeDict['end'] = item[4]
                    timeDict['price'] = item[7]
                    timeDict['seaturl'] = item[8]
                    timeDict['hallname'] = item[5]
                    timeDict['version'] = item[2]
                    timeDict['language'] = item[3]
                    if timeDict['name'] == choiced:
                        timeList.append(timeDict)
            if len(timeList) == 0:
                raise Exception('获取具体信息失败')

            # for item in timeList:
                # print(item)
            # --------------------------------------------------------得到最后元组
            FinalList = []

            for i in range(len(timeList)):
                FinalList.append((timeList[i]['start'][:5], timeList[i]['end'],
                                  timeList[i]['language'] + timeList[i]['version'], timeList[i]['hallname'],
                                  timeList[i]['price']))

            if len(FinalList) == 0:
                raise Exception('获取最终列表失败')

            # for item in FinalList:
                # print(item)

            return FinalList
        # ---------------------------------------------------------------------

        except Exception as e:
            # print(e)
            return
# if __name__ == '__main__':

    # 测试
    # cinemaurl='http://theater.mtime.com/China_Zhejiang_Province_Hangzhou_Jiangganqu/6886'
    # Time().get_timetable_from_time(0, cinemaurl, '蜘蛛侠：英雄远征 Spider-Man: Far From Home')
