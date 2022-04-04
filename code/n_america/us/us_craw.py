# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 08 04 15:56
# ====================================================================================

def main():
    import pandas as pd
    import os
    import requests
    import json
    import datetime
    import dateutil
    from tqdm import tqdm
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    import sys

    module_path_string = "K:\\Github\\GlobalPowerUpdate-Kow\\code\\global_code"
    sys.path.append(module_path_string)

    import global_function as af

    path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\n_america\\us\\craw\\'
    startDate = datetime.datetime.now().strftime('%Y%m') + '01'  # 当月第一天 数据最起码要一个月间隔
    endDate = datetime.datetime.now().strftime('%Y%m%d')
    interval = 'hourly'
    regions = pd.read_csv(os.path.join(path, 'EIA_Regions.csv'))

    for i in range(0, len(regions)):
        r = regions['id'][i]
        timeZone = regions['time_zone'][i]
        print(r, startDate, endDate)
        US48 = pd.DataFrame(
            columns=['datetime', 'Coal', 'Wind', 'Hydro', 'Solar', 'Other', 'Petroleum', 'Nuclear', 'Natural gas'])
        US48 = US48.set_index('datetime')
        for s in tqdm(pd.date_range(startDate, endDate, freq='MS')):
            sDate = s.strftime('%m%d%Y')
            eDate = (datetime.datetime.strptime(sDate, "%m%d%Y") + dateutil.relativedelta.relativedelta(
                months=1) + datetime.timedelta(days=-1)).strftime('%m%d%Y')
            outfile_path = af.create_folder(path + 'time_line\\', sDate + '_' + eDate)
            outfile = os.path.join(outfile_path, 'US_EIA_Regional_%s.csv' % (interval + '_' + r))
            # NG for net generation; US48 for 48 states in US; no more than 365 days are chosen
            url = 'https://www.eia.gov/electricity/930-api/region_data_by_fuel_type/series_data?' \
                  'type[0]=NG' \
                  '&respondent[0]=' + r + \
                  '&start=' + sDate + ' 00:00:00' \
                                      '&end=' + eDate + ' 23:59:59' \
                                                        '&frequency=' + interval + \
                  '&series=undefined' \
                  '&limit=10000' \
                  '&offset=0' \
                  '&timezone=' + timeZone

            while True:
                try:
                    res = requests.get(url)
                    break
                except:
                    pass
            data = json.loads(res.content.decode())[0]['data']

            Flag = 1
            for d in data:
                temp = pd.DataFrame(d['VALUES'])[['DATES', 'DATA']]
                temp.columns = ['DATES', d['FUEL_TYPE_NAME']]
                temp['DATES'] = pd.to_datetime(temp['DATES'])
                temp.rename(columns={'DATES': 'datetime'}, inplace=True)
                temp.set_index('datetime', drop=True, inplace=True)
                if Flag:
                    df = temp
                    Flag = 0
                else:
                    df = df.join(temp, how='outer')
                df['region'] = r
                # df['time_zone'] = 'US/'+timeZone
                df.to_csv(outfile, encoding='utf_8_sig')

    # data_process
    file_path = path + 'time_line\\'
    out_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\n_america\\us\\raw\\'
    file_name = af.search_file(file_path)
    df = pd.concat(pd.read_csv(f) for f in file_name).sort_values(by='datetime')
    df = df.groupby(['datetime']).sum().reset_index()
    col_list = ['datetime', 'coal', 'wind', 'hydro', 'solar', 'other', 'oil', 'nuclear', 'gas']
    df.columns = col_list
    df.to_csv(out_path + 'raw.csv', index=False)


if __name__ == '__main__':
    main()

