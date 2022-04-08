# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 09 21 20:18
# ====================================================================================

# P東北電力ネットワーク    tohoku-epco     https://setsuden.nw.tohoku-epco.co.jp/download.html
# https://setsuden.nw.tohoku-epco.co.jp/common/demand/juyo_2020_tohoku.csv

import urllib.request
from datetime import datetime
import pandas as pd
import re
from global_code import global_function as af


def main():
    u = 'https://setsuden.nw.tohoku-epco.co.jp/common/demand/juyo_%s_tohoku.csv'
    directory = '2_tohokuepco'

    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]

    name = re.compile(r'%s\\(?P<name>.*?).csv' % directory, re.S)

    # Download the zipfile data
    af.japan_download_Csvformat(u, in_path, name, start_date=2019)

    # Extract all data
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez')


if __name__ == '__main__':
    main()
