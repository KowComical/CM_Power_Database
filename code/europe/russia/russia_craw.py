import requests
import pandas as pd
import re
from datetime import datetime
import os
import time
import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')

file_path = './data/europe/russia/craw/'

from global_code import global_function as af

end_date = datetime.now().strftime('%Y-%m-%d')
# 应该爬取的所有日期范围
date_range = pd.date_range(start='2000-01-01', end=end_date, freq='D').strftime("%Y-%m-%d")[:-1]  # 不要最后一天

df_code = pd.read_csv(os.path.join(file_path, 'code.csv'))
num_list = df_code['num'].unique()
name_list = df_code['name'].unique()


# 开始爬取分地区发电能源
def main():
    craw()


def craw():
    for num, name in zip(num_list, name_list):
        file_name = af.search_file(os.path.join(file_path, name))  # 读取当前region文件夹的数据
        date_name = re.compile(r'%s/.*?/(?P<title>.*?).csv' % name, re.S)  # 节选日期
        exisiting_date = []  # 提取所有已存在的文件
        for f in file_name:
            exisiting_date.append(date_name.findall(f)[0])
        # 找到还未爬取的范围
        needed_range = list(set(date_range) - set(exisiting_date))
        for d in needed_range:
            time.sleep(1)
            temp_url = 'https://www.so-ups.ru/functioning/ees/ees-indicators/ees-gen-consump-hour' \
                       '/?tx_mscdugraph_pi[controller]=Graph&tx_mscdugraph_pi[action]=fullview&tx_mscdugraph_pi[' \
                       'viewDate]=%s&tx_mscdugraph_pi[viewKpo]=%s' % (d, int(num))
            temp_r = requests.get(temp_url)
            # 提取当日数据
            df_data = pd.DataFrame()
            data = re.compile(
                r'<div class="big-chart" data-type="4" data-datax="(?P<num>.*?)".*?data-datay1="(?P<name>.*?)"',
                re.S)
            # 当日日期
            if data.findall(temp_r.text):  # 如果有数据
                temp = pd.DataFrame([data.findall(temp_r.text)[0][0]])
                date_list = temp[0].str.split(',', expand=True).iloc[0]
                # 当日数值
                temp = pd.DataFrame([data.findall(temp_r.text)[0][1]])
                data_list = temp[0].str.split(',', expand=True).iloc[0]

                df_data['date'] = date_list
                df_data['mw'] = data_list
                df_data['region'] = name
                # 输出
                out_path = os.path.join(file_path, name, str(pd.to_datetime(d).strftime('%Y')))  # 按照地区年份分文件夹
                if not os.path.exists(out_path):
                    os.mkdir(out_path)
                df_data.to_csv(os.path.join(out_path, '%s.csv' % d), index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
