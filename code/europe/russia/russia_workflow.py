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

    # 校准数据
    df['M_DATE'] = pd.to_datetime(df['M_DATE'], format='%d.%m.%Y 0:00:00')
    # 2016-01-01 ~ 2020-03-23 的所有thermal数据乘以1.8
    index_list = df[(df['M_DATE'] >= '2016-01-01') & (df['M_DATE'] <= '2020-03-23')].index.tolist()
    for t in index_list:
        df.loc[t, 'P_TES'] = df.loc[t, 'P_TES'] * 1.8
    # 2016-05-01 ~ 2016-09-18 的thermal数据再乘以1.3
    index_list = df[(df['M_DATE'] >= '2016-05-01') & (df['M_DATE'] <= '2016-09-18')].index.tolist()
    for t in index_list:
        df.loc[t, 'P_TES'] = df.loc[t, 'P_TES'] * 1.3
    # 2017-05-01 ~ 2017-09-18 的thermal数据再乘以1.3
    index_list = df[(df['M_DATE'] >= '2017-05-01') & (df['M_DATE'] <= '2017-09-18')].index.tolist()
    for t in index_list:
        df.loc[t, 'P_TES'] = df.loc[t, 'P_TES'] * 1.3
    # 2018-05-01 ~ 2018-09-18 的thermal数据再乘以1.3
    index_list = df[(df['M_DATE'] >= '2018-05-01') & (df['M_DATE'] <= '2018-09-18')].index.tolist()
    for t in index_list:
        df.loc[t, 'P_TES'] = df.loc[t, 'P_TES'] * 1.3
    # 2019-05-01 ~ 2019-09-18 的thermal数据再乘以1.3
    index_list = df[(df['M_DATE'] >= '2019-05-01') & (df['M_DATE'] <= '2019-09-18')].index.tolist()
    for t in index_list:
        df.loc[t, 'P_TES'] = df.loc[t, 'P_TES'] * 1.3

    df.to_csv(os.path.join(out_path, 'Russia_Hourly_Generation.csv'), index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
