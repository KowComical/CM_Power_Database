from matplotlib.dates import MonthLocator, DateFormatter
import matplotlib.pyplot as plt
import pandas as pd
import re
import os
from datetime import datetime
import seaborn as sns
sns.set()

import sys


sys.dont_write_bytecode = True
sys.path.append('./code/global_code/')
import global_function as af


def main(category):
    out_path = './image/'
    country_list = ['Brazil', 'China', 'Russia', 'EU27&UK', 'France', 'Germany', 'India', 'Italy', 'Japan', 'Spain',
                    'United Kingdom', 'United States', 'South Africa']  # 这里以后要修改
    df_all = sum_country(country_list, category)  # 合并数据

    # plt.style.use('seaborn-poster')  # 图表风格
    plt.figure(figsize=(100, 50),dpi=200)  # 设置图表大小
    # plt.figure(figsize=(18, 24),dpi=200)  # 设置图表大小

    sub_plot(df_all, country_list)  # 开始画图

    out_put(out_path, category)  # 输出图


def sum_country(country_list, category):
    file_path = './data/'
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
    df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
    df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
    df_all['country'] = df_all['country'].str.replace('Us', 'United States')
    df_all['country'] = df_all['country'].str.replace('South_africa', 'South Africa')

    # 前一天的数据基本都不准确
    yesterday = af.get_yesterday().strftime('%Y-%m-%d')
    df_all = df_all[df_all['date'] < yesterday].reset_index(drop=True)

    df_all = df_all[['date', 'country', 'Type', 'Value']]

    if not category:
        df_all = df_all.groupby(['date', 'country']).sum().reset_index()
        df_all['Type'] = 'All'
    else:
        df_all = df_all[df_all['Type'] == category].reset_index(drop=True)
    df_all = df_all.rename(columns={'country': 'country/region', 'Type': 'energy_source', 'Value': 'value'})

    # 添加欧盟
    df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))

    eu27_list = df_c['country'].tolist() + ['United Kingdom']
    df_eu27 = df_all[df_all['country/region'].isin(eu27_list)].groupby(
        ['date', 'energy_source']).sum().reset_index()
    df_eu27['country/region'] = 'EU27&UK'
    df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)

    df_all = df_all.groupby(['country/region', 'date']).sum().reset_index()
    df_all = pd.pivot_table(df_all, index='date', values='value', columns='country/region').reset_index()

    df_all = df_all[['date'] + country_list]
    df_all = df_all[df_all['date'] >= '2019-01-01'].reset_index(drop=True)
    df_all['year'] = df_all['date'].dt.year
    df_all['month'] = df_all['date'].dt.month
    return df_all


def draw_pic(df_all, c, i):
    # 开始画图
    year_list = df_all['year'].drop_duplicates().tolist()
    n = 0.3
    color_pool = []
    for z in range(len(year_list)):  # 设置渐变颜色
        color_pool.append(n)
        n += 0.4
    # plt.style.use('seaborn')

    plt.title(c, size=70)
    if i % 4 == 0:  # 如果能被4整除 也就是最左边一列
        plt.ylabel('Power generated (Gwh)', size=70)
    else:
        plt.ylabel('')

    for d, p in zip(range(len(year_list)), color_pool):
        x = df_all[df_all['year'] == year_list[0]]['date'].tolist()
        y = df_all[df_all['year'] == year_list[d]][c].tolist()[0:len(x)]
        if 'frica' in c:  # 有的时候南非最后一天数据不完全
            x = x[:-1]
            y = y[:-1]
        # noinspection PyBroadException
        try:
            plt.plot(x, y, color=af.lighten_color('orange', p), linewidth=8, label=year_list[d])
        except:  # 如果长度不一致
            len_num = len(x) - len(y)
            y = y + [None] * len_num
            plt.plot(x, y, color=af.lighten_color('grey', p), linewidth=8, label=year_list[d])
    ax = plt.gca()  # 表明设置图片的各个轴，plt.gcf()表示图片本身
    ax.xaxis.set_major_locator(MonthLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    plt.legend(loc='best', prop={'size': 50})
    plt.yticks(size=40)
    if i <= 7:  # 这里以后要修改
        plt.xticks(())
    else:
        plt.xticks(size=60)


def sub_plot(df_all, country_list):
    for i in range(len(country_list)):
        plt.subplot(4, 4, i + 1)  # 第一个是列 第二个是行
        draw_pic(df_all, country_list[i], i)
    plt.tight_layout()


def out_put(out_path, category):
    current_date = datetime.now().strftime('%Y%m%d')
    if not category:  # 全部的情况
        out_path_energy = af.create_folder(out_path, 'all')
        out_path_type = af.create_folder(out_path_energy, 'power')
        out_path_yearly = af.create_folder(out_path_type, current_date[:4])
        out_path_monthly = af.create_folder(out_path_yearly, current_date[4:6])

        plt.savefig(os.path.join(out_path_monthly, 'Power_generation_for_all_country_%s.svg' % current_date),
                    format='svg')
        # readme也需要一个
        plt.savefig(os.path.join(out_path, 'Power_generation_for_all_country.svg'), format='svg')
    else:
        out_path_energy = af.create_folder(out_path, 'all')
        out_path_type = af.create_folder(out_path_energy, category)
        out_path_yearly = af.create_folder(out_path_type, current_date[:4])
        out_path_monthly = af.create_folder(out_path_yearly, current_date[4:6])

        plt.savefig(os.path.join(out_path_monthly, 'Power_generation_for_all_country_%s.svg' % current_date),
                    format='svg')
        plt.savefig(os.path.join(out_path, '%s_generation_for_all_country.svg' % category.capitalize()), format='svg')
