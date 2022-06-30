import requests
import pandas as pd
import os
import time
import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af

file_path = './data/oceania/australia/craw/'

region_list = ['NEM/NSW1', 'NEM/QLD1', 'NEM/SA1', 'NEM/TAS1', 'NEM/VIC1', 'WEM']
data_range = pd.date_range(start='1999-01', end='2022-07', freq='1M')

# 所有已爬取的
all_file = af.search_file(file_path)


def main():
    try:
        craw()  # 爬取数据
    except Exception as e:
        print(e)


def craw():
    for r in region_list:
        url = 'https://api.opennem.org.au/stats/power/network/fueltech/%s' % r
        r = r.replace('/', '_')  # windows文件名不能有斜杠 所以要转为下划线
        out_path = os.path.join(file_path, r)
        if not os.path.exists(out_path):  # 如果有了文件夹的话就直接pass掉
            os.mkdir(out_path)
        for d in data_range:
            params_data = {'month': pd.to_datetime(d).strftime('%Y-%m-%d')}
            # 如果已爬取则略过
            d_name = pd.to_datetime(d).strftime('%Y-%m')
            exist_name = os.path.join(file_path, r, '%s.csv' % d_name)
            if exist_name not in all_file:
                r_t = requests.get(url, params=params_data, timeout=60)
                result = pd.json_normalize(r_t.json(), record_path='data')
                result = result[result['type'] == 'power'].reset_index(drop=True)

                type_list = result['fuel_tech'].tolist()
                df = pd.DataFrame()
                for t in type_list:
                    temp = result[result['fuel_tech'] == t].reset_index(drop=True)
                    if temp['history.interval'][0] == '5m':  # 时间区间分为5分钟和30分钟不等 solar是30分钟
                        freq = '5min'
                    else:
                        freq = '30min'
                    start_time = pd.to_datetime(temp['history.start'][0]).strftime('%Y-%m-%d %H:%M:%S')
                    end_time = pd.to_datetime(temp['history.last'][0]).strftime('%Y-%m-%d %H:%M:%S')
                    date_range = pd.date_range(start=start_time, end=end_time, freq=freq)
                    data = temp['history.data'][0]  # 数据
                    df_temp = pd.DataFrame(data, date_range, columns=['data'])
                    df_temp['type'] = t  # 能源类型
                    df_temp['unit'] = temp['units'][0]  # 单位
                    df_temp['network'] = temp['network'][0]  # 地区
                    df_temp['region'] = temp['region'][0]  # 州
                    df = pd.concat([df, df_temp])
                df = df.reset_index().rename(columns={'index': 'datetime'})
                # 输出
                df.to_csv(os.path.join(out_path, '%s.csv' % d_name), index=False, encoding='utf_8_sig')
                time.sleep(15)


if __name__ == '__main__':
    main()
