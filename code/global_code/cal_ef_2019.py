import pandas as pd
import numpy as np
import re
import sys

sys.dont_write_bytecode = True
sys.path.append('K:\\Github\\GlobalPowerUpdate-Kow\\code\\global_code\\')
import global_function as af
import os

file_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\'
global_path = os.path.join(file_path, 'global')
ef_path = os.path.join(file_path, 'ef')

file_name = af.search_file(file_path)
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
file_name_no = [file_name[i] for i, x in enumerate(file_name) if not x.find('eu27_uk') != -1]
file_name_eu = [file_name[i] for i, x in enumerate(file_name) if x.find('eu27_uk') != -1]
file_name_eu = [file_name_eu[i] for i, x in enumerate(file_name_eu) if not x.find('United Kingdom') != -1]

# # 提取主要国家名
name = re.compile(r'data\\.*?\\(?P<name>.*?)\\simulated', re.S)
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
eu_name = re.compile(r'daily\\(?P<name>.*?).csv', re.S)
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
    columns={'level_7': 'type', 0: 'value'})
df_all = df_all[df_all['type'].isin(['coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other'])].reset_index(
    drop=True)
df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
df_all['country'] = df_all['country'].str.replace('Us', 'United States')

# 添加欧盟
df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))

eu27_list = df_c['country'].tolist() + ['United Kingdom']
df_eu27 = df_all[df_all['country'].isin(eu27_list)].groupby(
    ['year', 'type']).sum().reset_index()
df_eu27['country'] = 'EU27&UK'
df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)

df_all = df_all.groupby(['country', 'year', 'type']).sum().reset_index().drop(columns=['month'])

# 只要主要国家
country_list = ['Brazil', 'China', 'Russia', 'EU27&UK', 'France', 'Germany', 'India', 'Italy', 'Japan', 'Spain',
                'United Kingdom', 'United States']
df_all = df_all[df_all['country'].isin(country_list)].reset_index(drop=True)
# 只要火电
type_list = ['coal', 'gas', 'oil']
df_all = df_all[df_all['type'].isin(type_list)].reset_index(drop=True)
# ################################################################# 计算排放因子 #############################################################
#  只要19年到22年3月的数据
df_all = df_all[df_all['year'] == 2019].reset_index(drop=True)

# 读取IPCC排放因子
df_ef = pd.read_csv(os.path.join(ef_path, 'IPCC_EFs.csv'))
# 根据IPCC排放因子计算排放
df_all = pd.merge(df_all, df_ef, left_on='type', right_on='type(10^6g/GWH)').drop(columns=['type(10^6g/GWH)'])
df_all['emission-ipcc-efs'] = df_all['value'] * df_all['ef'] / 1000000
# 汇总一个thermal排放出来
df_sum = df_all.groupby(['country', 'year']).sum().reset_index()
df_sum['type'] = 'thermal-emission'
df_all = pd.concat([df_all, df_sum]).reset_index(drop=True).drop(columns=['ef'])
df_power = pd.pivot_table(df_all, index=['country', 'year'], values='value', columns='type').reset_index()
df_all = pd.pivot_table(df_all, index=['country', 'year'], values='emission-ipcc-efs', columns='type').reset_index()

# 读取zd数据
df_zd = pd.read_csv(os.path.join(ef_path, 'Power-ZD.csv'))
df_all = pd.merge(df_all, df_zd)
df_all['thermal_factor'] = df_all['Power-ZD'] / df_all['thermal-emission']

df_all['coal_new'] = df_all['coal'] * df_all['thermal_factor']
df_all['gas_new'] = df_all['gas'] * df_all['thermal_factor']
df_all['oil_new'] = df_all['oil'] * df_all['thermal_factor']

df_all['coal'] = df_all['coal_new'] / df_power['coal'] * 1000000
df_all['gas'] = df_all['gas_new'] / df_power['gas'] * 1000000
df_all['oil'] = df_all['oil_new'] / df_power['oil'] * 1000000

df_ef = df_all[['country', 'coal', 'gas', 'oil']]
df_ef = df_ef.set_index(['country']).stack().reset_index().rename(columns={'level_1': 'type', 0: 'ef'})
df_ef.to_csv(os.path.join(ef_path, 'ef.csv'), index=False, encoding='utf_8_sig')
