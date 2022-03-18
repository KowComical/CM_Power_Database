#!/usr/bin/env python
# coding: utf-8

# In[54]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/13 13:51
# @Author  : Zhu Deng
# @Site    : https://github.com/zhudeng94
# @File    : toolkit.py
# @Software: PyCharm

import pandas as pd
import datetime
import numpy as np
import os
from tqdm import tqdm

sourcePath = 'K:\\Github\\GlobalPowerUpdate-Kow\\数据库\\code\\Europe'
dataPath = 'K:\\Github\\GlobalPowerUpdate-Kow\\数据库\\data\\europe\\eu27_uk'
endYear = datetime.datetime.utcnow().year
now = datetime.date.today().strftime("%Y-%m-%d") #获取当前年月日


def main():
    area = pd.read_csv(os.path.join(sourcePath, 'entsoe_areaCode.csv'))
    """
    Skip inactive data
    """
    area = area[area['hasData'].map(lambda x:x != 'inactive')]

    for i in tqdm(area.index):
        name = area['countryName'][i]
        timeDiff = area['timeDiff'][i]
        try:
            data_preprocess(dataPath, name, timeDiff)
        except:
            pass


def data_preprocess(dataPath, name, time_diff):

    country_data = pd.DataFrame()
    for year in range(2015, endYear + 1):
        tmp = pd.read_csv(os.path.join(dataPath, 'craw','entsoe', name, "%s_ENTSOE_%s.csv" % (name, year)))
        country_data = pd.concat([country_data, tmp])
    outfile = os.path.join(dataPath, 'raw','entsoe', "%s.csv" % name)

    # 数据预处理
    country_data['MTU'] = pd.to_datetime(country_data['MTU'].str[19:35], format='%d.%m.%Y %H:%M')
    # UTC时间转换为本地时间
    country_data['MTU'] = [(i + datetime.timedelta(hours=int(time_diff))) for i in country_data['MTU']]
    country_data.set_index('MTU', drop=True, inplace=True)

    del country_data['Area']

    # 删除所有列中包含'-'的行（'-'表示数据未发布）
    country_data = country_data.replace('-', np.nan)
    country_data = country_data.dropna(how='all')

    # 将'n/e'设置为空值
    country_data = country_data.replace('n/e', np.nan)

    country_data.to_csv(outfile)
    country_data = pd.read_csv(outfile, index_col=0)
    country_data.index = pd.to_datetime(country_data.index)

    # 中位差法去除异常值
    th = 3.5
    for col in country_data.columns[1:]:
        c = country_data[col]
        t = (c - c.median()).abs()
        c[0.75 * t / t.median() > th] = np.nan

    # 线性插值补全缺失值
    try:
        country_data.interpolate(method='linear', inplace=True)

        country_data = country_data.resample('1H').mean()
        country_data.to_csv(outfile, float_format="%.3f")
    except:
        pass


if __name__ == '__main__':
    main()

