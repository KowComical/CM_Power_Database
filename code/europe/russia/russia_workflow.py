# 数据源来自: Zhu Deng
import requests
import sys
import pandas as pd
import os
from datetime import datetime

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af
from global_code import global_all as g
sys.path.append('./code/europe/')
from russia import russia_craw as rc

global_path = './data/'
file_path = os.path.join(global_path, 'europe', 'russia')
out_path = os.path.join(file_path, 'raw')
new_path = os.path.join(file_path, 'craw', 'ЕЭС РОССИИ')
out_path_simulated = af.create_folder(file_path, 'simulated')

end_year = int(datetime.now().strftime('%Y'))


def main():
    # 爬虫
    craw()
    # 处理数据
    g.russia()
    # 新数据源爬取
    rc.main()
    # 讲之前数据源停止的数据用新数据源填补
    filling_new()
    # 提取最新日期
    af.updated_date('Russia')


def craw():
    for i in range(end_year, end_year + 1):
        url = 'https://858127-cc16935.tmweb.ru/webapi/api/CommonInfo/PowerGeneration?priceZone[' \
              ']=0&startDate=%s.01.01&endDate=%s.12.31' % (
        i, i)

        r = requests.get(url)
        df = pd.json_normalize(r.json()[0], record_path='m_Item2')
        df.to_csv(os.path.join(out_path, 'yearly', '%s.csv' % i), index=False, encoding='utf_8_sig')


def filling_new():
    file_name = af.search_file(new_path)  # 读取新数据源数据
    df = pd.concat([pd.read_csv(f) for f in file_name]).reset_index(drop=True).drop(columns=['region'])
    df['date'] = pd.to_datetime(df['date'])
    df_old = df.copy()
    df = df[df['date'] >= '2022-05-16'].reset_index(drop=True).rename(columns={'date': 'datetime'})  # 从旧数据源有问题的地方开始
    # 讲前一年的各能源占比填进来
    df['year'] = df['datetime'].dt.year - 1
    df['month'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['hour'] = df['datetime'].dt.hour
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']].assign(), errors='coerce')
    df = df[['datetime', 'mw']]

    # 读取simulated数据
    file_name = af.search_file(out_path_simulated)
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('hourly') != -1]
    df_hourly = pd.concat([pd.read_csv(f) for f in file_name]).reset_index(drop=True)
    df_hourly = df_hourly[df_hourly['date'] <= '2022-05-15'].reset_index(drop=True)  # 2022年5月15号之后数据就开始出现问题
    df_hourly['datetime'] = pd.to_datetime(df_hourly['datetime'])

    df_temp = pd.merge(df, df_hourly).drop(columns=['total.prod']).rename(columns={'mw': 'total.prod'})
    # 按照去年的占比得到今年的能源数据
    col_list = df_temp.loc[:, df_temp.columns.str.contains('perc', case=False)].columns
    for c in col_list:
        df_temp[c[:-5]] = df_temp['total.prod'] * df_temp[c]

    # 改回今年
    df_temp['day'] = pd.to_datetime(df_temp['date']).dt.day
    df_temp['year'] = df_temp['year'] + 1
    df_temp['datetime'] = pd.to_datetime(df_temp[['year', 'month', 'day', 'hour']].assign(), errors='coerce')
    af.time_info(df_temp, 'datetime')
    df_temp = df_temp.drop(columns=['day'])
    # 新旧合并
    df_new = pd.concat([df_hourly, df_temp]).reset_index(drop=True)
    df_new['datetime'] = pd.to_datetime(df_new['datetime'])

    # 讲所有之前的全能源都替换为新数据源数据
    df_old = df_old.rename(columns={'date': 'datetime'})
    df_old['datetime'] = pd.to_datetime(df_old['datetime'])

    df_result = pd.merge(df_old, df_new).drop(columns=['total.prod']).rename(columns={'mw': 'total.prod'})
    for c in col_list:
        df_result[c[:-5]] = df_result['total.prod'] * df_result[c]

    # 输出
    for y in df_result['year'].drop_duplicates().tolist():
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        # hourly
        df_hourly = df_result[df_result['year'] == y].reset_index(drop=True)
        af.agg(df_hourly, 'datetime', out_path_simulated_yearly, 'hourly',
               name='Russia_hourly_generation-' + str(y) + '.csv', folder=False, unit=False)
        df_daily = df_hourly.copy()
        df_monthly = df_hourly.copy()
        # daily
        df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
        af.agg(df_daily, 'datetime', out_path_simulated_yearly, 'daily',
               name='Russia_daily_generation-' + str(y) + '.csv', folder=False, unit=True)
        # monthly
        df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
        af.agg(df_monthly, 'datetime', out_path_simulated_yearly, 'monthly',
               name='Russia_monthly_generation-' + str(y) + '.csv', folder=False, unit=True)


if __name__ == '__main__':
    main()
