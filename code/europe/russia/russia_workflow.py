# 数据源来自: Zhu Deng
import requests
import sys
import pandas as pd
import os

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af
from global_code import global_all as g

out_path = './data/europe/russia/raw/'


def main():
    # 爬虫
    craw()
    # 处理数据
    g.russia()
    # 提取最新日期
    af.updated_date('Russia')


def craw():
    url = 'https://emres.cn/api/carbonmonitor/getRussiaPowerHourly.php'
    r = requests.get(url)
    df = pd.json_normalize(r.json())
    df.to_csv(os.path.join(out_path, 'Russia_Hourly_Generation.csv'), index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
