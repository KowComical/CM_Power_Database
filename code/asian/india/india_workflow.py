# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : India_POSOCO.py

import datetime
import requests
from bs4 import BeautifulSoup
import os
import re
import pdfplumber
import time
import pandas as pd
import sys

sys.dont_write_bytecode = True

sys.path.append('./code/')
from global_code import global_function as af
from global_code import global_all as g

in_path = './data/asia/india/craw/'
out_path = './data/asia/india/raw/'
output_1 = os.path.join(out_path, 'India_POSOCO_Daily.csv')
output_2 = os.path.join(out_path, 'India_POSOCO_Daily_Thermal.csv')


def main():
    # 爬虫+预处理
    craw()
    # 整理数据
    g.india()
    # 提取最新日期
    af.updated_date('India')


def craw():
    url = "https://posoco.in/reports/daily-reports/daily-reports-%s/"
    endYear = datetime.datetime.utcnow().year  # 获取当前年份
    for year in range(endYear - 1, endYear + 1):
        date_range = str(year) + '-' + str(year + 1)[2:]
        if not os.path.exists(os.path.join(in_path, '0_original_pdf_file', date_range)):
            os.mkdir(os.path.join(in_path, '0_original_pdf_file', date_range))
        r = requests.get(url % date_range)
        if r.status_code == 200:  # successfully responses
            soup = BeautifulSoup(r.text, features='lxml')
            table = soup.find('table')
            for link in table.find_all('a'):
                if 'NLDC' in link.text:
                    download_pdf_file(link, date_range)


def download_pdf_file(link, date_range):
    raw_link = link['href']
    filename = os.path.join(in_path, '0_original_pdf_file', date_range, raw_link.strip().split('/')[-2] + '.pdf')
    if not os.path.exists(filename):
        # noinspection PyBroadException
        try:
            download = requests.get(raw_link, allow_redirects=True)
            open(filename, 'wb').write(download.content)
            parse_pdf_file(filename)
        except:
            time.sleep(10)


def parse_pdf_file(filename):
    errors = os.path.join(in_path, 'error.txt')
    pattern1 = re.compile('\d+\.\d+\.\d+')
    # noinspection PyBroadException
    try:
        pdf = pdfplumber.open(filename)
        # noinspection PyBroadException
        try:
            date = pattern1.findall(pdf.pages[0].extract_text())[0]
            date = date.split('.')[2] + '-' + date.split('.')[1] + '-' + date.split('.')[0]
        except:
            date = filename
    except:
        f = open(errors, 'a+')
        f.write(time.strftime('%Y%m%d %H:%M') + ": " + filename + '\n')
        f.close()
        return
    # noinspection PyBroadException
    try:
        for i in range(len(pdf.pages)):
            # noinspection PyBroadException
            try:
                dfs = pdf.pages[i].extract_tables()
                for d in dfs:
                    d = pd.DataFrame(d[1:], columns=d[0])
                    if '' in d.columns:
                        if 'Hydro' in d[''].tolist():
                            extract_table(d, date)
            except:
                pass
    except:
        f = open(errors, 'a+')
        f.write(time.strftime('%Y%m%d %H:%M') + ": " + filename + '\n')
        f.close()
        return


def extract_table(df, date):
    if len(df) >= 7:
        temp = pd.DataFrame(df.iloc[0:7, 6]).T
        temp.columns = ['Coal', 'Lignite', 'Hydro', 'Nuclear', 'Gas, Naptha & Diesel',
                        'RES (Wind, Solar, Biomass & Others)', 'Total']
        temp['date'] = date
        # return temp
        if os.path.exists(output_1):
            temp.to_csv(output_1, mode='a', header=False, index=False)
        else:
            temp.to_csv(output_1, index=False)
    else:
        temp = pd.DataFrame(df.iloc[0:6, 6]).T
        temp.columns = ['Thermal (Coal & Lignite)', 'Hydro', 'Nuclear', 'Gas, Naptha & Diesel',
                        'RES (Wind, Solar, Biomass & Others)', 'Total']
        temp['date'] = date
        # return temp
        if os.path.exists(output_2):
            temp.to_csv(output_2, mode='a', header=False, index=False)
        else:
            temp.to_csv(output_2, index=False)


if __name__ == '__main__':
    main()
