import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import os

import sys

sys.dont_write_bytecode = True
sys.path.append('./code/global_code/')
import global_function as af

file_path = './data/'
global_path = os.path.join(file_path, 'global')
out_path = './image/'

file_name = af.search_file(file_path)
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
file_name_no = [file_name[i] for i, x in enumerate(file_name) if not x.find('eu27_uk') != -1]
file_name_eu = [file_name[i] for i, x in enumerate(file_name) if x.find('eu27_uk') != -1]
file_name_eu = [file_name_eu[i] for i, x in enumerate(file_name_eu) if not x.find('United Kingdom') != -1]

# # 提取主要国家名
name = re.compile(r'data/.*?/(?P<name>.*?)/simulated', re.S)
result_no = []
for f in file_name_no:
    c = name.findall(f)[0]
    df_temp = pd.read_csv(f)
    af.time_info(df_temp, 'date')
    df_temp = af.check_col(df_temp, 'daily')
    df_temp['country'] = c.capitalize()
    result_no.append(df_temp)
df_no = pd.DataFrame(np.concatenate(result_no), columns=df_temp.columns)

# 欧州国家
eu_name = re.compile(r'daily/(?P<name>.*?).csv', re.S)
result_eu = []
for f in file_name_eu:
    c = eu_name.findall(f)[0]
    df_temp = pd.read_csv(f)
    df_temp['country'] = c.capitalize()
    result_eu.append(df_temp)
df_eu = pd.DataFrame(np.concatenate(result_eu), columns=df_temp.columns)

# 合并并处理
df_all = pd.concat([df_no, df_eu]).reset_index(drop=True)

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
df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
df_all['country'] = df_all['country'].str.replace('Us', 'United States')

# 前一天的数据基本都不准确
col_list = ['date', 'year', 'country', 'Type', 'Value']
yesterday = af.get_yesterday().strftime('%Y-%m-%d')
df_all = df_all[df_all['date'] < yesterday].reset_index(drop=True)
df_all['year'] = df_all['date'].dt.year

df_all = pd.pivot_table(df_all, index=['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country'],
                        values='Value', columns='Type').reset_index()

df_all = df_all[['country', 'date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']]
df_all = df_all.set_index(['country', 'date']).stack().reset_index().rename(
    columns={'Type': 'energy_source', 0: 'value', 'country': 'country/region'})

# 添加欧盟
df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))

eu27_list = df_c['country'].tolist() + ['United Kingdom']
df_eu27 = df_all[df_all['country/region'].isin(eu27_list)].groupby(
    ['date', 'energy_source']).sum().reset_index()
df_eu27['country/region'] = 'EU27&UK'
df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)

df_all = df_all.groupby(['country/region', 'date']).sum().reset_index()
df_all = pd.pivot_table(df_all, index='date', values='value', columns='country/region').reset_index()
country_list = ['Brazil', 'China', 'Russia', 'EU27&UK', 'France', 'Germany', 'India', 'Italy', 'Japan', 'Spain',
                'United Kingdom', 'United States']
df_all = df_all[['date'] + country_list]
df_all = df_all[df_all['date'] >= '2019-01-01'].reset_index(drop=True)
df_all['year'] = df_all['date'].dt.year
df_all['month'] = df_all['date'].dt.month

plt.figure(figsize=(100, 50))
for i in range(len(country_list)):
    pic = plt.subplot(3, 4, i + 1)
    af.draw_pic(df_all, country_list[i], i)
plt.tight_layout()
plt.savefig(os.path.join(out_path, 'Power generation for all country.svg'), format='svg')
