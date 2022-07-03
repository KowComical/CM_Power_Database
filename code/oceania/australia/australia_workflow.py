import requests
import pandas as pd
import os

# 路径
in_path = './data/oceania/australia/raw/'
in_path_file = os.path.join(in_path, 'raw_data.csv')

import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af
from global_code import global_all as g


def main():
    # 爬取数据
    craw()
    # 处理数据
    g.australia()
    # 提取最新日期
    af.updated_date('Australia')


def craw():
    # 读取旧数据
    df_old = pd.read_csv(in_path_file)

    # 爬取新数据
    region_list = ['NEM/NSW1', 'NEM/QLD1', 'NEM/SA1', 'NEM/TAS1', 'NEM/VIC1', 'WEM']
    df = pd.DataFrame()

    for r in region_list:
        url = 'https://data.opennem.org.au/v3/stats/au/%s/power/7d.json' % r
        r = requests.get(url)
        result = pd.json_normalize(r.json(), record_path='data')
        result = result[result['type'] == 'power'].reset_index(drop=True)

        type_list = result['fuel_tech'].tolist()

        for t in type_list:
            temp = result[result['fuel_tech'] == t].reset_index(drop=True)
            if temp['history.interval'][0] == '5m':  # 时间区间分为5分钟和30分钟不等 solar是30分钟
                freq = '5min'
            else:
                freq = '30min'
            start_time = pd.to_datetime(temp['history.start'][0]).strftime('%Y-%m-%d %H:%M:%S')
            end_time = pd.to_datetime(temp['history.last'][0]).strftime('%Y-%m-%d %H:%M:%S')
            date_range = pd.date_range(start=start_time, end=end_time, freq=freq)
            data = temp['history.data'][0]  # 数据
            df_temp = pd.DataFrame(data, date_range, columns=['data'])
            df_temp['type'] = t  # 能源类型
            df_temp['unit'] = temp['units'][0]  # 单位
            df_temp['network'] = temp['network'][0]  # 地区
            df_temp['region'] = temp['region'][0]  # 州
            df = pd.concat([df, df_temp])
    df = df.reset_index().rename(columns={'index': 'datetime'})
    # 将能源类型分类并重新命名
    # coal
    coal_list = ['coal_brown', 'coal_black']
    # gas
    gas_list = ['gas_ccgt', 'gas_ocgt', 'gas_wcmg', 'gas_recip', 'gas_steam']
    # oil
    oil_list = ['distillate']
    # nuclear 暂无
    # wind
    wind_list = ['wind']
    # solar
    solar_list = ['solar_rooftop', 'solar_utility']
    # hydro
    hydro_list = ['hydro', 'pumps']
    # other #存疑
    other_list = ['bioenergy_biomass', 'bioenergy_biogas']

    for c in coal_list:
        df['type'] = df['type'].replace(c, 'coal')
    for c in gas_list:
        df['type'] = df['type'].replace(c, 'gas')
    for c in oil_list:
        df['type'] = df['type'].replace(c, 'oil')
    for c in wind_list:
        df['type'] = df['type'].replace(c, 'wind')
    for c in solar_list:
        df['type'] = df['type'].replace(c, 'solar')
    for c in hydro_list:
        df['type'] = df['type'].replace(c, 'hydro')
    for c in other_list:
        df['type'] = df['type'].replace(c, 'other')
    # 去掉不要的能源类型
    type_list = ['coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']
    df = df[df['type'].isin(type_list)].reset_index(drop=True)
    # 按能源汇总
    df = df.groupby(['datetime', 'type']).sum().reset_index()
    # 按小时汇总
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['hour'] = df['datetime'].dt.hour

    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']].assign(), errors='coerce')
    df = df[['datetime', 'type', 'data']]
    df = df.groupby(['datetime', 'type']).mean().reset_index()
    # 将所有小于0的值变为0
    df.loc[df[df['data'] < 0].index, ['data']] = 0
    # 合并新旧数据并删除重复部分
    df_result = pd.concat([df_old, df]).reset_index(drop=True)
    df_result['datetime'] = pd.to_datetime(df_result['datetime'])
    df_result = df_result[~df_result.duplicated(['datetime', 'type'])]  # 删除重复的部分
    df_result.to_csv(in_path_file, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
