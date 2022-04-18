#!/usr/bin/env python
# coding: utf-8

# import requests
# import os
# import json
# import pandas as pd
# import re
# import numpy as np
# import sys
# import zipfile
#
# module_path_string = "K:\\Github\\GlobalPowerUpdate-Kow\\code\\global_code"
# sys.in_path.append(module_path_string)
# import global_function as af
#
# # 迅雷下载
# af.xunlei('https://api.eia.gov/bulk/EBA.zip',
#           'K:\\Github\\GlobalPowerUpdate-Kow\\data\\n_america\\us\\craw\\result_1.zip')
#
# # 解压缩zip
# file_path = 'D:\\迅雷下载\\'
# with zipfile.ZipFile(file_path + 'EBA.zip') as zf:
#     zf.extractall(file_path)
#
# name = re.compile(r'from (.*?) for', re.S)
# result = []
#
# # 由于文件中有多行，直接读取会出现错误，因此一行一行读取
# file = open(file_path + 'EBA.txt', 'r', encoding='utf-8')
# for line in file.readlines():  # 读取json数据的每一行（或者说每一个）
#     dic = json.loads(line)
#     if 'Net generation from' in dic['name']:
#         if 'UTC' in dic['name']:
#             df_temp = pd.DataFrame(dic['data'])
#             df_temp.columns = ['datetime', 'net_gen']
#             df_temp['ty'] = name.findall(dic['name'])[0]
#             result.append(df_temp)
# df_result = pd.DataFrame(np.concatenate(result), columns=df_temp.columns)
# df_result = pd.pivot_table(df_result, index='datetime', values='net_gen', columns='ty').reset_index()
# df_result['datetime'] = pd.to_datetime(df_result['datetime'], format='%Y/%m/%d %H:%M:%S')
#
#
# # ###############################################
# # !/usr/bin/env python
# # coding: utf-8
# def main():
#     import requests
#     import json
#     import pandas as pd
#     import re
#     import numpy as np
#
#     # read balancing authorities
#     link = 'https://api.eia.gov/category/?api_key=EM2vJse7LA5vvOBIkerrVOePxAYZDvI8i9TPUCdT&category_id=3390101'
#
#     r = requests.get(link, stream=True)
#     result = bytes.decode(r.content)
#     j = json.loads(result)
#     BAs = j['category']['childcategories'][14:]
#     name = re.compile(r'from (.*?) for', re.S)
#     p1 = re.compile(r'[(](.*?)[)]', re.S)
#     energy_sources = ['COL', 'WAT', 'NG', 'NUC', 'OTH', 'OIL', 'SUN', 'WND']
#
#     file_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\n_america\\us\\raw\\'
#
#     result_data = []
#     for b in BAs:
#         region_id = re.findall(p1, b['name'])[0]
#         for eng in energy_sources:
#             link = 'https://api.eia.gov/series/?api_key=EM2vJse7LA5vvOBIkerrVOePxAYZDvI8i9TPUCdT&series_id=EBA.' + \
#                    region_id + '-ALL.NG.' + eng + '.H'
#             r = requests.get(link, stream=True)
#             result = bytes.decode(r.content)
#             j = json.loads(result)
#             if 'series' in j:
#                 if j['series']:
#                     df_temp = pd.DataFrame(j['series'][0]['data'])
#                     df_temp.columns = ['datetime', 'net_gen']
#                     df_temp['ty'] = name.findall(j['series'][0]['name'])[0]
#                     result_data.append(df_temp)
#     df = pd.DataFrame(np.concatenate(result_data), columns=df_temp.columns)
#     df['datetime'] = pd.to_datetime(df['datetime'], format='%Y/%m/%d %H:%M:%S')
#     df = df.groupby(['datetime', 'ty']).sum().reset_index()
#     df = pd.pivot_table(df, index='datetime', values='net_gen', columns='ty').reset_index()
#     df.to_csv(file_path + 'raw.csv', index=False, encoding='utf_8_sig')
#
#
# if __name__ == '__main__':
#     main()
# # 迅雷下载
# af.xunlei('https://api.eia.gov/bulk/EBA.zip', 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\n_america\\us\\craw'
#                                               '\\result_1.zip')
