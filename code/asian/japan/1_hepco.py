# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 09 21 20:18
# ====================================================================================

# 北海道電力ネットワーク   hepco   http://denkiyoho.hepco.co.jp/area_forecast.html
# http://denkiyoho.hepco.co.jp/area/data/zip/202010-12_hokkaido_denkiyohou.zip

from global_code import global_function as af
import re


def main():
    u = 'http://denkiyoho.hepco.co.jp/area/data/zip/%s_hokkaido_denkiyohou.zip'

    directory = '1_hepco'

    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]

    name = re.compile(r'%s\\.*?_.*?_(?P<name>.*?).csv' % directory, re.S)

    # Download the zipfile data from non_exist file
    af.japan_download_Zipformat(u, in_path, name)
    # Extract all data
    af.japan_extractData(in_path, out_path, name, directory, date='20190922', ty='None')


if __name__ == '__main__':
    main()
