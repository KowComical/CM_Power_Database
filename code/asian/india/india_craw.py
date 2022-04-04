#!/usr/bin/env python
# coding: utf-8

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/3 16:07
# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : India_POSOCO.py
# @Software: PyCharm

def main():
    import datetime
    import os
    import requests
    from bs4 import BeautifulSoup
    from tqdm import tqdm
    path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\asia\\india\\craw\\'
    url = "https://posoco.in/reports/daily-reports/daily-reports-%s/"
    endYear = datetime.datetime.utcnow().year  # 获取当前年份
    for year in range(endYear - 1, endYear):
        date_range = str(year) + '-' + str(year + 1)[2:]
        if not os.path.exists(os.path.join(path, '0_original_pdf_file', date_range)):
            os.mkdir(os.path.join(path, '0_original_pdf_file', date_range))
        print(url % date_range)
        r = requests.get(url % date_range)
        if r.status_code == 200:  # successfully responses
            soup = BeautifulSoup(r.text, features='lxml')
            table = soup.find('table')
            for link in tqdm(table.find_all('a')):
                if 'NLDC' in link.text:
                    download_pdf_file(link, date_range)


def download_pdf_file(link, date_range):
    import os
    import time
    import requests
    path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\asia\\india\\craw\\'
    raw_link = link['href']
    filename = os.path.join(path, '0_original_pdf_file', date_range, raw_link.strip().split('/')[-2] + '.pdf')
    if not os.path.exists(filename):
        try:
            download = requests.get(raw_link, allow_redirects=True)
            open(filename, 'wb').write(download.content)
            parse_pdf_file(filename)
        except:
            time.sleep(10)


def parse_pdf_file(filename):
    import os
    import re
    import pdfplumber
    import time
    import pandas as pd
    path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\asia\\india\\craw\\'
    errors = os.path.join(path, 'error.txt')
    pattern1 = re.compile('\d+\.\d+\.\d+')
    try:
        pdf = pdfplumber.open(filename)
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
    try:
        for i in range(len(pdf.pages)):
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
    import os
    import pandas as pd
    out_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\asia\\india\\raw\\'
    output_1 = os.path.join(out_path, 'India_POSOCO_Daily.csv')
    output_2 = os.path.join(out_path, 'India_POSOCO_Daily_Thermal.csv')
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
