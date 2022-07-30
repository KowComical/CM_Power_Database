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

file_name = af.search_file(file_path)

end_date = datetime.now().strftime('%Y-%m-%d')
date_range = pd.date_range(start='2000-01-01', end=end_date, freq='D').strftime("%Y-%m-%d")[:-1]  # 不要最后一天

df_code = pd.read_csv(os.path.join(file_path, 'code.csv')).iloc[:6]
num_list = df_code['num'].unique()
name_list = df_code['name'].unique()


# 开始爬取分地区发电能源
def main():
    craw()


def craw():
    for num, name in zip(num_list, name_list):
        for d in date_range:
            if not os.path.exists(os.path.join(file_path, name, '%s.csv' % d)):  # 文件不存在才会开始爬
                time.sleep(1)
                temp_url = 'https://www.so-ups.ru/functioning/ees/ees-indicators/ees-gen-consump-hour' \
                           '/?tx_mscdugraph_pi[controller]=Graph&tx_mscdugraph_pi[action]=fullview&tx_mscdugraph_pi[' \
                           'viewDate]=%s&tx_mscdugraph_pi[viewKpo]=%s' % (d, int(num))
                try:
                    temp_r = requests.get(temp_url)
                except Exception as e:
                    print(e)
                    break
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
                    out_path = os.path.join(file_path, name)
                    if not os.path.exists(out_path):
                        os.mkdir(out_path)
                    df_data.to_csv(os.path.join(out_path, '%s.csv' % d), index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
