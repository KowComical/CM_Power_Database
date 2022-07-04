import time
import re
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
import pyautogui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af


def main():
    japan_selenium()


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
