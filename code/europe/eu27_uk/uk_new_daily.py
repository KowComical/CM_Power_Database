import os
import re
from datetime import timedelta

import pandas as pd
import requests

# UK 10年的daily新数据
file_path = './data/europe/eu27_uk/raw/uk_Electricity_Produ`ction/'
if not os.path.exists(file_path):
    os.mkdir(file_path)
out_path = os.path.join(file_path, 'uk_daily.csv')


def main():
    craw_daily()


def craw_daily():
    df_old = pd.read_csv(out_path)
    col_list = ['Biomass', 'CCGT', 'Coal', 'Hydroelectric', 'Interconnect', 'Nuclear', 'OCGT', 'Oil', 'Other',
                'Pumped Storage', 'Wind', 'solar']
    date_list = ['year', 'month', 'day', 'hour', 'minute']

    url = 'https://electricityproduction.uk/from/all-sources/?t=10y'
    r = requests.get(url)
    # 筛选有用数据
    data_table = re.compile(r'allsource_data.addRows(?P<name>.*?);', re.S)
    # list to dataframe
    df = pd.DataFrame(data_table.findall(r.text)[0][2:-3].split('['))[1:]
    df = df[0].str.split('[)],', expand=True)
    # 提取更新到的时间
    date = re.compile(r'<p class="text-right">Last.*?updated (?P<name>.*?). G', re.S)
    max_date = date.findall(r.text)[0]
    max_date = pd.to_datetime(max_date)
    max_date = (max_date - timedelta(days=1)).strftime('%Y-%m-%d')  # 最新的一天的数据还未生成

    # 生成日期range
    date_range = pd.date_range(end=max_date, periods=len(df), freq='1d')[::-1]

    # 处理data格式
    df_data = df[1].str.split(',', expand=True).drop(columns=[12, 13])
    df_data.columns = col_list

    df_data['datetime'] = date_range
    # 合并新旧
    df = pd.concat([df_old, df_data]).reset_index(drop=True)
    # 去除重复的部分
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[~df.duplicated(['datetime'])].reset_index(drop=True)
    df = df.sort_values('datetime').reset_index(drop=True)
    # 输出
    df.to_csv(out_path, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
