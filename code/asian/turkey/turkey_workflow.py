#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/7 15:43
# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : Turkey_TEIAS.py
# @Software: PyCharm
import datetime

import pandas as pd
import requests
import json
import re
from tqdm import tqdm
import os
import time

url = 'https://ytbsbilgi.teias.gov.tr/ytbsbilgi/frm_istatistikler.jsf'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50',
    'Cookie': 'JSESSIONID=D3148B880363156DBC78CB65ECA3E112; '
              'TS0152acb3'
              '=019183421958fbdbf3b08a25bdbeddc7b8bad81b71b55c80c547fd3db4125c665fe2a1b1ce28a4f4ef83efd988beb4513ce263198334dae7a7c0e08efde459b58a42b121a6; TS01ef6dd3=0191834219fbe03b30ef539d1e9d8492fbff7ad2b4b55c80c547fd3db4125c665fe2a1b1ce4f6c806bdebe738bb9f04e7566f6953d; TS01ef6dd3031=0188b55a20a65ea743b2cba56c1827dad3c63ef4bc5876a79a0323ec8783b38e4ae5f6be5c2a25ceae28c8f78308161b637b80295264901042de20063391e59de7c1a311f7',
}
Data = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formdash:rapor',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formdash',
    'formdash:rapor': 'formdash:rapor',
    'formdash': 'formdash',
    'hidden1': '13',
    'formdash:bitisTarihi2_input': '2021-11-05',
    'javax.faces.ViewState': '2866292535702225257:-4806324036425322669'
}
COLUMNS_MAP = {
    'saat': 'Hour',
    'linyit': 'Lignite',
    'taskomur': 'Hard Coal',
    'asfaltitkomur': 'Asphaltite Coal',
    'ithalkomur': 'Imported Coal',
    'fueloil': 'Fuel Oil',
    'motorin': 'Dıesel Oil',
    'nafta': 'Naphtha',
    'lpg': 'LPG',
    'dogalgaz': 'Natural Gas',
    'lng': 'LNG',
    'atikisi': 'Waste',
    'biyokutle': 'Biomass',
    'jeotermal': 'Geothermal',
    'barajli': 'Hydro Storage',
    'akarsu': 'Run Of River',
    'ruzgar': 'Wind',
    'gunes': 'Solar',
}
COLS = ['Date'] + list(COLUMNS_MAP.values())
START_YEAR = 2014

path = './data/asia/turkey/'
raw_path = os.path.join(path, 'raw')
if not os.path.exists(path):
    os.mkdir(path)

p = re.compile(r'var gunlukUretimEgrisiData = (?P<data>.*);')


def main():
    # start from 2016.1.1
    end_year = datetime.datetime.now().year + 1
    for year in range(START_YEAR, end_year):
        dateRange = pd.date_range(str(year) + '-01-01', '%d-12-31' % year, freq='D')
        outfile = os.path.join(raw_path, 'Turkey_TEIAS_Hourly_%d.csv' % year)
        df = pd.DataFrame()
        for date in tqdm(dateRange):
            Data['formdash:bitisTarihi2_input'] = date.strftime('%Y-%m-%d')
            while True:
                # noinspection PyBroadException
                try:
                    r = requests.get(url, data=json.dumps(Data), headers=headers)
                    match = p.findall(r.text)[0]
                    if match[0] != '[':
                        match = '[' + match + ']'
                    temp = pd.DataFrame(json.loads(match))
                    temp['Date'] = date.strftime('%Y-%m-%d')
                    df = pd.concat([df, temp])
                    break
                except:
                    time.sleep(5)
                    pass
        df.rename(columns=COLUMNS_MAP, inplace=True)
        df.to_csv(outfile, index=False)


if __name__ == '__main__':
    main()
