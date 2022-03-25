import datetime

import pandas as pd
import numpy as np
import re
import os
import sys

module_path_string = "K:\Github\GlobalPowerUpdate-Kow\数据库\code\global_code"
sys.path.append(module_path_string)
import global_function as af

file_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\数据库\\data\\'
file_name = []
for parent, dirnames, filenames in os.walk(file_path):
    for fn in filenames:
        file_name.append(os.path.join(parent, fn))
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
file_name_no = [file_name[i] for i, x in enumerate(file_name) if not x.find('eu27_uk') != -1]
file_name_eu = [file_name[i] for i, x in enumerate(file_name) if x.find('eu27_uk') != -1]
file_name_eu = [file_name_eu[i] for i, x in enumerate(file_name_eu) if not x.find('United Kingdom') != -1]

# 提取国家名
title = re.compile(r'data.*?\\.*?\\(?P<name>.*?)\\simulated', re.S)
country_name_no = []
for f in file_name_no:
    result = title.finditer(f)
    for it in result:
        country_name_no.append(it.group('name'))

# 欧盟国家
title = re.compile(r'daily\\(?P<name>.*?).csv', re.S)
country_name_eu = []
for f in file_name_eu:
    result = title.finditer(f)
    for it in result:
        country_name_eu.append(it.group('name'))

result_no = []
for f, c in zip(file_name_no, country_name_no):
    if c != 'russia':
        df_temp = pd.read_csv(f)
        af.time_info(df_temp, 'date')
        df_temp = af.check_col(df_temp, 'daily')
        df_temp['country'] = c.capitalize()
        result_no.append(df_temp)
df_no = pd.DataFrame(np.concatenate(result_no), columns=df_temp.columns)

result_eu = []
for f, c in zip(file_name_eu, country_name_eu):
    df_temp = pd.read_csv(f)
    df_temp['country'] = c.capitalize()
    result_eu.append(df_temp)
df_eu = pd.DataFrame(np.concatenate(result_eu), columns=df_temp.columns)
df_all = pd.concat([df_no, df_eu]).reset_index(drop=True)

result_eu_all = []
for f, c in zip(file_name_eu, country_name_eu):
    df_temp = pd.read_csv(f)
    df_temp['country'] = 'EU27&UK'
    result_eu_all.append(df_temp)
df_eu_all = pd.DataFrame(np.concatenate(result_eu_all), columns=df_temp.columns)
df_eu_all = df_eu_all.groupby(['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country']).sum().reset_index()
df_all = pd.concat([df_all, df_eu_all]).reset_index(drop=True)

# russia
file_name_russia = [file_name_no[i] for i, x in enumerate(file_name_no) if x.find('russia') != -1]
df_russia = pd.concat([pd.read_csv(f) for f in file_name_russia]).drop(
    columns=['P_BS', 'renewables', 'P_BS.perc', 'renewables.perc'])
df_russia['country'] = 'Russia'

df_all = pd.concat([df_all, df_russia]).reset_index(drop=True)
for x in df_all.columns.tolist():
    try:
        df_all[x] = df_all[x].astype(float)
    except:
        pass
af.time_info(df_all, 'date')

df_all = df_all.set_index(
    ['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country']).stack().reset_index().rename(
    columns={'level_7': 'Type', 0: 'Value'})
df_all = df_all[df_all['Type'].isin(['coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other'])].reset_index(
    drop=True)
df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'UK')
df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
df_all['country'] = df_all['country'].str.replace('Us', 'United States')

col_list = ['date', 'year','country', 'Type', 'Value']
yesterday = af.get_yesterday().strftime('%Y-%m-%d')
df_all = df_all[df_all['date'] < yesterday].reset_index(drop=True)
df_all['year'] = df_all['date'].dt.year
df_all[col_list].to_csv(file_path + 'global\\global.csv', index=False, encoding='utf_8_sig')
df_pivot = pd.pivot_table(df_all, index=['month_date', 'country', 'Type'], values='Value', columns='year').reset_index()
df_pivot.to_csv(file_path + 'global\\global_line_chart.csv', index=False, encoding='utf_8_sig')

df_all = df_all[(df_all['year'] >= 2019) & (df_all['year'] <= 2022)].reset_index(drop=True)
df_all['date'] = pd.to_datetime(df_all['date'])
df_all = df_all.drop(columns=['weekday', 'month', 'unit'])
index_list = ['month_date', 'country', 'Type']
df_2019 = df_all[df_all['year'] == 2019].set_index(index_list)
df_rest = df_all[df_all['year'] != 2019].set_index(index_list)

df_relative = (df_rest - df_2019).reset_index().dropna().drop(columns=['date'])
df_relative['year'] += 2019
df_relative['year'] = df_relative['year'].astype(int)
df_relative['date'] = df_relative['year'].astype(str) + '-' + df_relative['month_date'].astype(str)
df_relative['date'] = pd.to_datetime(df_relative['date'])
df_relative['month'] = df_relative['date'].dt.month
df_relative.to_csv(file_path + 'global\\global_relative.csv', index=False, encoding='utf_8_sig')

df_relative = pd.pivot_table(
    df_all, index=['month_date', 'country', 'Type'], values='Value', columns='year').reset_index()
df_relative.to_csv(file_path + 'global\\global_relative_line_chart.csv', index=False, encoding='utf_8_sig')


# ############################################################################
# df_all = df_all[(df_all['year'] >= 2021) & (df_all['year'] <= 2022)].reset_index(drop=True)
# df_all['date'] = pd.to_datetime(df_all['date'])
# df_all = df_all.drop(columns=['weekday', 'month', 'unit'])
# index_list = ['month_date', 'country', 'Type']
# df_2021 = df_all[df_all['year'] == 2021].set_index(index_list)
# df_rest = df_all[df_all['year'] != 2021].set_index(index_list)
#
# df_relative = (df_rest - df_2021).reset_index().dropna().drop(columns=['date'])
# df_relative['year'] += 2021
# df_relative['year'] = df_relative['year'].astype(int)
# df_relative['date'] = df_relative['year'].astype(str) + '-' + df_relative['month_date'].astype(str)
# df_relative['date'] = pd.to_datetime(df_relative['date'])
# df_relative['month'] = df_relative['date'].dt.month
# df_relative.to_csv(file_path + 'global\\global_relative_2022.csv', index=False, encoding='utf_8_sig')

