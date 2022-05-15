import pandas as pd
import re
import global_function as af
import os

file_path = '../../data/'
global_path = os.path.join(file_path, 'global')

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
df_all = df_all[df_all['Type'].isin(['coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other'])].reset_index(
    drop=True)
df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
df_all['country'] = df_all['country'].str.replace('Us', 'United States')

# col_list = ['date', 'year', 'country', 'Type', 'Value']
# yesterday = af.get_yesterday().strftime('%Y-%m-%d')
# df_pic = df_pic[df_pic['date'] < yesterday].reset_index(drop=True)
# df_pic['year'] = df_pic['date'].dt.year
df_all = pd.pivot_table(df_all, index=['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'country'],
                        values='Value', columns='Type').reset_index()
#
# df_pic = df_pic[
#     (df_pic['year'] == 2021) & (df_pic['month'] == 12)].reset_index(drop=True)
#
df_all = df_all[['country', 'date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']]
df_all = df_all.set_index(['country', 'date']).stack().reset_index().rename(
    columns={'Type': 'energy_source', 0: 'value', 'country': 'country/region'})
#
# 添加欧盟
df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))

eu27_list = df_c['country'].tolist() + ['United Kingdom']
df_eu27 = df_all[df_all['country/region'].isin(eu27_list)].groupby(
    ['date', 'energy_source']).sum().reset_index()
df_eu27['country/region'] = 'EU27&UK'
df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)

df_all = df_all.groupby(['country/region', 'date']).sum().reset_index()
df_all = pd.pivot_table(df_all, index='date', values='value', columns='country/region').reset_index()
df_all = df_all[
    ['date', 'Brazil', 'China', 'Russia', 'EU27&UK', 'France', 'Germany', 'India', 'Italy', 'Japan', 'Spain',
     'United Kingdom', 'United States']]
df_all = df_all[(df_all['date'] >= '2019-01-01') & (df_all['date'] < '2022-04-01')].reset_index(drop=True)
# # 只要6个国家
# country_list = ['India', 'United States', 'EU27&UK', 'United Kingdom', 'Brazil', 'China', 'Japan']
# df_pic = df_pic[df_pic['country/region'].isin(country_list)].reset_index(drop=True)
# # df_t = df_pic.groupby(['date', 'energy_source']).sum().reset_index()
# # df_t['country/region'] = 'Total'
# # df_pic = pd.concat([df_pic, df_t])
#
# time_stamp = []  # 将当地时间转换为时间戳
# for d in df_pic['date'].tolist():
#     time_stamp.append(time.mktime(d.timetuple()))
# df_pic['timestamp'] = time_stamp
#
# utc_time = []  # 将当地时间时间戳转换为utc时间
# for t in df_pic['timestamp'].tolist():
#     utc_time.append(datetime.fromtimestamp(t, tz=timezone.utc))
# df_pic['utc'] = utc_time
#
# time_stamp = []  # 将utc时间转换为utc时间戳
# for d in df_pic['utc'].tolist():
#     time_stamp.append(time.mktime(d.timetuple()))
# df_pic['timestamp'] = time_stamp
# df_pic = df_pic[['country/region', 'date', 'energy_source', 'value', 'timestamp']]
# df_pic['date'] = df_pic['date'].dt.strftime('%d/%m/%Y')
#
df_all.to_csv(
    global_path + 'Global_Power_2022.4.26.csv', index=False,
    encoding='utf_8_sig')
