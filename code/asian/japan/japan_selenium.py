from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import sys
import re
import os
import pandas as pd
# from dateutil.relativedelta import relativedelta

sys.dont_write_bytecode = True

sys.path.append('./code/')
from global_code import global_function as af


def main():
    japan_selenium()


def japan_selenium():
    # 修改默认下载路径
    c_options = webdriver.ChromeOptions()
    out_path = './data/asia/japan/raw/month/'
    download_path = 'C:\\'
    download_path = af.create_folder(download_path, 'kow')
    prefs = {'download.default_directory': download_path}
    c_options.add_experimental_option('prefs', prefs)

    # 判断是否更新了新的文件需要下载
    file_name = af.search_file(out_path)

    name = re.compile(r'month/(?P<name>.*?)_', re.S)  # 从路径找出国家
    date = [name.findall(f)[0] for f in file_name]
    date = max(date)
    max_date = '%s年%s月' % (date[:4], int(date[-2:]))
    # 设置下个月的文件名
    # next_date = pd.to_datetime(date, format='%Y%m') + relativedelta(months=1)
    # next_date = next_date.strftime('%Y%m')

    # 开始模拟
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=c_options)  # 打开浏览器
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
        print('start download...')
        wd.find_element(By.ID, 'table3_rows_0__pdfCsvBtn').click()
        time.sleep(10)
        # 找到确认下载并点击确认
        confirm_text = 'ui-button-text'
        wd.find_elements(By.CLASS_NAME, confirm_text)[2].click()
        time.sleep(30)

        # 找到下载的文件
        csv_name = af.search_file(download_path)[0]
        csv_name = csv_name.decode('utf-8')
        df = pd.read_csv(os.path.join(download_path, '%s' % csv_name), encoding='shift-jis')
        df.to_csv(os.path.join(out_path, '%s' % csv_name), encoding='shift-jis')

    wd.quit()


if __name__ == '__main__':
    main()
