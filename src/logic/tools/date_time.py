# -*- coding:utf-8 -*-

import re
import requests
import datetime
from bs4 import BeautifulSoup


def GetNetTime():
    try:
        head = {'User-Agent': 'Mozilla/5.0'}
        rep = requests.get(r'http://time1909.beijing-time.org/time.asp', headers = head)
        if 200 == rep.status_code:
            rep.encoding = "UTF-8"
        
            time_arr = re.split('[];=]',rep.text.replace("\r\n", ""))

            print("net time")
            return datetime.datetime(int(time_arr[3]), int(time_arr[5]), int(time_arr[7])
                , int(time_arr[9]), int(time_arr[11]), int(time_arr[13]))
        else:
            return datetime.datetime.now()
    except Exception as err:
        print(err.__str__())
        return datetime.datetime.now()

