import re
from global_code import global_function as af
import urllib.request


def main():
    okiden()
    hepco()
    tohoku()
    tepco()
    chuden()
    rikuden()
    kansai()
    energia()
    yonden()
    kyuden()


def okiden():
    # 0_okiden
    u = 'http://www.okiden.co.jp/denki2/juyo_10_%s.csv'
    directory = '0_okiden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date='20190101')
    af.japan_extractData(in_path, out_path, name, directory, date='20190831', ty='None', first=13, second=7)


def hepco():
    # 1_hepco
    u = 'http://denkiyoho.hepco.co.jp/area/data/zip/%s_hokkaido_denkiyohou.zip'
    directory = '1_hepco'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/.*?_.*?_(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Zipformat(u, in_path, name, start_date='20190101', freq='3MS')
    af.japan_extractData(in_path, out_path, name, directory, date='20190922', ty=None, first=13, second=7)


def tohoku():
    # 2_tohokuepco
    u = 'https://setsuden.nw.tohoku-epco.co.jp/common/demand/juyo_%s_tohoku.csv'
    directory = '2_tohokuepco'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date=2019)
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez', first=None, second=None)


def tepco():
    # 3_hepco
    u = 'https://www.tepco.co.jp/forecast/html/images/juyo-%s.csv'
    directory = '3_hepco'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date=2019)
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez', first=None, second=None)


def chuden():
    # 4_chuden
    u = 'https://powergrid.chuden.co.jp/denki_yoho_content_data/download_csv/%s_power_usage.zip'
    directory = '4_chuden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/.*?/(?P<name>.*?)_' % directory, re.S)
    # Download and extract all data
    af.japan_download_Zipformat(u, in_path, name, start_date='20190401', freq='MS')
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='so_ez', first=None, second=None)


def rikuden():
    # 5_rikuden
    u = 'http://www.rikuden.co.jp/nw/denki-yoho/csv/juyo_05_%s.csv'
    directory = '5_rikuden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date='20190101')
    af.japan_extractData(in_path, out_path, name, directory, date='20190929', ty='None', first=13, second=7)


def kansai():
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    # 6_kansai
    u = 'https://www.kansai-td.co.jp/yamasou/%s_jisseki.zip'
    directory = '6_kansai'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?)_' % directory, re.S)
    # Download and extract all data
    af.japan_download_Zipformat(u, in_path, name, start_date='20190101', freq='MS')
    af.japan_extractData(in_path, out_path, name, directory, date='20190911', ty=None, first=16, second=10)


def energia():
    # 7_energia
    u = 'https://www.energia.co.jp/nw/jukyuu/sys/juyo-%s.csv'
    directory = '7_energia'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date=2018)
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez', first=None, second=None)


def yonden():
    # 8_yonden
    u = 'https://www.yonden.co.jp/nw/denkiyoho/csv/juyo_shikoku_%s.csv'
    directory = '8_yonden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date=2019)
    af.japan_extractData(in_path, out_path, name, directory, date=None, ty='ez', first=None, second=None)


def kyuden():
    # 9_kyuden
    u = 'https://www.kyuden.co.jp/td_power_usages/csv/juyo-hourly-%s.csv'
    directory = '9_kyuden'
    in_path = af.japan_path(directory)[0]
    out_path = af.japan_path(directory)[1]
    name = re.compile(r'%s/(?P<name>.*?).csv' % directory, re.S)
    # Download and extract all data
    af.japan_download_Csvformat(u, in_path, name, start_date='20190101')
    af.japan_extractData(in_path, out_path, name, directory, date='20190904', ty='None', first=13, second=7)


if __name__ == '__main__':
    main()
