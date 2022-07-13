# 数据来源 Taochun Sun
import time
import re
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys

sys.dont_write_bytecode = True
sys.path.append('K:\\Github\\CM_Power_Database\\code\\')
from global_code import global_function as af

# 路径
file_path = 'K:\\Github\\CM_Power_Database\\data\\africa\\nigeria\\craw\\'
# 设置备注
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('--headless')
options.add_argument('--disable-gpu')
# 打开网页
wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # 打开浏览器
wd.get('https://www.niggrid.org/GenerationProfile')  # 打开要爬的网址
wd.implicitly_wait(60)
time.sleep(1)

date_range = pd.read_csv(file_path + 'date_range.csv')
# 将数字变为小时格式
hour_range = date_range['hour'].str.split(':', expand=True).rename(columns={0: 'first_hour', 1: 'second_hour'})
hour_range['first_hour'] = hour_range['first_hour'].str.zfill(2)

hour_range['hour'] = hour_range['first_hour'] + ':' + hour_range['second_hour']
date_range['hour'] = hour_range['hour']

date_range['day'] = date_range['day'].astype(str)
date_range['hour'] = date_range['hour'].astype(str)
date_range['year'] = date_range['year'].astype(str)
date_range['month'] = date_range['month'].astype(str)

file_name = af.search_file(file_path)
file_name = [file_name[i] for i, x in enumerate(file_name) if not x.find('date_range') != -1]

exsiting_year = re.compile(r'craw\\(?P<name>.*?)-', re.S)
exsiting_month = re.compile(r'craw\\.*?-(?P<name>.*?)-', re.S)
exsiting_day = re.compile(r'craw\\.*?-.*?-(?P<name>.*?)_', re.S)
exsiting_first_hour = re.compile(r'craw\\.*?_(?P<name>.*?)_', re.S)
exsiting_second_hour = re.compile(r'craw\\.*?_.*?_(?P<name>.*?).csv', re.S)

# 去掉已下载的
for f in file_name:
    year = exsiting_year.findall(f)[0]
    month = exsiting_month.findall(f)[0]
    day = exsiting_day.findall(f)[0]
    hour = exsiting_first_hour.findall(f)[0] + ':' + exsiting_second_hour.findall(f)[0]
    date_range = date_range[~(
            (date_range['year'] == year) & (date_range['month'] == month) & (date_range['day'] == day) & (
            date_range['hour'] == hour))].reset_index(drop=True)
date_range = date_range[8000:]  # 分批次下载

year_list = date_range['year'].tolist()
month_list = date_range['month'].tolist()
day_list = date_range['day'].astype(int).tolist()
hour_list = date_range['hour'].tolist()

# 开始爬取
for y, m, d, h in zip(year_list, month_list, day_list, hour_list):
    df = pd.DataFrame()
    wd.find_element(By.XPATH, "//*[@name='ctl00$MainContent$txtReadingDate']").click()  # 点击选日期
    time.sleep(1)
    wd.find_element(By.XPATH, "//*[@value=%s]" % y).click()  # 点击选年份
    time.sleep(1)
    try:
        wd.find_elements(By.XPATH, "//*[contains(text(), '%s')]" % m)[0].click()  # 点击选月份
    except Exception as e:
        print(e)
        wd.find_element(By.XPATH, "//*[@name='ctl00$MainContent$txtReadingDate']").click()  # 点击选日期
        time.sleep(1)
        wd.find_element(By.XPATH, "//*[@value=%s]" % y).click()  # 点击选年份
        time.sleep(1)
        wd.find_elements(By.XPATH, "//*[contains(text(), %s)]" % m)[0].click()  # 点击选月份
    time.sleep(1)
    wd.find_element(By.LINK_TEXT, str(d)).click()  # 点击选日子
    time.sleep(1)
    wd.find_element(By.XPATH, "//*[@value='%s']" % h).click()  # 选择小时
    time.sleep(1)
    wd.find_element(By.XPATH, "//*[@name='ctl00$MainContent$btnGetReadings']").click()  # 点击确定
    time.sleep(1)
    # 提取数据
    html = wd.page_source  # 获取网页源代码
    # 如果有数据
    if html.find('No Readings for that Day') == -1:
        df = pd.read_html(wd.page_source)[0][:-1].drop(columns=['#']).rename(
            columns={'Company': 'sector', 'MW': 'num', 'Units': 'unit'})
        # 添加日期
        df['year'] = y
        df['month'] = m
        df['day'] = d
        df['hour'] = h
        df.to_csv(os.path.join(file_path, '%s-%s-%s_%s_%s.csv' % (y, m, d, h[:-3], h[-2:])), index=False,
                  encoding='utf_8_sig')
        time.sleep(1)
    else:
        print('%s-%s-%s %s 无数据' % (y, m, d, h))
        empty = pd.DataFrame()
        empty.to_csv(os.path.join(file_path, '%s-%s-%s_%s_%s.csv' % (y, m, d, h[:-3], h[-2:])), index=False,
                     encoding='utf_8_sig')
    wd.get('https://www.niggrid.org/GenerationProfile')  # 打开要爬的网址
