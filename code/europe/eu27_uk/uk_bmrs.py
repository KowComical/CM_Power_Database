# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : UK_BMRE.py

import requests
import pandas as pd
from datetime import datetime
import json
import os
import datetime as dt

parameter = {"flowid": "gbfthistoric", "start_date": "", "end_date": ""}
base_url = 'https://www.bmreports.com/bmrs/?q=tabledemand&parameter='

file_path = './data/europe/eu27_uk/raw/uk-BMRS/'

output_file = os.path.join(file_path, 'UK_BMRS_Hourly.csv')


def main():
    uk_bmrs()


# 下载bmrs数据
def uk_bmrs():
    # 读取旧文件设定爬取时间范围
    df = pd.read_csv(output_file)
    df['datetime'] = pd.to_datetime(df['datetime'])

    start_date = (pd.to_datetime(max(df['datetime'])) - dt.timedelta(days=1)).strftime(
        '%Y-%m-%d')  # raw文件最大日期的前两天 否则有时会有bug
    end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    date_range = pd.date_range(start_date, end_date)
    # 开始爬取除solar能源数据
    df_result = pd.DataFrame()
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
        df_result = pd.concat([df_result, df_temp]).reset_index(drop=True)
    # 合并结果
    df = pd.concat([df, df_result]).reset_index(drop=True)
    df = df.set_index('datetime').resample('H').mean().reset_index()  # 去掉下载的重复部分

    # 开始爬取solar能源数据
    start_date = pd.to_datetime(min(df['datetime'])).strftime('%Y-%m-%d')  # 读取bmrs的起始日期 其实就是2018年1月1
    url = 'https://api0.solar.sheffield.ac.uk/pvlive/api/v4/gsp/0?&start=%sT00:00:00&end=%sT23:59:59&data_format=csv' % (
        start_date, end_date)
    # 清理数据
    df_solar = pd.read_csv(url).rename(columns={'generation_mw': 'solar', 'datetime_gmt': 'datetime'}).drop(
        columns=['gsp_id'])  # 单位为mw
    df_solar['datetime'] = pd.to_datetime(df_solar['datetime']).dt.tz_localize(None)
    df_solar = df_solar.set_index('datetime').resample('h').mean().reset_index()  # 汇总为小时数据Mwh
    df = df.drop(columns=['solar'])  # 删掉旧的solar
    df_result = pd.merge(df, df_solar)  # 替换为新的solar

    # 输出
    df_result.to_csv(output_file, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
