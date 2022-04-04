#!/usr/bin/env python
# coding: utf-8

# ###############################备注########################################
# df_cleaned 时间列 = ['datetime','date','year','month','month_date','weekday','hour']
# df_simulated_hourly 时间列 = ['datetime','date','year','month','month_date','weekday','hour'] unit = ['Mwh']
# df_simulated_daily 时间列 = ['date','year','month','month_date','weekday'] unit = ['Gwh']
# df_simulated_monthly 时间列 = ['year','month'] unit = ['Gwh']
# ###########################function#########################################
def get_yesterday():
    import datetime
    yesterday = datetime.date.today() + datetime.timedelta(-1)
    return yesterday


def search_file(file_path):
    import os
    file_name = []
    for parent, dirnames, filenames in os.walk(file_path):
        for fn in filenames:
            file_name.append(os.path.join(parent, fn))
    return file_name


def xunlei(url, downpath):
    from win32com.client import Dispatch
    filename = url.split('/')[-1]
    thunder = Dispatch('ThunderAgent.Agent64.1')
    thunder.AddTask(url, filename, downpath)
    thunder.CommitTasks()


def lighten_color(color, amount=0.5):  # 改颜色深浅
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


def draw_pic(country):
    from matplotlib.dates import MonthLocator, DateFormatter
    from pylab import mpl
    import pandas as pd
    import matplotlib.pyplot as plt
    import re

    mpl.rcParams['font.sans-serif'] = ['SimHei']
    name = re.compile(r'data.*?\\.*?\\(?P<name>.*?)\\simulated', re.S)  # 从路径找出国家

    path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\'
    file_name = search_file(path)
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]

    df_all = pd.concat(pd.read_csv(f) for f in file_name if country == name.findall(f)[0])
    df_all = df_all.set_index(['date', 'year', 'month', 'month_date', 'weekday', 'unit']).stack().reset_index().rename(
        columns={'level_6': 'type', 0: 'value'})
    df_all = df_all.groupby(['date', 'year', 'month']).sum().reset_index()
    df_all = df_all[df_all['year'] >= 2019].reset_index(drop=True)
    df_all = df_all[:-1]  # 最后一天的数据一般都不准确

    file_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\image\\'
    out_path = create_folder(file_path, country)

    year_list = df_all['year'].drop_duplicates().tolist()
    n = 0.3
    color_pool = []
    for i in range(len(year_list)):
        color_pool.append(n)
        n += 0.4

    # 作图参数
    plt.figure(figsize=(10, 5))
    size_num = 20
    plt.title('Power generation between years for ' + country, size=size_num)
    plt.ylabel('Power generated (Gwh)', size=size_num)
    plt.xticks(size=size_num)
    plt.yticks(size=size_num)

    # 作图
    for d, p in zip(range(len(year_list)), color_pool):
        x = df_all[df_all['year'] == year_list[0]]['date'].tolist()
        y = df_all[df_all['year'] == year_list[d]]['value'].tolist()[0:len(x)]
        try:
            plt.plot(x, y, color=lighten_color('orange', p), linewidth=3, label=year_list[d])
        except:  # 如果长度不一致
            len_num = len(x) - len(y)
            y = y + [None] * len_num
            plt.plot(x, y, color=lighten_color('orange', p), linewidth=3, label=year_list[d])

        ax = plt.gca()  # 表明设置图片的各个轴，plt.gcf()表示图片本身
        ax.xaxis.set_major_locator(MonthLocator())
        ax.xaxis.set_major_formatter(DateFormatter('%b'))
        plt.legend(loc='best', prop={'size': size_num})
    plt.savefig(out_path + country + '_line_chart.png', dpi=500)


def write_pic(file_path, country):
    import matplotlib.pyplot as plt
    import os
    import pandas as pd
    import numpy as np
    iea = iea_data(country)
    result = []
    folder = os.listdir(file_path)
    for dbtype in folder[::]:
        if os.path.isfile(os.path.join(file_path, dbtype)):
            folder.remove(dbtype)
    for item in folder:
        d_file_path = os.path.join(file_path, item)
        file = os.listdir(d_file_path)
        file_name = []
        for dbtype in file:
            if os.path.isfile(os.path.join(d_file_path, dbtype)):
                file_name.append(dbtype)
        file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('monthly') != -1]
        df = pd.read_csv(d_file_path + file_name[0])
        result.append(df)
    df_all = pd.DataFrame(np.concatenate(result), columns=df.columns)
    df_all['date'] = pd.to_datetime(df_all[['year', 'month']].assign(Day=1))  # 合并年月
    iea['date'] = pd.to_datetime(iea[['year', 'month']].assign(Day=1))  # 合并年月
    date_list = sorted(list(set(df_all['date']) & set(iea['date'])))

    df_all = df_all.set_index('date').loc[date_list].reset_index()
    iea = iea.set_index('date').loc[date_list].reset_index()

    font_size = 25
    plt.figure(figsize=(25, 25))
    i = 1
    for z in df_all.columns.tolist():
        if z in iea.columns.tolist():
            if z != 'year' and z != 'month' and z != 'date':
                pic = plt.subplot(4, 2, i)
                pic.set_title('[' + str(i) + ']' + ' ' + z, size=font_size)
                i += 1
                x = df_all['date']
                y1 = df_all[z]
                y2 = iea[z]
                plt.plot(x, y1, color='red', label='simulated')
                plt.plot(x, y2, label='iea')
                # plt.tick_params(labelsize=font_size)
                plt.xlabel('Year', size=font_size)
                plt.ylabel('Emissions', size=font_size)
                plt.rcParams.update({'font.size': 15})
                pic.legend(loc=0)
                plt.tight_layout()
    plt.savefig('D:\\Python\\Work\\朱碧青\\Image_Store\\2022\\02-25\\' + country + '.png')


def create_folder(file_path, Type):  # 建立需要的文件夹
    import os
    out_path = os.path.join(file_path, Type + '\\')
    if not os.path.exists(out_path):  # 如果有了文件夹的话就直接pass掉
        os.mkdir(out_path)
    return out_path


def check_col(df, Type):  # 检查数据的现存列名是否一致 如果不一致就删掉多余的
    if Type == 'hourly':  # 如果是simulated_hourly
        r_col = ['unit', 'datetime', 'date', 'year', 'month', 'month_date', 'weekday', 'hour', 'coal', 'oil', 'gas',
                 'nuclear', 'hydro', 'wind', 'solar', 'other', 'fossil', 'low.carbon', 'total.prod', 'coal.perc',
                 'oil.perc', 'gas.perc', 'nuclear.perc', 'hydro.perc', 'wind.perc', 'solar.perc', 'other.perc',
                 'fossil.perc', 'low.carbon.perc']
        df['unit'] = 'Mwh'
    if Type == 'daily':
        r_col = ['unit', 'date', 'year', 'month', 'month_date', 'weekday', 'coal', 'oil', 'gas', 'nuclear', 'hydro',
                 'wind', 'solar', 'other', 'fossil', 'low.carbon', 'total.prod', 'coal.perc', 'oil.perc', 'gas.perc',
                 'nuclear.perc', 'hydro.perc', 'wind.perc', 'solar.perc', 'other.perc', 'fossil.perc',
                 'low.carbon.perc']
        df['unit'] = 'Gwh'
    if Type == 'monthly':
        r_col = ['unit', 'year', 'month', 'coal', 'oil', 'gas', 'nuclear', 'hydro', 'wind', 'solar', 'other', 'fossil',
                 'low.carbon', 'total.prod', 'coal.perc', 'oil.perc', 'gas.perc', 'nuclear.perc', 'hydro.perc',
                 'wind.perc', 'solar.perc', 'other.perc', 'fossil.perc', 'low.carbon.perc']
        df['unit'] = 'Gwh'
    df = df[r_col]
    return df


def time_b_a(x, which):  # 根据which 选择得到所选日期的前which天或者后which天
    import datetime
    myday = datetime.datetime.strptime(x, '%Y-%m-%d')
    delta = datetime.timedelta(days=which)
    my_yestoday = myday + delta
    my_yes_time = my_yestoday.strftime('%Y-%m-%d')
    return my_yes_time


def time_info(df, date_name):  # 添加各种时间列
    import pandas as pd
    df[date_name] = pd.to_datetime(df[date_name])
    df['year'] = df[date_name].dt.year
    df['month'] = df[date_name].dt.month
    df['month_date'] = df[date_name].dt.strftime('%m-%d')
    df['weekday'] = df[date_name].dt.day_name()
    df['hour'] = df[date_name].dt.hour
    if date_name != 'date':
        df['date'] = df[date_name].dt.strftime('%Y-%m-%d')


def check_date(df, date_name, f):  # 检查现存时间缺失值并填充
    import pandas as pd
    df[date_name] = pd.to_datetime(df[date_name])
    real_date = pd.date_range(start=min(df[date_name]), end=max(df[date_name]), freq=f).tolist()
    df_date = df[date_name].drop_duplicates().tolist()
    missing_date = list(set(real_date) - set(df_date))
    for z in missing_date:
        df = df.append([{date_name: z}], ignore_index=True)
        df = df.sort_values(by=date_name).reset_index(drop=True)
    time_info(df, date_name)
    return df


def insert_date(df, date_name, z):
    import pandas as pd
    df[date_name] = pd.to_datetime(df[date_name])
    df = df.append([{date_name: z}], ignore_index=True)
    df = df.sort_values(by=date_name).reset_index(drop=True)
    return df


def iea_data(j):
    import pandas as pd
    iea_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\#global_rf\\iea\\iea_all.csv'
    df_iea = pd.read_csv(iea_path)
    df_iea = df_iea[df_iea['country'] == j.capitalize()].reset_index(drop=True)
    return df_iea


# 填充缺失值
def fill_null(df, j, date_name, Type):
    import calendar
    import pandas as pd
    import numpy as np
    df_iea = iea_data(j)
    filling_result = []
    df_null = df[df.isna().any(axis=1)].reset_index(drop=True)  # 所有包含缺失值的行
    df_not_null = df[~df.isna().any(axis=1)].reset_index(drop=True)  # 所有不包含缺失值的行
    for x in df_null['year'].drop_duplicates().tolist():  # 按年份循环
        df_temp = df_null[df_null['year'] == x].reset_index(drop=True)  # 按年份赋值新的df
        for y in df_temp['month'].drop_duplicates().tolist():  # 新df中按月循环
            df_temp_month = df_temp[df_temp['month'] == y].reset_index(drop=True)  # 按月份赋值新的df
            month_date = calendar.monthrange(x, y)[1]  # 计算当月天数
            for z in df_iea.columns.tolist():
                if df_iea[z].dtype == float and z != 'total.gen':  # 如果这一列类型是float并且不为total时
                    try:  # 如果这一列类型是float并且不为total时
                        df_temp_month[z] = df_iea[(df_iea['year'] == x) & (df_iea['month'] == y)][z].tolist()[
                                               0] / month_date
                    except:
                        df_temp_month[z] = df_iea[(df_iea['year'] == x - 1) & (df_iea['month'] == y)][z].tolist()[
                                               0] / month_date
            filling_result.append(df_temp_month)
    df_missing = pd.DataFrame(np.concatenate(filling_result), columns=df_temp_month.columns)
    df = pd.concat([df_missing, df_not_null])
    df = df.sort_values(by=date_name).reset_index(drop=True)
    total_proc(df, unit=True)
    df = check_col(df, Type)
    return df


def total_proc(df, unit=True):  # 处理数据
    fossil_list = ['coal', 'gas', 'oil']
    carbon_list = ['nuclear', 'hydro', 'wind', 'solar', 'other']
    perc_list = ['fossil', 'low.carbon']
    df[fossil_list] = df[fossil_list].astype(float)
    df[carbon_list] = df[carbon_list].astype(float)
    df['fossil'] = df[fossil_list].astype(float).sum(axis=1)
    df['low.carbon'] = df[carbon_list].astype(float).sum(axis=1)
    df['total.prod'] = df[perc_list].astype(float).sum(axis=1)
    if unit == True:
        for z in df.columns.tolist():
            if df[z].dtype == float:
                df[z] = df[z] / 1000
    for y in df.columns.tolist():
        if df[y].dtype == float:
            if y != 'total.prod' and 'perc' not in y:
                df[y + '.perc'] = df[y] / df['total.prod']
    df['unit'] = 'Gwh'  # 补充单位


def agg(df, date_name, path, Type, name, folder, unit):  # 输出
    time_info(df, date_name)
    total_proc(df, unit)
    df = check_col(df, Type)
    if folder == True:
        out_path = create_folder(path, Type)
        out_file = out_path + name
    else:
        out_file = path + name
    df.to_csv(out_file, index=False, encoding='utf_8_sig')
