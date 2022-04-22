# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 08 04 15:56
# ====================================================================================

import pandas as pd
import os
import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import sys

sys.path.append('./code/global_code/')
import global_function as af
import global_all as g

in_path = './data/n_america/us/craw/'
out_path = './data/n_america/us/raw/'
startDate = (datetime.today().replace(day=1) - timedelta(days=1)).strftime("%Y%m") + '01'  # 上月第一天 间隔起码一个月
endDate = datetime.now().strftime('%Y%m%d')
interval = 'hourly'
regions = pd.read_csv(os.path.join(in_path, 'EIA_Regions.csv'))

for i in range(0, len(regions)):
    r = regions['id'][i]
    timeZone = regions['time_zone'][i]
    print(r, startDate, endDate)
    for s in tqdm(pd.date_range(startDate, endDate, freq='MS')):
        sDate = s.strftime('%m%d%Y')
        eDate = (datetime.strptime(sDate, "%m%d%Y") +
                 relativedelta(months=1) + timedelta(days=-1)).strftime('%m%d%Y')
        outfile_path = af.create_folder(in_path + 'time_line', sDate + '_' + eDate)
        outfile = os.path.join(outfile_path, 'US_EIA_Regional_%s.csv' % (interval + '_' + r))
        # NG for net generation; US48 for 48 states in US; no more than 365 days are chosen
        url = 'https://www.eia.gov/electricity/930-api/region_data_by_fuel_type/series_data?' \
              'ty[0]=NG' \
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
file_name = af.search_file(os.path.join(in_path, 'time_line'))
df = pd.concat(pd.read_csv(f) for f in file_name).sort_values(by='datetime')
df = df.groupby(['datetime']).sum().reset_index()
col_list = ['datetime', 'coal', 'wind', 'hydro', 'solar', 'other', 'oil', 'nuclear', 'gas']
df.columns = col_list
df.to_csv(os.path.join(out_path, 'raw.csv'), index=False)

# 数据整理
g.us()
# 数据可视化
af.draw_pic('us')
