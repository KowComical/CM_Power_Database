#!/usr/bin/python3
# -*- coding: utf-8 -*-

# 数据及10公司爬虫代码源：Zhu Deng

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import logging

logging.getLogger('WDM').setLevel(logging.NOTSET)  # 关闭运行chrome时的打印内容

import re
import urllib.request
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import pyautogui
import numpy as np
import pandas as pd
import os
import sys

sys.dont_write_bytecode = True

sys.path.append('./code/')
from global_code import global_function as af
from global_code import global_all as g


def main():
    # 爬取月度日本发电能源数据
    japan_selenium()
    # 10公司爬虫
    okiden()
    hepco()
    tohoku()
    tepco()
    chuden()
    rikuden()
    kansai()
    energia()
    yonden()
    kyuden()
    # 数据预处理
    craw_to_raw()
    # 整理数据
    g.japan()
    # 提取最新日期
    af.updated_date('Japan')


def craw_to_raw():
    # 当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')
    # 汇总craw数据
    file_path = './data/asia/japan/'
    file_name = af.search_file(file_path)
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('company') != -1]

    df_data = pd.DataFrame()
    name = re.compile(r'company/(?P<name>.*?).csv', re.S)
    for f in file_name:
        df_temp = pd.read_csv(f)
        if '当日実績(万kW)' in df_temp.columns:
            df_temp = df_temp.rename(columns={'当日実績(万kW)': name.findall(f)[0]})
        else:
            df_temp = df_temp.rename(columns={'実績(万kW)': name.findall(f)[0]})
        df_temp['datetime'] = df_temp['DATE'].astype(str) + ' ' + df_temp['TIME'].astype(str)
        df_temp['datetime'] = pd.to_datetime(df_temp['datetime'])
        df_temp = df_temp[['datetime', name.findall(f)[0]]]
        if df_data.empty:
            df_data = pd.concat([df_data, df_temp]).reset_index(drop=True)
        else:
            df_data = pd.merge(df_data, df_temp, how='outer')
    df_data = df_data.sort_values('datetime').replace(0, np.nan)
    # 用线性填充同一天某些公司还未更新的值
    df_data = df_data.set_index('datetime').interpolate('linear', limit_direction='both').reset_index()

    df_data = df_data.set_index(['datetime']).stack().reset_index().rename(columns={'level_1': 'company', 0: 'mwh'})
    df_data = df_data.groupby(['datetime']).sum().reset_index()
    df_data['mwh'] = df_data['mwh'] / 100  # 单位统一为Mwh
    df_data['datetime'] = pd.to_datetime(df_data['datetime'])
    df_data = df_data[df_data['datetime'] < current_date].reset_index(drop=True)
    df_data.to_csv(os.path.join(file_path, 'raw', '%s.csv' % 'craw_data'), index=False, encoding='utf_8_sig')


def okiden():
    # 0_okiden
    u = 'http://www.okiden.co.jp/denki2/juyo_10_%s.csv'
    directory = '0_okiden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date='20190101')
    af.japan_extractData(in_path, out_path, name, directory, date='20190831', ty='None', first=13, second=7)


def hepco():
    # 1_hepco
    u = 'http://denkiyoho.hepco.co.jp/area/data/zip/%s_hokkaido_denkiyohou.zip'
    directory = '1_hepco'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/.*?_.*?_(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Zipformat(u, in_path, name, start_date='20190101', freq='3MS')
    af.japan_extractData(in_path, out_path, name, directory, date='20190922', ty=None, first=13, second=7)


def tohoku():
    # 2_tohokuepco
    u = 'https://setsuden.nw.tohoku-epco.co.jp/common/demand/juyo_%s_tohoku.csv'
    directory = '2_tohokuepco'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date=2019)
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez', first=None, second=None)


def tepco():
    # 3_hepco
    u = 'https://www.tepco.co.jp/forecast/html/images/juyo-%s.csv'
    directory = '3_tepco'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date=2019)
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez', first=None, second=None)


def chuden():
    # 4_chuden
    u = 'https://powergrid.chuden.co.jp/denki_yoho_content_data/download_csv/%s_power_usage.zip'
    directory = '4_chuden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/.*?/(?P<name>.*?)_' % directory, re.S)
    # Download and extract all data
    af.japan_download_Zipformat(u, in_path, name, start_date='20190401', freq='MS')
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='so_ez', first=None, second=None)


def rikuden():
    # 5_rikuden
    u = 'http://www.rikuden.co.jp/nw/denki-yoho/csv/juyo_05_%s.csv'
    directory = '5_rikuden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date='20190101')
    af.japan_extractData(in_path, out_path, name, directory, date='20190929', ty='None', first=13, second=7)


def kansai():
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    # 6_kansai
    u = 'https://www.kansai-td.co.jp/yamasou/%s_jisseki.zip'
    directory = '6_kansai'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?)_' % directory, re.S)
    # Download and extract all data
    af.japan_download_Zipformat(u, in_path, name, start_date='20190101', freq='MS')
    af.japan_extractData(in_path, out_path, name, directory, date='20190911', ty=None, first=16, second=10)


def energia():
    # 7_energia
    u = 'https://www.energia.co.jp/nw/jukyuu/sys/juyo-%s.csv'
    directory = '7_energia'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date=2018)
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez', first=None, second=None)


def yonden():
    # 8_yonden
    u = 'https://www.yonden.co.jp/nw/denkiyoho/csv/juyo_shikoku_%s.csv'
    directory = '8_yonden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date=2019)
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez', first=None, second=None)


def kyuden():
    # 9_kyuden
    u = 'https://www.kyuden.co.jp/td_power_usages/csv/juyo-hourly-%s.csv'
    directory = '9_kyuden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date='20190101')
    af.japan_extractData(in_path, out_path, name, directory, date='20190904', ty='None', first=13, second=7)


def japan_selenium():
    out_path = './data/asia/japan/raw/month/'

    # 判断是否更新了新的文件需要下载
    file_name = af.search_file(out_path)

    date_name = re.compile(r'month/(?P<name>.*?)_', re.S)  # 从路径找出日期
    date = [date_name.findall(f)[0] for f in file_name]
    date = max(date)
    max_date = '%s年%s月' % (date[:4], int(date[-2:]))
    # 设置下个月的文件名
    next_date = (pd.to_datetime(date, format='%Y%m') + relativedelta(months=1)).strftime('%Y%m')

    # 开始模拟
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # 打开浏览器
    wd.get('https://occtonet3.occto.or.jp/public/dfw/RP11/OCCTO/SD/LOGIN_login#')  # 打开要爬的网址
    # 不知道为啥每次都会自动弹出另外一个不需要的窗口 所以先把不需要的关掉
    # noinspection PyBroadException
    try:
        handles = wd.window_handles
        wd.switch_to.window(handles[1])
        wd.close()  # 转到不需要的窗口并关闭
        wd.switch_to.window(handles[0])  # 切回原来的窗口
    except:
        pass
    wd.implicitly_wait(60)
    wd.find_element(By.ID, 'menu1-6').click()
    wd.find_element(By.ID, 'menu1-6-3-1').click()
    handles = wd.window_handles
    wd.switch_to.window(handles[1])  # 切到需要的窗口

    select = Select(wd.find_element(By.ID, 'ktgr'))
    select.select_by_value('7')  # 从下拉菜单里选取需要的数据内容
    wd.find_element(By.ID, 'searchBtn').click()

    # 如果要下载的月份文件已经存在了 则pass
    test = wd.find_element(By.ID, 'table3_rows_0__infNm')  # 这里之后可能需要修改
    if max_date in test.text:
        print('还未更新')
    else:
        wd.find_element(By.ID, 'table3_rows_0__pdfCsvBtn').click()
        time.sleep(5)
        # 找到确认下载并点击确认
        # confirm_text = 'ui-button-text'
        # wd.find_elements(By.CLASS_NAME, confirm_text)[2].click()
        wd.find_elements(By.XPATH, "//*[contains(text(), 'OK')]")[0].click()
        print('start download...')
        time.sleep(5)
        # 另存为地址及命名
        pyautogui.write('Japan_%s.csv' % next_date)  # 输入文件 # 不想再测试了 但目测这一步未成功 文件名并未改动
        time.sleep(1)
        pyautogui.press('enter')  # 点击确定
        time.sleep(10)
        # 找到存着的文件在哪里
        file_name = af.search_file('C:\\')
        file_name = [file_name[i] for i, x in enumerate(file_name) if x.find(next_date) != -1]
        if file_name:
            file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('csv') != -1][0]
        df = pd.read_csv(file_name, encoding='shift-jis')
        df.to_csv(os.path.join(out_path, '%s_10エリア計.csv' % next_date), encoding='shift-jis', index=False)
        print('finished')


if __name__ == '__main__':
    main()
