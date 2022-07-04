import time
from datetime import datetime, timezone
import pandas as pd
import re
import os

import sys

sys.dont_write_bytecode = True
sys.path.append('./code/global_code/')
import global_function as af

file_path = './data/'
global_path = os.path.join(file_path, 'global')


def main():
    process()


def process():
    file_name = af.search_file(file_path)
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
    file_name_no = [file_name[i] for i, x in enumerate(file_name) if not x.find('eu27_uk') != -1]
    file_name_eu = [file_name[i] for i, x in enumerate(file_name) if x.find('eu27_uk') != -1]
    file_name_eu = [file_name_eu[i] for i, x in enumerate(file_name_eu) if not x.find('United Kingdom') != -1]

    # 提取主要国家名
    name = re.compile(r'data/.*?/(?P<name>.*?)/simulated', re.S)

    df_all = pd.DataFrame()
    for f in file_name_no:
        c = name.findall(f)[0]
        df_temp = pd.read_csv(f)
        af.time_info(df_temp, 'date')
        df_temp = af.check_col(df_temp, 'daily')
        df_temp['country'] = c.capitalize()
        df_all = pd.concat([df_all, df_temp]).reset_index(drop=True)

    # 欧州国家
    eu_name = re.compile(r'daily/(?P<name>.*?).csv', re.S)
    for f in file_name_eu:
        c = eu_name.findall(f)[0]
        df_temp = pd.read_csv(f)
        df_temp['country'] = c.capitalize()
        df_all = pd.concat([df_all, df_temp]).reset_index(drop=True)

    # 处理
    for x in df_all.columns.tolist():
        # noinspection PyBroadException
        try:
            df_all[x] = df_all[x].astype(float)
        except:
            pass
    af.time_info(df_all, 'date')

    df_all = df_all.set_index(
        ['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country']).stack().reset_index().rename(
        columns={'level_7': 'Type', 0: 'Value'})
    df_all = df_all[
        df_all['Type'].isin(['coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other'])].reset_index(
        drop=True)
    df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'UK')
    df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
    df_all['country'] = df_all['country'].str.replace('Us', 'US')
    df_all['country'] = df_all['country'].str.replace('South_africa', 'South Africa')

    df_all = pd.pivot_table(df_all, index=['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country'],
                            values='Value', columns='Type').reset_index()

    df_all = df_all[['country', 'date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']]
    df_all = df_all.set_index(['country', 'date']).stack().reset_index().rename(
        columns={'Type': 'sector', 0: 'value'})

    # 添加欧盟
    df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))

    eu27_list = df_c['country'].tolist() + ['UK']
    df_eu27 = df_all[df_all['country'].isin(eu27_list)].groupby(
        ['date', 'sector']).sum().reset_index()
    df_eu27['country'] = 'EU27 & UK'
    df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)

    # 只需要重要国家
    country_list = ['Brazil', 'China', 'Russia', 'EU27 & UK', 'France', 'Germany', 'India', 'Italy', 'Japan', 'Spain',
                    'UK', 'US', 'South Africa']
    df_all = df_all[df_all['country'].isin(country_list)].reset_index(drop=True)
    df_all = df_all[(df_all['date'] >= '2019-01-01') & (df_all['date'] <= '2022-06-16')].reset_index(drop=True)
    # # 不要最后一天的数据
    # yesterday = af.get_yesterday().strftime('%Y-%m-%d')
    # df_all = df_all[(df_all['date'] >= '2019-01-01') & (df_all['date'] <= yesterday)].reset_index(drop=True)

    time_stamp = []  # 将当地时间转换为时间戳
    for d in df_all['date'].tolist():
        time_stamp.append(time.mktime(d.timetuple()))
    df_all['timestamp'] = time_stamp

    utc_time = []  # 将当地时间时间戳转换为utc时间
    for t in df_all['timestamp'].tolist():
        utc_time.append(datetime.fromtimestamp(t, tz=timezone.utc))
    df_all['utc'] = utc_time

    time_stamp = []  # 将utc时间转换为utc时间戳
    for d in df_all['utc'].tolist():
        time_stamp.append(time.mktime(d.timetuple()))
    df_all['timestamp'] = time_stamp
    df_all['timestamp'] = df_all['timestamp'].astype(int)

    df_all = df_all.drop(columns=['utc'])
    df_all['date'] = df_all['date'].dt.strftime('%d/%m/%Y')
    df_all['sector'] = df_all['sector'].str.title().replace('Other', 'Other sources').replace('Hydro',
                                                                                              'Hydroelectricity')
    df_all.to_csv(os.path.join(global_path, 'Global_PM_corT.csv'), index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
