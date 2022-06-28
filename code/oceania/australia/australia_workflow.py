import requests
import pandas as pd
import os

# 路径
in_path = './data/oceania/australia/craw/'
in_path_file = os.path.join(in_path, 'craw_data.csv')


def main():
    craw()  # 爬取数据


def craw():
    # 读取旧数据
    df_old = pd.read_csv(in_path_file)

    # 爬取新数据
    region_list = ['NEM/NSW1', 'NEM/QLD1', 'NEM/SA1', 'NEM/TAS1', 'NEM/VIC1', 'WEM']
    df = pd.DataFrame()

    for r in region_list:
        url = 'https://data.opennem.org.au/v3/stats/au/%s/power/7d.json' % r
        r = requests.get(url)
        result = pd.json_normalize(r.json(), record_path='data')
        result = result[result['type'] == 'power'].reset_index(drop=True)

        type_list = result['fuel_tech'].tolist()

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
    # 合并新旧数据并删除重复部分
    df_result = pd.concat([df_old, df]).reset_index(drop=True)
    df_result['datetime'] = pd.to_datetime(df_result['datetime'])
    df_result = df_result[~df_result.duplicated(['datetime', 'type', 'network', 'region'])]  # 删除重复的部分
    df_result.to_csv(in_path_file, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
