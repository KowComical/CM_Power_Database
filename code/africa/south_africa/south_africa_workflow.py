# 南非的近期发电数据
import re
import requests
import pandas as pd
import os

import sys

sys.dont_write_bytecode = True

def main():
    out_path = './data/africa/south_africa/aw/'
    out_file = os.path.join(out_path, 'last_7_days.csv')
    url = 'https://www.eskom.co.za/dataportal/supply-side/station-build-up-for-the-last-7-days/'

    r = requests.get(url)
    path = re.compile(r'<h3 class="elementor-icon-box-title">.*?<a href="(?P<name>.*?)">Download data file</a>', re.S)
    download_path = path.findall(r.text)[0]  # 找到下载链接地址

    df = pd.read_csv(download_path)  # 提取数据

    # 读取旧数据并合并未重复部分
    df_old = pd.read_csv(out_file)
    df_result = pd.concat([df_old, df]).reset_index(drop=True)
    df_result = df_result[~df_result.duplicated()].sort_values(by='Date_Time_Hour_Beginning').reset_index(drop=True)
    # 输出
    df_result.to_csv(out_file, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()

