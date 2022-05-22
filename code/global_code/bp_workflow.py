import pandas as pd
import requests
import re
import os

out_path = './data/#global_rf/bp/'
out_file = os.path.join(out_path, 'bp_raw.xlsx')

import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af


def main():
    download()  # 爬虫数据
    cleansing()  # 清理并输出
    # 提取最新日期
    af.updated_date('bp_cleaned')


def download():
    url = 'https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy.html'
    r = requests.get(url)
    path = re.compile(r'<a class="nr-linkcta__link-list-anchor" target="_blank" href="(?P<in_path>.*?)">', re.S)

    file_name = path.findall(r.text)
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('xlsx') != -1][0]  # 筛选需要的下载地址
    file_name = 'https://www.bp.com' + file_name

    r = requests.get(file_name)
    with open(out_file, 'wb') as f:
        f.write(r.content)


def cleansing():
    xl = pd.ExcelFile(out_file).sheet_names
    sheet_list = [xl[i] for i, z in enumerate(xl) if z.find('TWh') != -1]
    sheet_fossil = [xl[i] for i, z in enumerate(xl) if z.find('Gen from') != -1]
    xl = sheet_list + sheet_fossil

    df_all = pd.DataFrame()
    for x in xl:
        df = pd.read_excel(out_file, sheet_name=x, header=2).rename(columns={'Terawatt-hours': 'country'})
        df = df.dropna(axis=0, how='all', thresh=2).reset_index(drop=True)  # 非空值小于2时删除行
        df = df.dropna(axis=1, how='all').iloc[:, :-3]  # 最后三列不要

        # 不要total asia pacific之后的行
        ignore_index = df[df['country'] == 'Total Asia Pacific'].index.tolist()[0]
        df = df[:ignore_index]

        #  去掉汇总的行
        df = df[~df['country'].str.contains('Total')].reset_index(drop=True)
        df = df[~df['country'].str.contains('Other')].reset_index(drop=True)

        df = df.set_index(['country']).stack().reset_index().rename(columns={'level_1': 'date', 0: 'value'})
        df['type'] = x
        df_all = pd.concat([df, df_all]).reset_index(drop=True)

    df_all = pd.pivot_table(df_all, index=['country', 'date'], values='value', columns='type').reset_index()
    df_all['other'] = df_all['Geo Biomass Other - TWh']
    df_all = df_all.rename(
        columns={'Elec Gen from Coal': 'coal', 'Elec Gen from Gas': 'gas', 'Elec Gen from Oil': 'oil',
                 'Hydro Generation - TWh': 'hydro', 'Nuclear Generation - TWh': 'nuclear',
                 'Solar Generation - TWh': 'solar', 'Wind Generation - TWh': 'wind'})

    df_all[['coal', 'gas', 'oil', 'nuclear', 'hydro', 'wind', 'solar', 'other']] = df_all[
                                                                                       ['coal', 'gas', 'oil', 'nuclear',
                                                                                        'hydro', 'wind', 'solar',
                                                                                        'other']] * 1000  # Twh to Gwh
    df_all = df_all[['country', 'date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'wind', 'solar', 'other']]
    df_all.to_csv(out_path + 'bp_cleaned.csv', index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
