import pandas as pd
import re
import os
import matplotlib.pyplot as plt

import sys

sys.dont_write_bytecode = True
sys.path.append('K:\\Github\\CM_Power_Database\\code\\global_code\\')
import global_function as af

country_list = ['Australia', 'Brazil', 'China', 'Russia', 'EU27&UK', 'France', 'Germany', 'India', 'Italy', 'Japan',
                'Spain',
                'United Kingdom', 'United States', 'South Africa', 'Chile', 'Mexico']

needed_name = 'United States'


def main(needed_name):
    compare_pic(needed_name)


def compare_pic(needed_name):
    file_path = 'K:\\Github\\CM_Power_Database\\data\\'
    global_path = os.path.join(file_path, 'global')

    file_name = af.search_file(file_path)
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
    file_name_no = [file_name[i] for i, x in enumerate(file_name) if not x.find('eu27_uk') != -1]
    file_name_eu = [file_name[i] for i, x in enumerate(file_name) if x.find('eu27_uk') != -1]
    file_name_eu = [file_name_eu[i] for i, x in enumerate(file_name_eu) if not x.find('United Kingdom') != -1]

    # 提取主要国家名
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

    df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
    df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
    df_all['country'] = df_all['country'].str.replace('Us', 'United States')
    df_all['country'] = df_all['country'].str.replace('South_africa', 'South Africa')

    df_all['date'] = pd.to_datetime(df_all['date'])
    yesterday = af.get_yesterday().strftime('%Y-%m-%d')
    df_all = df_all[(df_all['date'] >= '2019-01-01') & (df_all['date'] < yesterday)].reset_index(drop=True)
    df_all = df_all[['country', 'date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']]

    # 添加欧盟
    df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))

    eu27_list = df_c['country'].tolist() + ['United Kingdom']
    df_eu27 = df_all[df_all['country'].isin(eu27_list)].groupby(['date']).sum().reset_index()
    df_eu27['country'] = 'EU27&UK'
    df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)
    # 只保留需要的国家
    df_all = df_all[df_all['country'].isin(country_list)].reset_index(drop=True)
    # 找到需要的国家
    df_all = df_all[df_all['country'] == needed_name].reset_index(drop=True)
    min_date = min(df_all['date']).strftime('%Y-%m-%d')
    # 行转列
    df_all = df_all.set_index(['date', 'country']).stack().reset_index().rename(
        columns={'level_2': 'sector', 0: 'CM_Power'})
    df_all = df_all.set_index('date')

    # iea
    df_iea = pd.read_csv(r'K:\Github\CM_Power_Database\data\#global_rf\iea\iea_daily.csv')
    # bp
    df_bp = pd.read_csv(r'K:\Github\CM_Power_Database\data\#global_rf\bp\bp_daily.csv')

    # 从iea或者bp中找到对应国家
    if df_iea[df_iea['country'].str.contains(needed_name)].empty:  # 如果iea里没有
        df_compare = df_bp[df_bp['country'].str.contains(needed_name)].reset_index(drop=True)
    else:
        df_compare = df_iea[df_iea['country'].str.contains(needed_name)].reset_index(drop=True).rename(
            columns={'type': 'sector'})
    df_compare['date'] = pd.to_datetime(df_compare['date'])
    df_compare = df_compare[df_compare['date'] >= min_date].reset_index(drop=True)
    df_compare = df_compare.set_index('date')
    compare_name = df_compare.columns[-1]

    # 开始画图
    sector_list = df_all['sector'].unique()
    fig = plt.figure(figsize=(100, 50), facecolor='w')
    num = [i for i in range(1, len(sector_list) + 1)]
    for c, i in zip(sector_list, num):
        pic = plt.subplot(4, 2, i)
        pic.set_title(c, size=80)
        df_compare[df_compare['sector'] == c][compare_name].plot(linewidth=8, color='tab:blue', alpha=0.8)
        df_all[df_all['sector'] == c]['CM_Power'].plot(linewidth=8, color='tab:red', alpha=0.8)
        plt.legend(['%s_%s' % (compare_name, c), 'CM_Power_%s' % c], loc='best', prop={'size': 60})
        plt.xticks(size=60)
        plt.yticks(size=60)
        plt.ylabel('Power generation (Gwh)', size=60)
        plt.xlabel('', size=60)
    # 防止图都叠在一起
    fig.tight_layout()
    fig.savefig(
        r'K:\Github\Python\Work\朱碧青\Image_Store\2022\07-26\compare_%s_with_%s.svg' % (needed_name, compare_name),
        format='svg')


if __name__ == '__main__':
    main(needed_name)
