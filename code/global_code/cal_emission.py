import pandas as pd
import numpy as np
import re
import sys
import os

sys.dont_write_bytecode = True
sys.path.append('../../code/global_code/')
import global_function as af


data_path = '../../data/'
global_path = os.path.join(data_path, 'global')
ef_path = os.path.join(data_path, 'ef')
cm_path = os.path.join(data_path, '#global_rf')

file_name = af.search_file(data_path)
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
file_name_no = [file_name[i] for i, x in enumerate(file_name) if not x.find('eu27_uk') != -1]
file_name_eu = [file_name[i] for i, x in enumerate(file_name) if x.find('eu27_uk') != -1]
file_name_eu = [file_name_eu[i] for i, x in enumerate(file_name_eu) if not x.find('United Kingdom') != -1]

# # 提取主要国家名
name = re.compile(r'data/.*?\\(?P<name>.*?)\\simulated', re.S)
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

df_all['date'] = pd.to_datetime(df_all['date'])
df_all = df_all[['country', 'date', 'coal', 'gas', 'oil']]
df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
df_all['country'] = df_all['country'].str.replace('Us', 'United States')

# 只要19年到22年3月底
# df_pic = df_pic[(df_pic['date'] >= '2019-01-01') & (df_pic['date'] < '2022-04-01')].reset_index(drop=True)  # 这句随时要改
df_all = df_all.set_index(['country', 'date']).stack().reset_index().rename(columns={'level_2': 'type', 0: 'value'})
df_all['year'] = df_all['date'].dt.year

# 添加欧盟
df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))

eu27_list = df_c['country'].tolist() + ['United Kingdom']
df_eu27 = df_all[df_all['country'].isin(eu27_list)].groupby(
    ['date', 'year', 'type']).sum().reset_index()
df_eu27['country'] = 'EU27&UK'
df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)
df_all['value'] = df_all['value'].astype(float)
# # 读取排放因子
# df_ef = pd.read_csv(os.path.join(ef_path, 'ef.csv'))
# df_pic = pd.merge(df_pic, df_ef)
# df_pic['emission'] = df_pic['value'] * df_pic['ef'] / 1000
# df_pic = df_pic.groupby(['country', 'date']).sum().reset_index().drop(columns=['year', 'ef', 'value'])
#
# # 读取CM数据做后续比较
# df_cm = pd.read_csv(os.path.join(cm_path, 'CM_v2021.11.csv'))
# df_cm['country'] = df_cm['country'].replace('UK', 'United Kingdom')
# df_cm['date'] = pd.to_datetime(df_cm['date'])
# df_cm = df_cm[df_cm['sector'] == 'Power'].reset_index(drop=True)
#
# df_result = pd.merge(df_pic, df_cm).rename(columns={'emission': 'PM', 'co2': 'CM'})
# df_pic = pd.pivot_table(df_pic, index='date', values='emission', columns='country').reset_index()
#
# df_result.to_csv(os.path.join(global_path, 'compare_CM.csv'), index=False, encoding='utf_8_sig')
# df_pic.to_csv(os.path.join(global_path, 'Global_Power_Emission.csv'), index=False, encoding='utf_8_sig')
