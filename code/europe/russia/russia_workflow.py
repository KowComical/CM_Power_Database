import requests
import sys
import pandas as pd
import os

sys.dont_write_bytecode = True
sys.path.append('../../code/')
from global_code import global_all as g


def main():
    out_path = '../../data/europe/russia/raw/'

    # 爬取数据
    url = 'https://emres.cn/api/carbonmonitor/getRussiaPowerHourly.php'  # api 来自于邓铸
    r = requests.get(url)
    df = pd.json_normalize(r.json())
    print(df)
    # df.to_csv(os.path.join(out_path, 'Russia_Hourly_Generation.csv'), index=False, encoding='utf_8_sig')
    # 处理数据
    # g.russia()


if __name__ == '__main__':
    main()
