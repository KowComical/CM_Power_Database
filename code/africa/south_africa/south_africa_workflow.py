from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import logging

logging.getLogger('WDM').setLevel(logging.NOTSET)  # 关闭运行chrome时的打印内容

import time
import pandas as pd
import re
import os

import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
import global_code.global_function as af
import global_code.global_all as g

out_path = './data/africa/south_africa/raw/'
out_file = os.path.join(out_path, 'raw.csv')


def main():
    # 爬虫+预处理数据
    craw()
    # 整理数据
    g.south_africa()
    # 提取最新日期
    af.updated_date('south_africa')


def craw():
    # chrome驱动路径
    url = 'https://www.eskom.co.za/dataportal/supply-side/station-build-up-for-yesterday/'
    # 开始模拟
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--remote-debugging-port=9222")  # 虽然不知道为什么 但是不加这条会报错
    chrome_options.add_argument("--no-sandbox")

    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wd.get(url)  # 打开要爬的网址
    wd.implicitly_wait(10)  # 每0.5秒进行一次操作 如果一直失败超过10秒则报错 以防万一用的 关键部分则还是用睡眠来操控
    time.sleep(15)
    html = wd.page_source  # 获取网页源代码

    # 获取新网址
    url_name = re.compile(r'<iframe loading="lazy" width="600" height="600" src="(?P<name>.*?)">', re.S)
    new_url = url_name.findall(html)[0]
    wd.quit()  # 将旧的网页关掉
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wd.get(new_url)  # 打开要爬的网址
    time.sleep(15)
    # 找到右键元素
    confirm_text = 'clearCatcher'
    ActionChains(wd).context_click(wd.find_elements(By.CLASS_NAME, confirm_text)[0]).perform()  # 右键
    # noinspection PyBroadException
    try:
        wd.find_element(By.XPATH, '//*[@title="以表的形式显示"]').click()  # 这个网站很奇怪 他会判断本地ip 然后根据ip生成相应语言的源代码
    except:
        wd.find_element(By.XPATH, '//*[@title="Show as a table"]').click()
    time.sleep(5)
    # 获取当前页面的源代码 所要数据就藏在里面
    html = wd.page_source

    # 获取列名
    col_list = ['Eskom Gas SCO', 'Pumped Water SCO Pumping', 'Hydro Water SCO', 'Eskom OCGT SCO',
                'Thermal Generation', 'Nuclear Generation', 'International Imports', 'Eskom OCGT Generation',
                'Eskom Gas Generation', 'Dispatchable IPP OCGT',
                'Hydro Water Generation', 'Pumped Water Generation', 'IOS Excl ILS and MLR', 'ILS Usage',
                'Manual Load_Reduction(MLR)', 'Wind', 'PV', 'CSP', 'Other RE']

    # 先获取数据
    data = re.compile(r'aria-label="(?P<name>.*?)"', re.S)
    data_result = data.findall(html)

    # 经常出错 因为每次爬取的时候的时间长度并不一致 所以想出以下办法
    # 先将列表中的非数字元素剔除掉
    result = []
    for x in data_result:
        # noinspection PyBroadException
        try:
            result.append(float(x))
        except:
            pass
    # 再用只包含数字的新列表除以19（一共19列数据） 如果能够整除 则正确 否则报错
    if len(result) % 19 == 0:
        len_result = int(len(result) / 19)
    else:
        print('error when crawling data')
        return

    # 提取数据到dataframe中
    df_result = pd.DataFrame()
    for i in range(0, len(result), len_result):
        temp = pd.DataFrame(result[i:i + len_result])
        df_result = pd.concat([df_result, temp], axis=1).reset_index(drop=True)

    # 获取日期
    date = re.compile(r'<div title="(?P<name>.*?)"', re.S)
    # 起始日期
    start_date = date.findall(html)
    start_date = [start_date[i] for i, x in enumerate(start_date) if x.find('/') != -1]
    start_date = min(start_date)
    date_range = pd.date_range(start=start_date, periods=len_result, freq='H')

    # 填充列名
    df_result.columns = col_list
    df_result['Date Time Hour Beginning'] = date_range

    # 新旧合并
    df_old = pd.read_csv(out_file)
    df_result = pd.concat([df_old, df_result]).reset_index(drop=True)
    df_result['Date Time Hour Beginning'] = pd.to_datetime(df_result['Date Time Hour Beginning'])
    df_result = df_result[~df_result.duplicated(['Date Time Hour Beginning'])]  # 删除重复的部分
    df_result.to_csv(out_file, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
