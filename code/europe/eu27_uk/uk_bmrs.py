# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : UK_BMRE.py

import requests
import pandas as pd
from datetime import datetime
import json
import os

parameter = {"flowid": "gbfthistoric", "start_date": "", "end_date": ""}
base_url = 'https://www.bmreports.com/bmrs/?q=tabledemand&parameter='

path = './data/europe/eu27_uk/raw/uk-BMRS/'
if not os.path.exists(path):
    os.mkdir(path)

output_file = os.path.join(path, 'UK_BMRS_Hourly.csv')
if os.path.exists(output_file):
    df = pd.read_csv(output_file)
    start_date = max(df['datetime'])
else:
    start_date = '2018-01-01'
end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
date_range = pd.date_range(start_date, end_date)


def main():
    uk_solar()


# 下载bmrs数据
def uk_bmrs():
    df_temp = pd.DataFrame()
    for d in range(len(date_range) - 1):
        parameter['start_date'] = datetime.strftime(date_range[d], '%Y-%m-%d')
        parameter['end_date'] = datetime.strftime(date_range[d + 1], '%Y-%m-%d')

        url = base_url + str(parameter).replace('\'', '\"')
        res = requests.get(url)
        js = json.loads(res.text)['responseBody']['responseList']['item']
        df_temp = pd.DataFrame(js)
        df_temp['settlementPeriod'] = df_temp['settlementPeriod'].astype(int)
        # 整理小时数据
        df_temp['datetime'] = pd.to_datetime(df_temp['startTimeOfHalfHrPeriod']) + pd.to_timedelta(
            (df_temp['settlementPeriod'] / 2 - 0.5), unit='h')
        # 统一格式
        df_temp = df_temp.drop(columns=['recordType', 'startTimeOfHalfHrPeriod', 'settlementPeriod', 'activeFlag'])
        for c in df_temp.columns:
            if c != 'datetime':
                df_temp[c] = df_temp[c].astype(float)
        # 汇总为小时数据
        df_temp = df_temp.set_index('datetime').resample('H').mean().reset_index()
    return df_temp


# 下载uk solar新数据
def uk_solar():
    df_temp = uk_bmrs()
    s_d = pd.to_datetime(min(df_temp['datetime'])).strftime('%Y-%m-%d')  # 读取bmrs的起始日期
    url = 'https://api0.solar.sheffield.ac.uk/pvlive/v3/ggd/0?&start=%sT00:00:00&end=%sT23:59:59&data_format=csv' % (
        s_d, end_date)
    df_new = pd.read_csv(url).rename(columns={'generation_mw': 'solar', 'datetime_gmt': 'datetime'}).drop(
        columns=['n_ggds', 'ggd_id'])  # 单位为mw
    df_new['datetime'] = pd.to_datetime(df_new['datetime']).dt.tz_localize(None)
    df_new = df_new.set_index('datetime').resample('h').mean().reset_index()  # 汇总为小时数据Mwh
    df_result = pd.merge(df_temp, df_new)
    df_old = pd.read_csv(output_file)

    # 合并结果
    df_new_result = pd.concat([df_old, df_result]).reset_index(drop=True)
    df_new_result.to_csv(output_file, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
