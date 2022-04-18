#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/13 13:47
# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : Europe_ENTSOE.py
# @Software: PyCharm
import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import os
import datetime

in_path = '../../code/europe/eu27_uk/entsoe'  # 国家参数存放的地方
out_path = '../../data/europe/eu27_uk/craw/entsoe'  # 爬虫数据将要保存的地方
raw_path = '../../data/europe/eu27_uk/'  # raw数据保存的地方

endYear = datetime.datetime.utcnow().year  # 数据截至年
now = datetime.date.today().strftime("%Y-%m-%d")  # 获取当前年月日


def main():
    session = login()
    downloadOriginalData(session)
    pre()


def login(u='https://transparency.entsoe.eu/sso/login'):
    s = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.125 "
                      "Safari/537.36 Edg/84.0.522.61",
    }
    res = requests.get(u, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
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
    area = pd.read_csv(os.path.join(in_path, 'entsoe_areaCode.csv'))
    area = area[area['hasData'].map(lambda x: x != 'inactive')]

    for i in tqdm(area.index):
        code = area['code'][i]
        name = area['countryName'][i]
        codeType = 'CTY'
        cnyPath = os.path.join(out_path, name)
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
                                                          '&dateTime.endDateTime=01.08.' + str(
                year) + '+00%3A00%7CUTC%7CDAYTIMERANGE' \
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
            fileName = os.path.join(out_path, name, "%s_ENTSOE_%s.csv" % (name, year))
            if os.path.exists(fileName) and (year < endYear):
                continue
            while True:
                try:
                    print('Starting download %s_%s' % (name, year))
                    r = s.get(u)
                    break
                except:
                    s = login(u)
                    print('reconstruct session')
            f = open(fileName, 'wb')
            f.write(r.content)
            r.close()
            f.close()


def pre():
    area = pd.read_csv(os.path.join(in_path, 'entsoe_areaCode.csv'))
    area = area[area['hasData'].map(lambda x: x != 'inactive')]

    for i in tqdm(area.index):
        name = area['countryName'][i]
        timeDiff = area['timeDiff'][i]
        try:
            data_preprocess(raw_path, name, timeDiff)
        except:
            pass


def data_preprocess(dataPath, name, time_diff):
    country_data = pd.DataFrame()
    for year in range(2015, endYear + 1):
        tmp = pd.read_csv(os.path.join(dataPath, 'craw', 'entsoe', name, "%s_ENTSOE_%s.csv" % (name, year)))
        country_data = pd.concat([country_data, tmp])
    outfile = os.path.join(dataPath, 'raw', 'entsoe', "%s.csv" % name)

    # 数据预处理
    country_data['MTU'] = pd.to_datetime(country_data['MTU'].str[19:35], format='%d.%m.%Y %H:%M')
    # UTC时间转换为本地时间
    country_data['MTU'] = [(i + datetime.timedelta(hours=int(time_diff))) for i in country_data['MTU']]
    # country_data.set_index('MTU', drop=True, inplace=True)
    country_data = country_data.drop(columns=['Area']).set_index('MTU')

    # 删除所有列中包含'-'的行（'-'表示数据未发布）
    country_data = country_data.replace('-', np.nan).dropna(how='all')
    # 将'n/e'设置为空值
    country_data = country_data.replace('n/e', np.nan)

    country_data.to_csv(outfile)
    country_data = pd.read_csv(outfile, index_col=0)
    country_data.index = pd.to_datetime(country_data.index)

    # 中位差法去除异常值
    th = 3.5
    for col in country_data.columns[1:]:
        c = country_data[col]
        t = (c - c.median()).abs()
        c[0.75 * t / t.median() > th] = np.nan

    # 线性插值补全缺失值
    try:
        country_data.interpolate(method='linear', inplace=True)

        country_data = country_data.resample('1H').mean()
        country_data.to_csv(outfile, float_format="%.3f")
    except:
        pass


if __name__ == '__main__':
    main()
