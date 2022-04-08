# # ====================================================================================
# #                           Interpreter: Python 3.6.1
# #                            Test platform: Mac OS X
# #
# #                                Author: Zhu Deng
# #                           Website: http://zhudeng.top
# #                         Contact Email: zhudeng94@gmail.com
# #                       Created: 2020 08 08 11:36
# # ====================================================================================
#
# import pandas as pd
# from tqdm import tqdm
# import datetime
# import os
# import time
#
# path = 'K:\\Github\\GlobalPowerUpdate-Kow\\data\\europe\\russia\\raw\\'
# if not os.path.exists(path):
#     os.mkdir(path)
# outfile = os.path.join(path, 'Russia_SOUPS_Hourly.csv')
# outfile_correct = os.path.join(path, 'Russia_SOUPS_Hourly (Corrected).csv')
# cols = ['P_AES', 'P_GES', 'P_TES', 'P_BS', 'P_REN']
#
#
# def main():
#     download()
#     correct()
#
#
# def download():
#     # Generation
#     url = 'https://br.so-ups.ru/webapi/Public/Export/Csv/PowerGen.aspx?startDate=%s&endDate=%s' \
#           '&territoriesIds=-1:null&notCheckedColumnsNames='
#
#     startDate = '2015-01-01'
#     endDate = datetime.datetime.utcnow()
#
#     for date in tqdm(pd.date_range(startDate, endDate, freq='7D')):
#
#         sd = date.strftime('%Y.%m.%d')
#         ed = (date + datetime.timedelta(days=6)).strftime('%Y.%m.%d')
#         while True:
#             try:
#                 df = pd.read_csv(url % (sd, ed), sep=';', encoding='windows-1251', decimal=',')
#                 if os.path.exists(outfile):
#                     df.to_csv(outfile, header=False, mode='a', index=False)
#                 else:
#                     df.to_csv(outfile, index=False)
#             except:
#                 time.sleep(10)
#                 print('retry...')
#                 continue
#             break
#
#
# def correct():
#     df = pd.read_csv(outfile)
#     temp = df.copy()
#
#     temp['M_DATE'] = pd.to_datetime(temp['M_DATE'], format='%d.%m.%Y 0:00:00')
#     temp['date'] = [t.strftime('%m%d') for t in temp['M_DATE']]
#
#     temp.loc[temp['M_DATE'] <= '2020-03-23', 'P_TES'] = temp.loc[temp['M_DATE'] <= '2020-03-23', 'P_TES'] * 1.8
#     temp.loc[(temp['date'] <= '0918') & (temp['date'] >= '0501') & (temp['M_DATE'].dt.year < 2020), 'P_TES'] = \
#         temp.loc[(temp['date'] <= '0918') & (temp['date'] >= '0501') & (temp['M_DATE'].dt.year < 2020), 'P_TES'] * 1.3
#
#     temp.index = temp['M_DATE']
#     temp = temp.resample('1D').sum()
#
#     temp[cols].to_csv(outfile_correct)
#
#
# if __name__ == '__main__':
#     main()
