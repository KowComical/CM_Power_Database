# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 09 21 20:18
# ====================================================================================

# 4 N中部電力パワーグリッド    chuden         https://powergrid.chuden.co.jp/denkiyoho/
# https://powergrid.chuden.co.jp/denki_yoho_content_data/download_csv/202010_power_usage.zip

import urllib.request
import pandas as pd
from datetime import datetime
import zipfile
import os
from tqdm import tqdm
from global_code import global_function as af

u = 'https://powergrid.chuden.co.jp/denki_yoho_content_data/download_csv/%s_power_usage.zip'
directory = '4_chuden'
in_path = af.japan_path(directory)[0]
out_path = af.japan_path(directory)[1]


def main():
    # Download the zipfile data
    startDate = '20190401'
    endDate = datetime.now().strftime("%Y%m%d")
    download_Zipformat(startDate, endDate)

    # Extract all data
    extractData()


def download_Zipformat(startDate, endDate):
    for month in tqdm(pd.date_range(startDate, endDate, freq='MS')):
        dateRange = month.strftime('%Y%m')
        fileName = "OriginalData/%s/%s.zip" % (directory, dateRange)
        print(u % dateRange)
        urllib.request.urlretrieve(u % dateRange, fileName)
        zip_file = zipfile.ZipFile(fileName)
        zip_file.extractall(path=originalDataPath)


def extractData():
    result = pd.DataFrame()
    files = os.listdir(originalDataPath)
    files.sort(key=lambda x: x[:-4])
    for file in files:
        if os.path.isdir(originalDataPath + file):
            fs = os.listdir(originalDataPath + file)
            fs.sort(key=lambda x: x[:-4])
            for f in fs:
                df = pd.read_csv(originalDataPath + file + '/' + f, skiprows=13, nrows=24, encoding='Shift_JIS')
                result = pd.concat([result, df])
        else:
            if 'csv' not in file or 'areajuyo' in file: continue
            df = pd.read_csv(originalDataPath + file, skiprows=13, nrows=24, encoding='Shift_JIS')
            result = pd.concat([result, df])
    pd.DataFrame(columns=result.columns).to_csv('%s.csv' % directory, index=False)
    header = pd.read_csv(originalDataPath + 'areajuyo_current.csv', encoding='Shift_JIS')
    header = header[header['DATE'] >= '2019/01/01']
    header.to_csv('%s.csv' % directory, index=False, header=False, mode='a')
    result.to_csv('%s.csv' % directory, index=False, header=False, mode='a')


if __name__ == '__main__':
    main()
