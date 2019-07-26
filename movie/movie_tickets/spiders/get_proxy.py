import requests
import re

def checkok(url, headers, ip):
    try:
        res = requests.get(url=url, headers=headers, proxies={'https:': 'https://' + ip}, timeout=1)
        if res.status_code == 200:
            return True
        else:
            return False
    except:
        return False


def getIPlist():
    url = 'http://www.15daili.com/apiProxy.ashx?un=13777893886&pw=5201314.&count=500'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    # # print(response.text)
    pattern = re.compile('(\d.*?:.*?)\r\n', re.S)
    ipresult = pattern.findall(response.text)

    success = 0
    fail = 0
    total = len(ipresult)

    baseurl = 'http://service.theater.mtime.com/Cinema.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Cinema.Services&Ajax_CallBackMethod=GetShowtimesJsonObjectByCinemaId&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Ftheater.mtime.com%2FChina_Beijing_Changping%2F12432%2F%3Fd%3D20190712&t=2019770234367486&Ajax_CallBackArgument0=12432&Ajax_CallBackArgument1=20190712'

    ipresult = ipresult[:10]
    oklist = []
    # # print('getting proxies...')
    for item in ipresult:
        # # print(item)
        if checkok(baseurl, headers, item) == True:
            success += 1
            # # print('success')
            oklist.append('https://' + item)
        else:
            fail += 1
            # # print('fail')
    # # print(oklist)
    # # print(success*1.0/50)
    return oklist