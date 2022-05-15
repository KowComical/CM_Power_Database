import pandas as pd
import re
import sys
import os

sys.dont_write_bytecode = True
sys.path.append('./code/global_code/')
import global_function as af

data_path = './data/'
global_path = os.path.join(data_path, 'global')
ef_path = os.path.join(data_path, 'ef')
cm_path = os.path.join(data_path, '#global_rf')

file_name = af.search_file(data_path)
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
df_emission = df_all.copy()
for x in df_all.columns.tolist():
    # noinspection PyBroadException
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

# ################################################################# 计算排放因子 #############################################################
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

# ################################################################## 计算排放值 ##########################################
df_emission['date'] = pd.to_datetime(df_emission['date'])
df_emission = df_emission[['country', 'date', 'coal', 'gas', 'oil']]
df_emission['country'] = df_emission['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
df_emission['country'] = df_emission['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
df_emission['country'] = df_emission['country'].str.replace('Us', 'United States')

# 只要19年到22年3月底
# df_emission = df_emission[(df_emission['date'] >= '2019-01-01') & (df_emission['date'] < '2022-04-01')].reset_index(drop=True)  # 这句随时要改
df_emission = df_emission.set_index(['country', 'date']).stack().reset_index().rename(
    columns={'level_2': 'type', 0: 'value'})
df_emission['year'] = df_emission['date'].dt.year

# 添加欧盟
df_eu27 = df_emission[df_emission['country'].isin(eu27_list)].groupby(
    ['date', 'year', 'type']).sum().reset_index()
df_eu27['country'] = 'EU27&UK'
df_emission = pd.concat([df_emission, df_eu27]).reset_index(drop=True)
df_emission['value'] = df_emission['value'].astype(float)
# 读取排放因子
df_emission = pd.merge(df_emission, df_ef)
df_emission['emission'] = df_emission['value'] * df_emission['ef'] / 1000
df_emission = df_emission.groupby(['country', 'date']).sum().reset_index().drop(columns=['year', 'ef', 'value'])

# 读取CM数据做后续比较
df_cm = pd.read_csv(os.path.join(cm_path, 'cm', 'CM_v2021.11.csv'))
df_cm['country'] = df_cm['country'].replace('UK', 'United Kingdom')
df_cm['date'] = pd.to_datetime(df_cm['date'])
df_cm = df_cm[df_cm['sector'] == 'Power'].reset_index(drop=True)

df_result = pd.merge(df_emission, df_cm).rename(columns={'emission': 'PM', 'co2': 'CM'})
df_emission = pd.pivot_table(df_emission, index='date', values='emission', columns='country').reset_index()

df_result.to_csv(os.path.join(global_path, 'compare_CM.csv'), index=False, encoding='utf_8_sig')
df_emission.to_csv(os.path.join(global_path, 'Global_Power_Emission.csv'), index=False, encoding='utf_8_sig')
