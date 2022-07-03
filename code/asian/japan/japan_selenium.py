from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import sys

sys.getdefaultencoding()
sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af
import time
import re
import os
import pandas as pd
from dateutil.relativedelta import relativedelta
import pyautogui

import logging

logging.getLogger('WDM').setLevel(logging.NOTSET)  # 关闭运行chrome时的打印内容


def main():
    japan_selenium()


def japan_selenium():
    out_path = './data/asia/japan/raw/month/'
    windows_path = af.create_folder('C:/', 'kow')

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
    test = wd.find_element(By.ID, 'table3_rows_0__infNm')
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
        pyautogui.write('C:\kow\Japan.csv')  # 输入文件
        time.sleep(1)
        pyautogui.press('enter')  # 点击确定
        time.sleep(10)

        df = pd.read_csv(os.path.join(windows_path, 'Japan.csv'), encoding='shift-jis')
        df.to_csv(os.path.join(out_path, 'Japan_202204.csv'), encoding='shift-jis')

        # 找到下载的文件 # 目前问题是找不到 是否是因为action里面无法下载文件？
        # file = af.search_file(download_path)
        # file = [file[i] for i, x in enumerate(file) if x.find(next_date) != -1]
        # file = [file[i] for i, x in enumerate(file) if x.find('csv') != -1][0]
        # for filename in os.listdir(download_path):
        #     if filename.startswith(next_date):
        #         try:
        #             print('1')
        #             df = pd.read_csv(os.path.join(download_path, '%s.csv' % next_date), encoding='shift-jis')
        #             df.to_csv(os.path.join(out_path, '%s.csv' % next_date), encoding='shift-jis')
        #         except:
        #             try:
        #                 print('2')
        #                 os.rename(os.path.join(download_path, filename),
        #                           os.path.join(download_path, '%s.csv' % next_date))
        #                 df = pd.read_csv(os.path.join(download_path, '%s.csv' % next_date), encoding='shift-jis')
        #                 df.to_csv(os.path.join(out_path, '%s.csv' % next_date), encoding='shift-jis')
        #             except:
        #                 print('3')
        #                 filename = filename.encode('utf-8').decode(locale.getpreferredencoding(False))
        #                 os.rename(os.path.join(download_path, filename),
        #                           os.path.join(download_path, '%s.csv' % next_date))
        #                 df = pd.read_csv(os.path.join(download_path, '%s.csv' % next_date), encoding='shift-jis')
        #                 df.to_csv(os.path.join(out_path, '%s.csv' % next_date), encoding='shift-jis')

        # path = 'C:\202204_10.csv'
        # file = file.encode('utf-8').decode(locale.getpreferredencoding(False))
        # # 不知道为什么 能找到文件路径 但是read时说找不到 离谱
        # # name = re.compile(r'C:\\(?P<name>.*?).csv', re.S)  # 从路径找出日期
        # # file = name.findall(file)[0]+'.csv'
        # # path = pathlib.Path(download_path, file)
        wd.quit()


if __name__ == '__main__':
    main()
