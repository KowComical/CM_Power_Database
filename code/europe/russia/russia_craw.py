import requests
import pandas as pd
import re
from datetime import datetime
import os
import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')

file_path = './data/europe/russia/craw/'

from global_code import global_function as af

file_name = af.search_file(file_path)

end_date = datetime.now().strftime('%Y-%m-%d')
date_range = pd.date_range(start='2000-01-01', end=end_date, freq='D').strftime("%Y-%m-%d")[:-1]  # 不要最后一天

headers = {
    'User-Agent': 'Mozilla'
                  '/5.0 (Macintosh; Intel Mac OS X 10_14) ''AppleWebKit'
                  '/605.1.15 (KHTML, like Gecko) ''Version/12.0 Safari/605.1.15'}

#  先找到各地区代码
url = 'https://www.so-ups.ru/functioning/ees/ees-indicators/ees-gen-consump-hour/?tx_mscdugraph_pi%5Bcontroller%5D' \
      '=Graph&tx_mscdugraph_pi%5Baction%5D=fullview&tx_mscdugraph_pi%5BviewDate%5D=2000-01-01&tx_mscdugraph_pi' \
      '%5BviewKpo%5D=1019 '


def main():
    craw()


def craw():
    r = requests.get(url)
    name = re.compile(r'<option value=(?P<num>.*?)>(?P<name>.*?)</option>', re.S)
    df_code = pd.DataFrame(name.findall(r.text)[1:], columns=['num', 'name'])

    num_list = df_code['num'].unique()
    name_list = df_code['name'].unique()
    # 开始爬取分地区发电能源
    for num, name in zip(num_list, name_list):
        for d in date_range:
            if not os.path.exists(os.path.join(file_path, name, '%s.csv' % d)):  # 文件不存在才会开始爬
                keyvalue = {'tx_mscdugraph_pi[controller]': 'Graph',
                            'tx_mscdugraph_pi[action]': 'fullview',
                            'tx_mscdugraph_pi[viewDate]': d,
                            'tx_mscdugraph_pi[viewKpo]': int(num)}
                temp_url = 'https://www.so-ups.ru/functioning/ees/ees-indicators/ees-gen-consump-hour/'
                try:
                    temp_r = requests.get(temp_url, params=keyvalue, headers=headers)
                except:
                    break
                # 提取当日数据
                df_data = pd.DataFrame()
                data = re.compile(
                    r'<div class="big-chart" data-type="4" data-datax="(?P<num>.*?)".*?data-datay1="(?P<name>.*?)"',
                    re.S)
                # 当日日期
                try:
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
                except:
                    out_path = os.path.join(file_path, name)
                    df_data.to_csv(os.path.join(out_path, '%s.csv' % d), index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
