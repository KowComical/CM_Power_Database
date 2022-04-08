# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 09 21 20:18
# ====================================================================================

# 3 N東京電力パワーグリッド    tepco           https://www.tepco.co.jp/forecast/html/download-j.html
# https://www.tepco.co.jp/forecast/html/images/juyo-2020.csv

import urllib.request
import pandas as pd
from datetime import datetime
import os
from global_code import global_function as af
import re


def main():
    u = 'https://www.tepco.co.jp/forecast/html/images/juyo-%s.csv'
    directory = '3_hepco'

    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]

    name = re.compile(r'%s\\(?P<name>.*?).csv' % directory, re.S)

    # Download the zipfile data
    af.japan_download_Csvformat(u, in_path, name, start_date=2019)

    # Extract all data
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez')


if __name__ == '__main__':
    main()
