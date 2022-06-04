import re
import pandas as pd
import requests
import os

file_path = './data/europe/eu27_uk/raw/UK_Electricity_Production/'
if not os.path.exists(file_path):
    os.mkdir(file_path)
out_path = os.path.join(file_path, 'UK_GMT_MW.csv')


def main():
    craw()


def craw():
    df_old = pd.read_csv(out_path)
    col_list = ['Biomass', 'CCGT', 'Coal', 'Hydroelectric', 'Interconnect', 'Nuclear', 'OCGT', 'Oil', 'Other',
                'Pumped Storage', 'Wind', 'solar']
    date_list = ['year', 'month', 'day', 'hour', 'minute']

    url = 'https://electricityproduction.uk/from/all-sources/?t=7d'
    r = requests.get(url)
    # 筛选有用数据
    data_table = re.compile(r'allsource_data.addRows(?P<name>.*?);', re.S)
    # list to dataframe
    df = pd.DataFrame(data_table.findall(r.text)[0][2:-3].split('['))[1:]
    df = df[0].str.split('[)],', expand=True)
    # 处理日期格式
    df_date = df[0].str.split(',', expand=True)
    df_date[0] = df_date[0].str.replace('new Date[(]', '')
    # 将日期转为datetime格式
    df_date.columns = date_list
    df_date['datetime'] = pd.to_datetime(df_date[['year', 'month', 'day', 'hour', 'minute']].assign(), errors='coerce')
    # 处理data格式
    df_data = df[1].str.split(',', expand=True).drop(columns=[12, 13])
    df_data.columns = col_list
    # 合并结果
    df_result = pd.concat([df_date[['datetime']], df_data], axis=1)

    # 合并新旧结果
    df_result = pd.concat([df_old, df_result]).reset_index(drop=True)
    # 删除重复的列
    df_result = df_result.loc[:, ~df_result.columns.duplicated()]
    # 输出结果
    df_result.to_csv(out_path, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
