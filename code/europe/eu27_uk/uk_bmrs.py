# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : UK_BMRE.py

import requests
import pandas as pd
from datetime import datetime
import json
from tqdm import tqdm
import os

parameter = {"flowid": "gbfthistoric", "start_date": "", "end_date": ""}
base_url = 'https://www.bmreports.com/bmrs/?q=tabledemand&parameter='

path = './data/europe/eu27_uk/raw/uk-BMRS/'

flag = 1
output_file = os.path.join(path, 'UK_BMRS_Hourly.csv')
if os.path.exists(output_file):
    df = pd.read_csv(output_file, index_col=1)
    start_date = df.index.max()
    flag = 0
else:
    start_date = '2018-01-01'
end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
date_range = pd.date_range(start_date, end_date)


def main():
    bmrs()  # 下载BMRS数据
    uk_solar()  # 下载solar数据并合并到BMRS里


def bmrs():
    global flag
    for d in tqdm(range(len(date_range) - 1)):
        parameter['start_date'] = datetime.strftime(date_range[d], '%Y-%m-%d')
        parameter['end_date'] = datetime.strftime(date_range[d + 1], '%Y-%m-%d')

        url = base_url + str(parameter).replace('\'', '\"')
        res = requests.get(url)
        js = json.loads(res.text)['responseBody']['responseList']['item']
        df_temp = pd.DataFrame(js)
        if flag:
            df_temp.to_csv(output_file, index=False)
            flag = 0
        else:
            df_temp.to_csv(output_file, index=False, header=False, mode='a')


def uk_solar():
    df_solar = pd.read_csv(output_file)  # 读取BMRS数据
    # 处理BMRS数据
    df_solar['datetime'] = pd.to_datetime(df_solar['startTimeOfHalfHrPeriod']) + pd.to_timedelta(
        (df_solar['settlementPeriod'] / 2 - 0.5), unit='h')
    df_solar = df_solar.set_index('datetime').resample('H').mean().reset_index()  # 为啥是mean而不是sum？

    #  设定数据范围
    end_year = int(datetime.now().strftime('%Y')) + 1
    df_result = pd.DataFrame()
    for i in range(2018, end_year):
        start = '%s-01-01' % i
        end = '%s-12-31' % i
        url = 'https://api0.solar.sheffield.ac.uk/pvlive/v3/ggd/0?&start=%sT00:00:00&end=%sT23:59:59&data_format=csv' % (
            start, end)
        df_new = pd.read_csv(url).rename(columns={'generation_mw': 'solar', 'datetime_gmt': 'datetime'}).drop(
            columns=['n_ggds', 'ggd_id'])  # 单位为mw
        df_new['datetime'] = pd.to_datetime(df_new['datetime']).dt.tz_localize(None)
        df_new = df_new.set_index('datetime').resample('h').sum().reset_index()  # 汇总为小时数据Mwh
        df_result = pd.concat([df_result, df_new]).reset_index(drop=True)
    # 合并bmrs和缺失的solar数据
    df_solar = pd.merge(df_solar, df_result)
    df_solar.to_csv(output_file, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
