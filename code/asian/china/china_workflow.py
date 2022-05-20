import requests
import pandas as pd
import re
import os
import functools
import numpy as np

import sys
sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af
from global_code import global_all as g


# ##################################################### craw 部分 ######################################################################
def main():
    out_path = './data/asia/china/craw/'
    out_file = os.path.join(out_path, 'manually.csv')
    url = 'https://cec.org.cn/ms-mcms/mcms/content/search'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) ''AppleWebKit/605.1.15 (KHTML, like Gecko) ''Version/12.0 Safari/605.1.15'}
    keyvalue = {'keyword': '月份电力工业运行简况', 'pageNumber': 1, 'pageSize': 200}

    s = requests.session()
    r = s.get(url, params=keyvalue, headers=headers, verify=False)
    result = pd.json_normalize(r.json()['data']['list'])  # 将结果保留到df
    # 数据预处理
    result['basicTitle'] = result['basicTitle'].str.replace('</span>', '').str.replace('<span>', '').str.replace(
        '\u3000',
        '').str.replace(
        '中电联发布', '').str.replace('图表', '').str.replace('中电联公布', '').str.replace('[(]', '', regex=True).str.replace(
        '[)]',
        '',
        regex=True)
    result['url'] = 'https://cec.org.cn/ms-mcms/mcms/content/detail?id=' + result['articleID'].astype(str)
    result['source'] = 'https://cec.org.cn/detail/index.html?' + result['newType'].astype(str) + '-' + result[
        'articleID'].astype(str)
    result = result[['basicTitle', 'url', 'source']]  # 只保留需要的列
    result = result[~result.duplicated(['basicTitle'])].reset_index(drop=True)  # 删除重复的新闻
    # 筛选有用的新闻数据
    result_list = result['basicTitle'].tolist()
    result_list = [result_list[i] for i, x in enumerate(result_list) if x.find('月份电力工业运行简况') != -1]
    result = result[result['basicTitle'].isin(result_list)].reset_index(drop=True)

    date = []
    year = re.compile(r'\d{4}', re.S)  # 只保留四位数字 也就是年份
    month = re.compile(r'-(?P<name>.*?)月', re.S)  # 保留月份
    # 提取年月信息
    for b in result['basicTitle']:
        year_data = year.findall(b)[0]
        month_data = month.findall(b)[0]
        date.append('%s-%s' % (year_data, month_data))
    result['date'] = date
    result['date'] = pd.to_datetime(result['date']).astype(str)

    # 去掉已经爬取过的
    file_name = af.search_file(out_path)
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('power') != -1]
    name = re.compile(r'power/(?P<name>.*?).csv', re.S)

    exist_list = []
    for f in file_name:
        exist_list.append(name.findall(f)[0])

    result = result[~result['date'].isin(exist_list)].reset_index(drop=True)

    # 抓取数据
    title_list = result['date'].tolist()
    url_list = result['url'].tolist()
    source_list = result['source'].tolist()

    sector_list = ['水电', '火电', '燃煤发电', '燃气发电', '核电', '风电', '太阳能发电', '生物质发电', '地热发电']

    # 建立两个储存数据的df
    df_power_all = pd.DataFrame()
    df_hour_all = pd.DataFrame()

    # 开始爬取
    for t, u, s in zip(title_list, url_list, source_list):
        r = requests.get(u, headers=headers, verify=False)
        text = r.json()['data']['articleContent']

        # 发电
        data = []
        sector = []
        for se in sector_list:
            power = re.compile(r'截至.*?%s(?P<name>.*?)千瓦' % se, re.S)
            # noinspection PyBroadException
            try:
                result_data = power.findall(text)[0]
                if 0 <= len(result_data) <= 8:
                    data.append(result_data + '千瓦')
                    sector.append(se)
                else:
                    data.append('')
                    sector.append(se)
            except:
                data.append('')
                sector.append(se)
        df_power = pd.concat([pd.DataFrame(data, columns=['power']), pd.DataFrame(sector, columns=['sector'])], axis=1)
        df_power['source'] = s
        df_power['date'] = t
        df_power.to_csv(os.path.join(out_path, 'power', '%s.csv' % t), encoding='utf_8_sig', index=False)
        df_power_all = pd.concat([df_power_all, df_power]).reset_index(drop=True)
        # 利用小时
        data = []
        sector = []
        for se in sector_list:
            hour = re.compile(r'%s.*?利用小时.*?(?P<name>.*?)小时' % se, re.S)
            # noinspection PyBroadException
            try:
                result_data = hour.findall(text)
                result_data = functools.reduce(lambda x, z: x if len(x) < len(z) else z, result_data)
                if 0 <= len(result_data) <= 8:
                    data.append(result_data)
                    sector.append(se)
            except:
                pass
        df_hour = pd.concat([pd.DataFrame(data, columns=['hour']), pd.DataFrame(sector, columns=['sector'])], axis=1)
        df_hour['source'] = s
        df_hour['date'] = t
        df_hour.to_csv(os.path.join(out_path, 'hour', '%s.csv' % t), encoding='utf_8_sig', index=False)
        df_hour_all = pd.concat([df_hour_all, df_hour]).reset_index(drop=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) ''AppleWebKit/605.1.15 (KHTML, like Gecko) ''Version/12.0 Safari/605.1.15'}
    keyvalue = {'keyword': '年度全国电力供需', 'pageNumber': 1, 'pageSize': 200}

    s = requests.session()
    r = s.get(url, params=keyvalue, headers=headers, verify=False)
    result = pd.json_normalize(r.json()['data']['list'])  # 将结果保留到df
    result['basicTitle'] = result['basicTitle'].str.replace('</span>', '').str.replace('<span>', '').str.replace(
        '\u3000',
        '').str.replace(
        '中电联发布', '').str.replace('图表', '').str.replace('中电联公布', '').str.replace('[(]', '', regex=True).str.replace(
        '[)]',
        '',
        regex=True)
    result = result[result['basicTitle'].str.contains('年度全国电力供需形势分析预测报告')].reset_index(drop=True)
    result = result[~result['categoryName'].str.contains('新闻')].reset_index(drop=True)

    result['date'] = result['basicTitle'].str.extract('(\d+)', expand=False) + '-12-01'
    result = result[~result.duplicated(['date'])].reset_index(drop=True)  # 删除重复的新闻
    result['url'] = 'https://cec.org.cn/ms-mcms/mcms/content/detail?id=' + result['articleID'].astype(str)
    result['source'] = 'https://cec.org.cn/detail/index.html?' + result['newType'].astype(str) + '-' + result[
        'articleID'].astype(str)
    result = result[['date', 'url', 'source']]  # 只保留需要的列

    # 去掉已经爬取过的
    file_name = af.search_file(out_path)
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('power') != -1]
    name = re.compile(r'power/(?P<name>.*?).csv', re.S)

    exist_list = []
    for f in file_name:
        exist_list.append(name.findall(f)[0])

    result = result[~result['date'].isin(exist_list)].reset_index(drop=True)

    # 抓取数据
    title_list = result['date'].tolist()
    url_list = result['url'].tolist()
    source_list = result['source'].tolist()

    for t, u, s in zip(title_list, url_list, source_list):
        r = requests.get(u, headers=headers, verify=False)
        text = r.json()['data']['articleContent']

        # 发电
        data = []
        sector = []
        sector_list = ['水电', '火电', '煤电', '燃气发电', '核电', '风电', '太阳能发电', '生物质发电', '地热发电']
        for se in sector_list:
            power = re.compile(r'全口径.*?截至.*?%s(?P<name>.*?)千瓦' % se, re.S)
            # noinspection PyBroadException
            try:
                result_data = power.findall(text)[0]
                if 0 <= len(result_data) <= 10:  # 抓取失败时直接pass
                    data.append(result_data + '千瓦')
                    sector.append(se)
                else:
                    data.append('')
                    sector.append(se)
            except:
                data.append('')
                sector.append(se)
        df_power = pd.concat([pd.DataFrame(data, columns=['power']), pd.DataFrame(sector, columns=['sector'])], axis=1)
        df_power['source'] = s
        df_power['date'] = t
        df_power['sector'] = df_power['sector'].str.replace('煤电', '燃煤发电')
        df_power.to_csv(os.path.join(out_path, 'power', '%s.csv' % t), encoding='utf_8_sig', index=False)
        df_power_all = pd.concat([df_power_all, df_power]).reset_index(drop=True)
        # 利用小时
        data = []
        sector = []
        sector_list = ['水电', '火电', '煤电', '气电', '核电', '风电', '太阳能发电', '生物质发电', '地热发电']
        for se in sector_list:
            hour = re.compile(r'%s(?P<name>(\d+))小时' % se, re.S)
            # noinspection PyBroadException
            try:
                result_data = hour.findall(text)
                result_data = functools.reduce(lambda x, z: x if len(x) < len(z) else z, result_data)[0]
                if 0 <= len(result_data) <= 10:
                    data.append(result_data)
                    sector.append(se)
            except:
                pass
        df_hour = pd.concat([pd.DataFrame(data, columns=['hour']), pd.DataFrame(sector, columns=['sector'])], axis=1)
        df_hour['source'] = s
        df_hour['date'] = t
        df_hour['sector'] = df_hour['sector'].str.replace('煤电', '燃煤发电').str.replace('气电', '燃气发电')
        df_hour.to_csv(os.path.join(out_path, 'hour', '%s.csv' % t), encoding='utf_8_sig', index=False)
        df_hour_all = pd.concat([df_hour_all, df_hour]).reset_index(drop=True)
    # 如果没有更新的数据 则处理现有的
    if not df_hour_all.empty:  # 如果数据更新了
        # 添加单位
        unit = []
        df_power_all['power'] = df_power_all['power'].astype(str)
        for p in df_power_all['power'].tolist():
            if '亿' in p:
                unit.append('亿千瓦')
            elif '万' in p:
                unit.append('万千瓦')
            else:
                unit.append(p)
        df_power_all['unit'] = unit
        df_power_all['power'] = df_power_all['power'].astype(str).str.extract('(-?\d+\.?\d*e?-?\d*?)',
                                                                              expand=False).astype(
            float)  # 将数据行只保留数据
        df_hour_all['hour'] = df_hour_all['hour'].astype(str).str.extract('(-?\d+\.?\d*e?-?\d*?)', expand=False).astype(
            float)  # 将数据行只保留数据
        # 将单位统一为亿万瓦
        power = []
        power_list = df_power_all['power'].tolist()
        unit_list = df_power_all['unit'].tolist()
        for p, u in zip(power_list, unit_list):
            if u == '亿千瓦':
                power.append(p)
            elif u == '万千瓦':
                power.append(p / 10000)
            else:
                power.append(np.nan)
        df_power_all['power'] = power

        df_all = pd.merge(df_power_all, df_hour_all, how='left').fillna(0)

        # 将手动版输出
        df_man = pd.pivot_table(df_all, index=['date', 'source'], values=['power', 'hour'],
                                columns='sector').reset_index().replace(0, '')
        if os.path.exists(out_file):
            df_man.to_csv(out_file, mode='a', header=False, index=False, encoding='utf_8_sig')
        else:
            df_man.to_csv(out_file, index=False, encoding='utf_8_sig')

    # #################################################### craw to raw 部分 ######################################################################
    # 路径
    iea_path = os.path.join('./data/', '#global_rf', 'iea')
    raw_path = os.path.join('./data/', 'asia', 'china', 'raw')
    # 数据预处理
    df_raw = pd.read_csv(out_file, header=1)
    df_raw = df_raw.dropna(axis=0, how='all', thresh=2).reset_index(drop=True)  # 非空值小于2时删除行
    df_raw = df_raw.rename(columns={'Unnamed: 0': 'date'}).drop(columns=['Unnamed: 1'])
    # 分开发电和利用小时
    df_power = df_raw.loc[:, df_raw.columns.str.contains('.1', case=False)].reset_index(drop=True)
    df_power = pd.concat([df_raw['date'], df_power], axis=1)
    df_power['date'] = pd.to_datetime(df_power['date'])
    df_hour = df_raw.loc[:, ~df_raw.columns.str.contains('.1', case=False)].reset_index(drop=True)
    df_hour['date'] = pd.to_datetime(df_hour['date'])
    df_hour['year'] = df_hour['date'].dt.year
    # 统一列名
    df_hour = df_hour.rename(
        columns={'太阳能发电': 'solar', '核电': 'nuclear', '水电': 'hydro', '火电': 'fossil', '燃气发电': 'gas', '燃煤发电': 'coal',
                 '风电': 'wind', '地热发电': 'geothermal', '生物质发电': 'biomass'})
    df_power = df_power.rename(
        columns={'太阳能发电.1': 'solar', '核电.1': 'nuclear', '水电.1': 'hydro', '火电.1': 'fossil', '燃气发电.1': 'gas',
                 '燃煤发电.1': 'coal', '风电.1': 'wind', '地热发电.1': 'geothermal', '生物质发电.1': 'biomass'})

    # 填补缺失值
    df_power = df_power.set_index('date').interpolate(method='linear', limit_direction='backward').reset_index()
    df_hour = df_hour.set_index('date').interpolate(method='linear', limit_direction='backward').reset_index()

    # 处理利用小时数据
    df_result = pd.DataFrame()
    for y in df_hour['year'].drop_duplicates().tolist():
        df_temp = df_hour[df_hour['year'] == y].reset_index(drop=True)
        for i in range(len(df_temp)):
            if i == 0:
                df_temp_t = pd.DataFrame([df_temp.iloc[i]])
            else:
                df_temp_t = pd.DataFrame([df_temp.iloc[i] - df_temp.iloc[i - 1]])
            df_result = pd.concat([df_result, df_temp_t]).reset_index(drop=True)
    df_result['date'] = df_hour['date']
    df_result = df_result.drop(columns=['year'])
    df_hour = df_result.set_index(['date']).stack().reset_index().rename(columns={'level_1': 'type', 0: 'hour'})
    df_power = df_power.set_index(['date']).stack().reset_index().rename(columns={'level_1': 'type', 0: 'power'})

    # 发电*利用小时
    df_gwh = pd.merge(df_power, df_hour, how='left')
    df_gwh['gwh'] = df_gwh['power'] * df_gwh['hour'] * 100
    df_gwh['year'] = df_gwh['date'].dt.year
    # 生成一个数据年度范围
    year_list = df_gwh['year'].drop_duplicates().tolist()
    df_gwh = df_gwh[['date', 'type', 'gwh']]
    df_gwh = pd.pivot_table(df_gwh, index='date', values='gwh', columns='type').reset_index()

    # iea 数据
    df_iea = pd.read_csv(os.path.join(iea_path, 'iea_china.csv'))
    df_iea = df_iea[df_iea['country'].str.contains('China')].reset_index(drop=True)
    df_iea['date'] = pd.to_datetime(df_iea[['year', 'month']].assign(Day=1))  # 合并年月
    # oil平均占比
    df_iea['oil_ratio'] = df_iea['oil'] / (df_iea['oil'] + df_iea['other'])

    # 只保留需要的列
    df_ratio = df_iea[['date', 'oil_ratio']]

    col_list = ['date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'wind', 'solar', 'other']
    df_iea = df_iea[col_list]

    df_gwh = pd.merge(df_gwh, df_ratio, how='left')
    df_gwh['oil_ratio'] = df_gwh['oil_ratio'].fillna(method='ffill').fillna(method='bfill')
    # 计算gwh的oil数据
    df_gwh['oil'] = df_gwh['oil_ratio'] * (df_gwh['fossil'] - df_gwh['coal'] - df_gwh['gas'])
    # 计算gwh的other数据
    df_gwh['other'] = df_gwh['fossil'] - df_gwh['coal'] - df_gwh['gas'] - df_gwh['oil']

    df_gwh = df_gwh.drop(columns=['fossil', 'oil_ratio'])

    df_gwh = df_gwh.set_index(['date']).stack().reset_index().rename(columns={'level_1': 'type', 0: 'gwh'})
    df_gwh['date'] = df_gwh['date'].dt.strftime('%Y-%m')
    df_gwh = pd.pivot_table(df_gwh, index='type', values='gwh', columns='date').reset_index()

    df_iea = df_iea.set_index(['date']).stack().reset_index().rename(columns={'level_1': 'type', 0: 'gwh'})
    df_iea['date'] = df_iea['date'].dt.strftime('%Y-%m')
    df_iea = pd.pivot_table(df_iea, index='type', values='gwh', columns='date').reset_index()

    # 填补缺失的1月数据
    for y in year_list:  # gwh的年度范围
        if y <= 2015:
            col_name = str(2015) + '-01'
            col_ratio_name = str(2015) + '-02'
            missing_data = df_iea[col_name] / (df_iea[col_name] + df_iea[col_ratio_name])
            if col_name not in df_gwh.columns:
                df_gwh[col_name] = df_gwh[col_ratio_name] * missing_data
                df_gwh[col_ratio_name] = df_gwh[col_ratio_name] - df_gwh[col_name]
        else:
            # noinspection PyBroadException
            try:
                col_name = str(y) + '-01'
                col_ratio_name = str(y) + '-02'
                missing_data = df_iea[col_name] / (df_iea[col_name] + df_iea[col_ratio_name])
                if col_name not in df_gwh.columns:
                    df_gwh[col_name] = df_gwh[col_ratio_name] * missing_data
                    df_gwh[col_ratio_name] = df_gwh[col_ratio_name] - df_gwh[col_name]
            except:
                col_name = str(y) + '-01'
                col_ratio_name = str(y) + '-02'
                missing_data = df_iea[str(y - 1) + '-01'] / (df_iea[str(y - 1) + '-01'] + df_iea[str(y - 1) + '-02'])
                if col_name not in df_gwh.columns:
                    df_gwh[col_name] = df_gwh[col_ratio_name] * missing_data
                    df_gwh[col_ratio_name] = df_gwh[col_ratio_name] - df_gwh[col_name]

    df_gwh = df_gwh.set_index(['type']).stack().reset_index().rename(columns={'level_1': 'date', 0: 'gwh'})
    # 处理缺失值和异常值
    df_gwh = df_gwh.replace(0, np.nan)
    index = df_gwh[df_gwh['gwh'] <= 0].index.tolist()
    for i in index:
        df_gwh.loc[i, 'gwh'] = np.nan
    df_gwh = pd.pivot_table(df_gwh, index='date', values='gwh', columns='type').reset_index()
    df_gwh = df_gwh.fillna(method='ffill').fillna(method='bfill')
    df_gwh = df_gwh[df_gwh['date'] >= '2022-01'].reset_index(drop=True)

    # 输出
    df_gwh['date'] = pd.to_datetime(df_gwh['date'])
    df_gwh['year'] = df_gwh['date'].dt.year
    year_list = df_gwh['year'].drop_duplicates().tolist()
    for y in year_list:
        df_temp = df_gwh[df_gwh['year'] == y].reset_index(drop=True)
        af.agg(df_temp, 'date', raw_path, 'monthly', name='/%s.csv' % y, folder=False, unit=False)

    # ###################################################### raw to simulated #########################################
    # 处理数据
    g.china()
    # 提取最新日期
    af.updated_date('China')


if __name__ == '__main__':
    main()
