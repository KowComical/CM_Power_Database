import re
import requests
import pandas as pd
import os

import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af
from global_code import global_all as g

out_path = './data/africa/south_africa/raw/'
out_file = os.path.join(out_path, 'last_7_days.csv')


def main():
    # 爬虫+预处理数据
    craw()
    # 整理数据
    g.south_africa()
    # 提取最新日期
    af.updated_date('south_africa')


def craw():
    url = 'https://www.eskom.co.za/dataportal/supply-side/station-build-up-for-the-last-7-days/'

    r = requests.get(url)
    path = re.compile(r'<h3 class="elementor-icon-box-title">.*?<a href="(?P<name>.*?)">Download data file</a>', re.S)
    download_path = path.findall(r.text)[0]  # 找到下载链接地址

    df = pd.read_csv(download_path)  # 提取数据
    df = df.dropna(axis=0, how='all', thresh=2).reset_index(drop=True)  # 非空值小于2时删除行
    df = df.drop(columns=['Thermal_Gen_Excl_Pumping_and_SCO'])  # 删除不需要的列
    # 读取旧数据并合并未重复部分
    df_old = pd.read_csv(out_file)
    df_result = pd.concat([df_old, df]).reset_index(drop=True)
    df_result['Date_Time_Hour_Beginning'] = pd.to_datetime(df_result['Date_Time_Hour_Beginning'])
    # 删除重复的日期
    df_result = df_result[~df_result.duplicated(['Date_Time_Hour_Beginning'])].sort_values(
        by='Date_Time_Hour_Beginning').reset_index(drop=True)
    # 输出
    df_result.to_csv(out_file, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
