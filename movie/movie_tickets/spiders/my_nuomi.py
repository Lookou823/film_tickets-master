import requests
import difflib
from bs4 import BeautifulSoup


class NuoMi:

    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}

    def get_timetable_from_nuomi(self, date_mark=0, cinema_url="", movie_name="银河补习班"):
        """
        :param date_mark: 从今天开始第几天的电影信息, 今天的下标是0, 明天是1
        :param cinema_url: 电影院主页
        :param movie_name: 电影名字
        :return: 选中的那天的时间表
        """
        try:
            response = requests.get(cinema_url, headers=self.headers)
            # print(response.text)
            res = self.parse_tickets_html(response.text, movie_name)
            if not res:
                return
            return res[date_mark]

        except Exception as e:
            # print(e)
            return

    def parse_tickets_html(self, page, movie_name):
        """

        :param page:
        :param movie_name:
        :return: a list of [<td>开场时间</td>
            <td>结束时间</td>
            <td>语言</td>
            <td>厅位</td>
            <td>价格</td>]
        """
        soup = BeautifulSoup(page, 'lxml')
        soup_div = soup.find('div', class_="mod m-movie-infos")    # 包裹所有点电影
        soup_div_in = soup_div.find_all('div', attrs={'data-movie-id': True})
        movie_id = None
        for div in soup_div_in:
            # 当前待匹配的电影名字
            selected_movie_name = div.div.get_text().replace('\n', '')
            # 相似度
            similarity_ratio = difflib.SequenceMatcher(None, selected_movie_name, movie_name).quick_ratio()
            # print(f"{movie_name}和{selected_movie_name}的相似度:{similarity_ratio}")
            # 如果匹配上了
            if similarity_ratio > 0.2:
                movie_id = div['data-movie-id']    # 先根据电影名获取电影的id
                break

        # assert movie_id, '未找到此电影'
        if not movie_id:
            return
        # 查询电影信息
        soup_ul = soup.find_all('div', class_=True,
                                attrs={'data-movie-id': '{}'.format(movie_id),
                                       'data-log': True,
                                       'data-date': True,
                                       'data-choosetagmap': True})

        res = []
        daily_ = []
        cur_date = ''
        for i in soup_ul:
            # 哪一天
            i_date = i.get('data-date')
            # print(i_date)
            if cur_date != i_date:    # 新的一天
                res.append(daily_)
                daily_ = []
                cur_date = i_date
            start_time = i.find('div', class_="start").string
            end_time = i.find('div', class_="end").string.replace('散场', '')
            lan = i.find('div', class_="lan").string
            theater = i.find('div', class_="theater").string
            price = i.find('div', class_="price").get_text(';').strip()
            price = price.split(';')[2]
            daily_.append((start_time, end_time, lan, theater, price))

        res.append(daily_)
        return res


if __name__ == '__main__':
    NuoMi().get_timetable_from_nuomi()