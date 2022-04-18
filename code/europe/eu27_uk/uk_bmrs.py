#!/usr/bin/env python
# coding: utf-8

# In[5]:


# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/23 00:19
# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : UK_BMRE.py
# @Software: PyCharm

import requests
import pandas as pd
from datetime import datetime
import json
from tqdm import tqdm
import os

parameter = {
    "flowid": "gbfthistoric",
    "start_date": "",
    "end_date": ""
}
base_url = 'https://www.bmreports.com/bmrs/?q=tabledemand&parameter='

path = '../../data/europe/eu27_uk/raw/uk-BMRS/'
if not os.path.exists(path):
    os.mkdir(path)

flag = 1
output_file = os.path.join(path, 'UK_BMRS_Hourly.csv')
if os.path.exists(output_file):
    df = pd.read_csv(output_file, index_col=1)
    start_date = df.index.max()
    flag = 0
else:
    start_date = '2018-01-01'
end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
date_range = pd.date_range(start_date, end_date)


def main():
    global flag
    for d in tqdm(range(len(date_range) - 1)):
        parameter['start_date'] = datetime.strftime(date_range[d], '%Y-%m-%d')
        parameter['end_date'] = datetime.strftime(date_range[d + 1], '%Y-%m-%d')

        url = base_url + str(parameter).replace('\'', '\"')
        res = requests.get(url)
        js = json.loads(res.text)['responseBody']['responseList']['item']
        df_temp = pd.DataFrame(js)
        if flag:
            df_temp.to_csv(output_file, index=False)
            flag = 0
        else:
            df_temp.to_csv(output_file, index=False, header=False, mode='a')


if __name__ == '__main__':
    main()
