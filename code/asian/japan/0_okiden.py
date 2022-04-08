# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 09 21 20:18
# ====================================================================================

# 0 N沖縄電力     　        okiden          http://www.okiden.co.jp/denki2/dl/
# http://www.okiden.co.jp/denki2/juyo_10_20201020.csv
import re
from global_code import global_function as af


def main():
    u = 'http://www.okiden.co.jp/denki2/juyo_10_%s.csv'

    directory = '0_okiden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]

    name = re.compile(r'%s\\(?P<name>.*?).csv' % directory, re.S)
    # Download the zipfile from non_exisiting date
    af.japan_download_Csvformat(u, in_path, name, start_date='20190101')
    # Extract all data
    af.japan_extractData(in_path, out_path, name, directory, date='20190831', ty='None')


if __name__ == '__main__':
    main()
