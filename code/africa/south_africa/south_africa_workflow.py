from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import pandas as pd
import re
import os

import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af
from global_code import global_all as g

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
    url = 'https://www.eskom.co.za/dataportal/supply-side/station-build-up-for-the-last-7-days/'
    # 开始模拟
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument("window-size=1024,768")
    chrome_options.add_argument("--no-sandbox")
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # wd = webdriver.Chrome(chromedriver) #打开浏览器
    wd.get(url)  # 打开要爬的网址
    wd.implicitly_wait(10)
    time.sleep(15)
    html = wd.page_source

    # 获取新网址
    url_name = re.compile(r'<iframe loading="lazy" width="600" height="600" src="(?P<name>.*?)">', re.S)
    new_url = url_name.findall(html)[0]
    wd.quit()
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wd.get(new_url)  # 打开要爬的网址
    print(wd.page_source)

    # 找到右键元素
    confirm_text = 'clearCatcher'
    ActionChains(wd).context_click(wd.find_elements(By.CLASS_NAME, confirm_text)[0]).perform()  # 右键

    wd.find_element(By.XPATH, '//*[@title="Show as a table"]').click()
    time.sleep(15)

    # 获取当前页面的源代码 所要数据就藏在里面
    html = wd.page_source
    wd.quit()

    # 获取列名
    col_list = ['Eskom Gas SCO', 'Pumped Water SCO Pumping', 'Hydro Water SCO', 'Eskom OCGT SCO',
                'Thermal Generation', 'Nuclear Generation', 'International Imports', 'Eskom OCGT Generation',
                'Eskom Gas Generation', 'Dispatchable IPP OCGT',
                'Hydro Water Generation', 'Pumped Water Generation', 'IOS Excl ILS and MLR', 'ILS Usage',
                'Manual Load_Reduction(MLR)', 'Wind', 'PV', 'CSP', 'Other RE']
    # 获取日期
    date = re.compile(r'<div title="(?P<name>.*?)"', re.S)
    # 起始日期
    start_date = date.findall(html)
    start_date = [start_date[i] for i, x in enumerate(start_date) if x.find('/') != -1]
    start_date = min(start_date)
    date_range = pd.date_range(start=start_date, periods=168, freq='h')

    # 获取数据
    data = re.compile(r'aria-label="(?P<name>.*?)"', re.S)
    data_result = data.findall(html)[10:]

    # 提取数据到dataframe中
    df_result = pd.DataFrame()
    for i in range(0, len(data_result), 24 * 7):
        temp = pd.DataFrame(data_result[i:i + 168])
        df_result = pd.concat([df_result, temp], axis=1).reset_index(drop=True)

    # 去除最后一列的乱码列
    df_result = df_result.iloc[:, :-1]
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
