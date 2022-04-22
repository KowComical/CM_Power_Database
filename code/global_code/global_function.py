#!/usr/bin/env python
# coding: utf-8

# ###############################备注########################################
# df_cleaned 时间列 = ['datetime','date','year','month','month_date','weekday','hour']
# df_simulated_hourly 时间列 = ['datetime','date','year','month','month_date','weekday','hour'] unit = ['Mwh']
# df_simulated_daily 时间列 = ['date','year','month','month_date','weekday'] unit = ['Gwh']
# df_simulated_monthly 时间列 = ['year','month'] unit = ['Gwh']
# ###########################function#########################################
def japan_download_Csvformat(u, in_path, name, start_date):
    from datetime import datetime
    import urllib.request
    import pandas as pd
    import os
    file_n = search_file(in_path)
    file_n = [file_n[i] for i, x in enumerate(file_n) if x.find('.csv') != -1]
    date = []
    for file in file_n:
        date.append(name.findall(file)[0])
    if not date:
        start_date = start_date
    else:
        start_date = str(int(max(date)))
    if len(str(start_date)) == 4:  # 如果是年份
        end_date = datetime.now().strftime("%Y")
        for i in range(int(start_date), int(end_date) + 1):
            fileName = os.path.join(in_path, '%s.csv' % i)
            print(u % i)
            urllib.request.urlretrieve(u % i, fileName)
    else:
        end_date = datetime.now().strftime("%Y%m%d")
        for month in pd.date_range(start_date, end_date, freq='D'):
            dateRange = month.strftime('%Y%m%d')
            fileName = os.path.join(in_path, '%s.csv' % dateRange)
            if os.path.exists(fileName):
                continue
            print(u % dateRange)
            urllib.request.urlretrieve(u % dateRange, fileName)


def japan_download_Zipformat(u, in_path, name, start_date, freq):
    import os
    from datetime import datetime
    from tqdm import tqdm
    import pandas as pd
    from dateutil.relativedelta import relativedelta
    import urllib.request
    import zipfile
    file_n = search_file(in_path)
    file_n = [file_n[i] for i, x in enumerate(file_n) if x.find('.csv') != -1]
    date = []
    # 这里有一个bug
    # 比如 当数据更新到3月30日时 连着好几天没有更新数据 一直到4月17号才更新
    # 那么以下的代码会忽略3月31日的数据 而是直接更新4月的
    # 目前还未想到好的办法 因为目前的代码逻辑是start_date是遍历整个文件夹文件得到的日期最大值
    # 只能保持每日更新 要不跨月必少一天数据
    for file in file_n:
        date.append(name.findall(file)[0])
    if not date:
        start_date = start_date
    else:
        start_date = str(max(date))
    end_date = datetime.now().strftime("%Y%m%d")
    for month in tqdm(pd.date_range(start_date, end_date, freq=freq)):
        if freq == '3MS':
            dateRange = month.strftime('%Y%m') + '-' + (month + relativedelta(months=+2)).strftime('%m')
        if freq == 'MS':
            dateRange = month.strftime('%Y%m')

        fileName = os.path.join(in_path, '%s.zip' % dateRange)
        print(u % dateRange)
        urllib.request.urlretrieve(u % dateRange, fileName)
        zip_file = zipfile.ZipFile(fileName)
        zip_file.extractall(path=in_path)
        zip_file.close()

    # delete unused zip
    file_n = search_file(in_path)
    file_zip = [file_n[i] for i, x in enumerate(file_n) if x.find('.zip') != -1]
    for f in file_zip:
        os.remove(f)


def japan_extractData(in_path, out_path, name, directory, date, ty, first, second):
    import pandas as pd
    import os
    if ty == 'ez':
        file_n = search_file(in_path)
        file_n = [file_n[i] for i, x in enumerate(file_n) if x.find('.csv') != -1]
        df = pd.concat(pd.read_csv(f, header=1, encoding='Shift_JIS') for f in file_n)
        df.to_csv(os.path.join(out_path, '%s.csv' % directory), index=False, encoding='utf_8_sig')

    elif ty == 'so_ez':
        file_n = search_file(in_path)
        file_n = [file_n[i] for i, x in enumerate(file_n) if x.find('.csv') != -1]
        df = pd.concat(pd.read_csv(f, skiprows=13, nrows=24, encoding='Shift_JIS') for f in file_n)
        # df['供給力(万kW)'] = df[['供給力想定値(万kW)', '供給力(万kW)']].sum(axis=1)
        # df = df.drop(columns=['供給力想定値(万kW)'])
        df.to_csv(os.path.join(out_path, '%s.csv' % directory), index=False, encoding='utf_8_sig')
    else:
        result = pd.DataFrame()
        file_n = search_file(in_path)
        file_n = [file_n[i] for i, x in enumerate(file_n) if x.find('.csv') != -1]
        for f in file_n:
            if name.findall(f)[0] > date:
                df = pd.read_csv(f, skiprows=first, nrows=24, encoding='Shift_JIS')
            else:
                df = pd.read_csv(f, skiprows=second, nrows=24, encoding='Shift_JIS')
            result = pd.concat([result, df])
        result = result.dropna(axis=1, how='all')
        result.to_csv(os.path.join(out_path, '%s.csv' % directory), index=False, encoding='utf_8_sig')


def japan_path(company):
    import os
    # 输入路径
    in_path = './data/asia/japan/craw/%s' % company
    if not os.path.exists(in_path):
        os.mkdir(in_path)

    # 输出路径
    out_path = './data/asia/japan/raw/company/'
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    return in_path, out_path


def get_yesterday():
    import datetime
    yesterday = datetime.date.today() + datetime.timedelta(-1)
    return yesterday


def search_file(file_path):
    import os
    file_name = []
    for parent, surnames, filenames in os.walk(file_path):
        for fn in filenames:
            file_name.append(os.path.join(parent, fn))
    return file_name


def xunlei(url, down_path):
    from win32com.client import Dispatch
    filename = url.split('/')[-1]
    thunder = Dispatch('ThunderAgent.Agent64.1')
    thunder.AddTask(url, filename, down_path)
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
    import pandas as pd
    import matplotlib.pyplot as plt
    import re
    import os

    in_path = './data/'
    global_path = './data/global/'

    if country == 'eu27_uk':
        name = re.compile(r'daily/(?P<name>.*?).csv', re.S)  # 从路径找出国家
        file_name = search_file(in_path)
        file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
        file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
        file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('per_country') != -1]
        file_name = [file_name[i] for i, x in enumerate(file_name) if not x.find('United Kingdom.csv') != -1]

        df_all = pd.DataFrame()
        for f in file_name:
            c = name.findall(f)[0]
            if c == 'United_Kingdom_BMRS':
                c = 'United kingdom'
            df_temp = pd.read_csv(f)
            df_temp['country'] = c.capitalize()
            df_all = pd.concat([df_temp, df_all])

        df_c = pd.read_csv(os.path.join(global_path, 'EU_country_list.csv'))
        eu27_list = df_c['country'].tolist() + ['United kingdom']
        df_all = df_all[df_all['country'].isin(eu27_list)].reset_index(drop=True)
        df_all = df_all.set_index(
            ['country', 'date', 'year', 'month', 'month_date', 'weekday', 'unit']).stack().reset_index().rename(
            columns={'level_7': 'ty', 0: 'value'}).drop(columns=['month_date', 'weekday', 'unit'])
    else:
        file_name = search_file(in_path)
        file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('daily') != -1]
        file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('simulated') != -1]
        file_name = [file_name[i] for i, x in enumerate(file_name) if x.find(country) != -1]
        if country == 'us':  # russia 和 us名字有冲突
            file_name = [file_name[i] for i, x in enumerate(file_name) if not x.find('russia') != -1]
        df_all = pd.concat(pd.read_csv(f) for f in file_name)
        df_all = df_all.set_index(
            ['date', 'year', 'month', 'month_date', 'weekday', 'unit']).stack().reset_index().rename(
            columns={'level_6': 'ty', 0: 'value'}).drop(columns=['month_date', 'weekday', 'unit'])

    df_all['value'] = df_all['value'].astype(float)
    df_all = df_all[df_all['ty'] == 'total.prod'].reset_index(drop=True)
    df_all = df_all.groupby(['date', 'year', 'month']).sum().reset_index()
    df_all = df_all[df_all['year'] >= 2019].reset_index(drop=True)
    df_all = df_all[:-1]  # 最后一天的数据一般都不准确

    file_path = './image/'
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
    plt.savefig(os.path.join(out_path, '%s_line_chart.png' % country), dpi=500)


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
                plt.xlabel('Year', size=font_size)
                plt.ylabel('Emissions', size=font_size)
                plt.rcParams.update({'font.size': 15})
                pic.legend(loc=0)
                plt.tight_layout()
    plt.savefig('D:\\Python\\Work\\朱碧青\\Image_Store\\2022\\02-25\\' + country + '.png')


def create_folder(file_path, Type):  # 建立需要的文件夹
    import os
    out_path = os.path.join(file_path, Type + '/')
    if not os.path.exists(out_path):  # 如果有了文件夹的话就直接pass掉
        os.mkdir(out_path)
    return out_path


def check_col(df, Type):
    r_col = []  # 检查数据的现存列名是否一致 如果不一致就删掉多余的
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
    my_yesterday = myday + delta
    my_yes_time = my_yesterday.strftime('%Y-%m-%d')
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
    iea_path = '../../data/#global_rf/iea/iea_cleaned.csv'
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
    if unit:
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
    if folder:
        out_path = create_folder(path, Type)
        out_file = out_path + name
    else:
        out_file = path + name
    df.to_csv(out_file, index=False, encoding='utf_8_sig')
