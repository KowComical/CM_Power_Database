import pandas as pd
import numpy as np
import re
import os
import sys

sys.path.append('K:\\Github\\GlobalPowerUpdate-Kow\\code\\global_code\\')
import global_function as af

file_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\'
global_path = os.path.join(file_path, 'global')
out_file = os.path.join(global_path, 'global_shadow_all.csv')

file_name = af.search_file(file_path)
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
file_name_no = [file_name[i] for i, x in enumerate(file_name) if not x.find('eu27_uk') != -1]
file_name_eu = [file_name[i] for i, x in enumerate(file_name) if x.find('eu27_uk') != -1]
file_name_eu = [file_name_eu[i] for i, x in enumerate(file_name_eu) if not x.find('United Kingdom') != -1]

# # 提取主要国家名
name = re.compile(r'data\\.*?\\(?P<name>.*?)\\simulated', re.S)
df_all = pd.DataFrame()
for f in file_name_no:
    c = name.findall(f)[0]
    df_temp = pd.read_csv(f)
    af.time_info(df_temp, 'date')
    df_temp = af.check_col(df_temp, 'daily')
    df_temp['country'] = c.capitalize()
    df_all = pd.concat([df_all, df_temp]).reset_index(drop=True)

# 欧州国家
eu_name = re.compile(r'daily\\(?P<name>.*?).csv', re.S)
for f in file_name_eu:
    c = eu_name.findall(f)[0]
    df_temp = pd.read_csv(f)
    df_temp['country'] = c.capitalize()
    df_all = pd.concat([df_all, df_temp]).reset_index(drop=True)

# 合并并处理
df_all = df_all.set_index(
    ['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country']).stack().reset_index().rename(
    columns={'level_7': 'Type', 0: 'Value'})
df_all = df_all[df_all['Type'].isin(['coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other'])].reset_index(
    drop=True)
df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'UK')
df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
df_all['country'] = df_all['country'].str.replace('Us', 'United States')

col_list = ['date', 'year', 'country', 'Type', 'Value']
yesterday = af.get_yesterday().strftime('%Y-%m-%d')
df_all = df_all[df_all['date'] < yesterday].reset_index(drop=True)
df_all['year'] = df_all['date'].dt.year

df_all = df_all[col_list]

df_all = df_all[(df_all['year'] >= 2020)].reset_index(drop=True)
df_all['Type'] = df_all['Type'].str.capitalize()
country_list = df_all['country'].drop_duplicates().tolist()
type_list = df_all['Type'].drop_duplicates().tolist()
for x in country_list:
    for y in type_list:
        try:
            test = df_all[(df_all['country'] == x) & (df_all['Type'] == y)].reset_index(drop=True)
            test = af.check_date(test, 'date', 'd')
            test['country'] = x
            test['Type'] = y
            missing_date = test[test.T.isnull().any()]['month_date'].tolist()
            existing_index = test[(test['year'] == 2021) & (test['month_date'].isin(missing_date))].index.tolist()
            missing_index = test[test.T.isnull().any()].index.tolist()
            for t, z in zip(missing_index, existing_index):
                test.loc[t, 'Value'] = test.loc[z, 'Value']

            test = test[test['month_date'] != '02-29'].reset_index(drop=True)
            test['date'] = '2020-' + test['month_date']
            if os.path.exists(out_file):
                test.to_csv(out_file, mode='a', header=False, index=False, encoding='utf_8_sig')
            else:
                test.to_csv(out_file, index=False, encoding='utf_8_sig')
        except:
            pass
