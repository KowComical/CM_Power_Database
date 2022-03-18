#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/13 13:47
# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : Europe_ENTSOE.py
# @Software: PyCharm

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

sourcePath = 'K:\\Github\\GlobalPowerUpdate-Kow\\数据库\\code\\Europe\\' #国家参数存放的地方
dataPath = 'K:\\Github\\GlobalPowerUpdate-Kow\\数据库\\data\\europe\\eu27_uk\\craw\\entsoe' #数据将要保存的地方

endYear = datetime.utcnow().year #数据截至年


def main():
    session = login()
    downloadOriginalData(session)

def login(u='https://transparency.entsoe.eu/sso/login'):
    s = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.125 "
                      "Safari/537.36 Edg/84.0.522.61",
    }
    res = requests.get(u, headers=headers)
    soup = BeautifulSoup(res.text)
    url = soup.find('form')['action']

    # Obtain Cookies
    headers["Cookie"] = res.headers['Set-Cookie']
    postData = {
        'username': 'zhudeng94@gmail.com',
        'password': 'CarbonMonitor_2020',
        'credentialId': '',
    }
    s.headers.update(headers)
    res = s.post(url, data=postData)
    return s

def downloadOriginalData(s):
    area = pd.read_csv(os.path.join(sourcePath, 'entsoe_areaCode.csv'))
    """
    Skip inactive data
    """
    area = area[area['hasData'].map(lambda x:x != 'inactive')]

    for i in tqdm(area.index):
        code = area['code'][i]
        name = area['countryName'][i]
        codeType = 'CTY'
        cnyPath = os.path.join(dataPath, name)
        if not os.path.exists(cnyPath):
            os.mkdir(cnyPath)
                
        for year in range(2015, endYear + 1):
            u = 'https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType/export?' \
                'name=' \
                '&defaultValue=false' \
                '&viewType=TABLE' \
                '&areaType=' + codeType + \
                '&atch=false' \
                '&datepicker-day-offset-select-dv-date-from_input=D' \
                '&dateTime.dateTime=01.08.' + str(year) + '+00%3A00%7CUTC%7CDAYTIMERANGE' \
                '&dateTime.endDateTime=01.08.' + str(year) + '+00%3A00%7CUTC%7CDAYTIMERANGE' \
                '&area.values=' + code + \
                '&productionType.values=B01&productionType.values=B02&productionType.values=B03' \
                '&productionType.values=B04&productionType.values=B05&productionType.values=B06' \
                '&productionType.values=B07&productionType.values=B08&productionType.values=B09' \
                '&productionType.values=B10&productionType.values=B11&productionType.values=B12' \
                '&productionType.values=B13&productionType.values=B14&productionType.values=B20' \
                '&productionType.values=B15&productionType.values=B16&productionType.values=B17' \
                '&productionType.values=B18&productionType.values=B19' \
                '&dateTime.timezone=UTC' \
                '&dateTime.timezone_input=UTC' \
                '&dataItem=ALL' \
                '&timeRange=YEAR' \
                '&exportType=CSV'
            fileName = os.path.join(dataPath, name, "%s_ENTSOE_%s.csv" % (name, year))
            if os.path.exists(fileName) and (year < endYear):
                continue
            while True:
                try:
                    print('Starting download %s...' % fileName)
                    r = s.get(u)
                    break
                except:
                    s = login(u)
                    print('reconstruct session')
            f = open(fileName, 'wb')
            f.write(r.content)
            r.close()
            f.close()

if __name__ == '__main__':
    main()