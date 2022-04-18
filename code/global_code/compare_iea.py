import re
import numpy as np
import pandas as pd
import global_function as af


file_path = '../../data/'
global_path = '../../data/global/'
file_name = af.search_file(file_path)
file_name_iea = [file_name[i] for i, x in enumerate(file_name) if x.find('iea_cleaned.csv') != -1]
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
    if c != 'russia':
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
df_all = df_all.set_index(
    ['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country']).stack().reset_index().rename(
    columns={'level_7': 'Type', 0: 'Value'})
df_all = df_all[df_all['Type'].isin(['coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other'])].reset_index(
    drop=True)
df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
df_all['country'] = df_all['country'].str.replace('Us', 'United States')

col_list = ['date', 'year', 'country', 'Type', 'Value']
yesterday = af.get_yesterday().strftime('%Y-%m-%d')
df_all = df_all[df_all['date'] < yesterday].reset_index(drop=True)
df_all['year'] = df_all['date'].dt.year
df_all = df_all[
    (df_all['year'] >= 2019) & (df_all['year'] <= 2021)].reset_index(drop=True)
df_all = pd.pivot_table(df_all, index=['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country'],
                        values='Value', columns='Type').reset_index()

df_all = df_all[['country', 'date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']]
df_all = df_all.set_index(['country', 'date']).stack().reset_index().rename(
    columns={'Type': 'energy_source', 0: 'pm', 'country': 'country/region'})

df_all = df_all[['country/region', 'date', 'energy_source', 'pm']]
df_t = df_all.groupby(['date', 'energy_source']).sum().reset_index()
df_all['year'] = df_all['date'].dt.year
df_all['month'] = df_all['date'].dt.month
df_all = df_all.groupby(['country/region', 'year', 'month', 'energy_source']).sum().reset_index()

# 找出欧盟27国和UK (其实是26少了Malta)
df_c = pd.read_csv(global_path+'EU_country_list.csv')
eu27_list = df_c['country'].tolist() + ['United Kingdom']
df_eu27 = df_all[df_all['country/region'].isin(eu27_list)].groupby(
    ['year', 'month', 'energy_source']).sum().reset_index()
df_eu27['country/region'] = 'EU27&UK'
df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)

# iea数据
df_iea = pd.read_csv(file_name_iea[0]).rename(columns={'Total Combustible Fuels': 'total'})
df_iea = df_iea.set_index(['country', 'year', 'month']).stack().reset_index().rename(
    columns={'level_3': 'energy_source', 0: 'iea', 'country': 'country/region'})
df_iea = df_iea[(df_iea['year'] >= 2019) & (df_iea['year'] <= 2021)].reset_index(drop=True)
df_iea['country/region'] = df_iea['country/region'].str.replace("People's Republic of China", "China").str.replace(
    "OECD Europe", "EU27&UK")

# 从iea里面去掉Malta这个国家
df_temp = pd.pivot_table(df_iea[df_iea['country/region'].isin(['EU27&UK', 'Malta'])],
                         index=['year', 'month', 'energy_source'], values='iea', columns='country/region').reset_index()
df_temp['EU27&UK'] = df_temp['EU27&UK'] - df_temp['Malta']
df_temp = df_temp.drop(columns=['Malta'])
df_temp = df_temp.set_index(['year', 'month', 'energy_source']).stack().reset_index().rename(
    columns={'level_3': 'country/region', 0: 'iea'})
# 把旧的EU27删掉
df_iea = df_iea[df_iea['country/region'] != 'EU27&UK'].reset_index(drop=True)
# 把新的加进去
df_iea = pd.concat([df_iea, df_temp]).reset_index(drop=True)

df_result = pd.merge(df_all, df_iea)
df_result['country/region'] = df_result['country/region'].str.replace('United States', 'US').str.replace(
    'United Kingdom', 'UK')
df_result['date'] = pd.to_datetime(df_all[['year', 'month']].assign(Day=1))  # 合并年月

# 年份差异
df_result.to_csv(global_path+'global_compare_iea.csv', index=False,
                 encoding='utf_8_sig')

