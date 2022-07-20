from jupyterthemes import jtplot
import matplotlib.pyplot as plt
import pandas as pd
import re
import os
import calendar
from datetime import datetime
import sys


sys.dont_write_bytecode = True
sys.path.append('./code/global_code/')
import global_function as af

out_path = './image/'
country_list = ['Australia', 'Brazil', 'China', 'Russia', 'EU27&UK', 'France', 'Germany', 'India', 'Italy', 'Japan',
                'Spain',
                'United Kingdom', 'United States', 'South Africa', 'Chile', 'Mexico']  # 这里以后要修改

file_path = './data/'
global_path = os.path.join(file_path, 'global')


def main(category):
    df_all = data_process(category)
    draw_plt(df_all, category)
    out_put(category)


def data_process(category):
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
    # 只保留需要的列
    col_list = ['country', 'date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'wind', 'solar', 'other']
    df_all = df_all[col_list]

    # 统一命名
    df_all['country'] = df_all['country'].str.replace('United_kingdom_bmrs', 'United Kingdom')
    df_all['country'] = df_all['country'].str.replace('Bosnia and Herz', 'Bosnia & Herz')
    df_all['country'] = df_all['country'].str.replace('Us', 'United States')
    df_all['country'] = df_all['country'].str.replace('South_africa', 'South Africa')

    # 添加欧盟
    df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))

    eu27_list = df_c['country'].tolist() + ['United Kingdom']
    df_eu27 = df_all[df_all['country'].isin(eu27_list)].groupby(['date']).sum().reset_index()
    df_eu27['country'] = 'EU27&UK'
    df_all = pd.concat([df_all, df_eu27]).reset_index(drop=True)
    # 只保留需要的国家
    df_all = df_all[df_all['country'].isin(country_list)].reset_index(drop=True)
    # 从19年开始统计
    df_all['date'] = pd.to_datetime(df_all['date'])
    yesterday = af.get_yesterday().strftime('%Y-%m-%d')
    df_all = df_all[(df_all['date'] >= '2019-01-01') & (df_all['date'] < yesterday)].reset_index(drop=True)

    if category:  # 设置能源类型
        df_all = df_all[['country', 'date', category]]
    return df_all


def draw_plt(df_all, category):
    # plt.style.use('seaborn-poster')  # 图表风格
    jtplot.style(theme='solarizedl')
    fig = plt.figure(figsize=(100, 50), dpi=200)  # 设置图表大小
    if category:
        category_name = category
    else:
        category_name = 'power'
    num = [i for i in range(len(country_list))]
    for co, i in zip(country_list, num):
        pic = plt.subplot(4, 4, i + 1)
        # pic.text(0, 0.9, '%s_%s' % (co, category_name.capitalize()), horizontalalignment='left',
        #          transform=pic.transAxes, size=80,
        #          color='black')
        if i % 4 == 0:  # 如果能被4整除 也就是最左边一列
            plt.ylabel('Power generated (Gwh)', size=70)
        else:
            plt.ylabel('')
        test = df_all[df_all['country'] == co].reset_index(drop=True)
        test['year'] = test['date'].dt.year
        test['month_date'] = test['date'].dt.strftime('%m-%d')
        # 行转列
        test = test.drop(columns=['country', 'date']).set_index(['year', 'month_date']).stack().reset_index().rename(
            columns={'level_2': 'type', 0: 'gwh'})
        test = test.groupby(['year', 'month_date']).sum().reset_index()

        year_list = test['year'].drop_duplicates().tolist()
        n = 0.3
        color_pool = []
        for z in range(len(year_list)):  # 设置渐变颜色
            color_pool.append(n)
            n += 0.4

        month_list = []
        for t in test['month_date'].tolist():
            month_list.append(calendar.month_abbr[int(t[:2])])
        test['month'] = month_list
        test = pd.pivot_table(test, index=['month_date', 'month'], values='gwh', columns='year').reset_index()

        for y, c in zip(year_list, color_pool):
            if y == year_list[-1]:  # 最后一年改为黑色显示
                test.set_index('month_date')[y].plot(color='black', linewidth=8)
            else:
                test.set_index('month_date')[y].plot(color=af.lighten_color('orange', c), linewidth=8)
        plt.yticks(size=50)
        plt.xticks(size=60)
        plt.xlabel('')  # 不要x轴标签
        plt.title('%s_%s' % (co, category_name.capitalize()), size=80)
        if i == 0:
            plt.legend(loc='best', prop={'size': 50})
        else:
            plt.legend('')
        # for axis in ['top', 'bottom', 'left', 'right']:
        #     pic.spines[axis].set_linewidth(4)  # change width
        #     pic.spines[axis].set_color('red')  # change color
    fig.tight_layout()


def out_put(category):
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
        plt.savefig(os.path.join(out_path, '%s_generation_for_all_country.svg' % category.capitalize()),
                    format='svg')
