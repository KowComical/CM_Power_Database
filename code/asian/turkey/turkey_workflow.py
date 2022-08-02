# 数据来源 Zhu Deng
import time
import re
import os
import pandas as pd
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys

sys.dont_write_bytecode = True
sys.path.append('K:\\Github\\CM_Power_Database\\code\\')
from global_code import global_function as af
from global_code import global_all as g

# 路径
file_path = 'K:\\Github\\CM_Power_Database\\data\\asia\\turkey\\'
craw_path = os.path.join(file_path, 'craw')
raw_path = os.path.join(file_path, 'raw')

# 筛选已下载的文件 只看hourly里的就行
file_name = af.search_file(craw_path)
file_name = [file_name[i] for i, x in enumerate(file_name) if not x.find('trans') != -1]
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('hourly') != -1]
date_name = re.compile(r'hourly\\.*?\\(?P<name>.*?).csv', re.S)

existing_date = []
for f in file_name:
    existing_date.append(date_name.findall(f)[0])
# 日期区间
start_date = '2017-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')
date_range = pd.date_range(start_date, end_date, freq='d').strftime('%Y-%m-%d')[:-1]  # 不要最后一天
date_range = [i for i in date_range if i not in existing_date]  # 筛掉已下载的

# 设置备注
name = re.compile(r'NETICESI_(?P<name>.*?).xlsx', re.S)
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('--headless')
options.add_argument('--disable-gpu')
prefs = {"download.default_directory": craw_path}
options.add_experimental_option("prefs", prefs)


def main():
    craw()  # 爬取数据 必须要土耳其IP
    craw_to_raw()  # 清洗数据
    g.turkey()  # 处理数据

    af.updated_date('Turkey')  # 提取最新日期 还没做好这里


def craw():
    # 打开网页
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # 打开浏览器
    wd.get('https://ytbsbilgi.teias.gov.tr/ytbsbilgi/frm_istatistikler.jsf')  # 打开要爬的网址
    wd.implicitly_wait(60)
    time.sleep(1)
    # 进入网址点一下确认按钮
    wd.find_elements(By.XPATH, "//*[contains(text(), 'Kabul Et ve Devam Et')]")[0].click()
    time.sleep(5)

    for d in date_range:
        try:
            # 输入所需日期
            inputElement = wd.find_element(By.ID, 'formdash:bitisTarihi2_input')
            time.sleep(1)
            wd.execute_script("arguments[0].value = ''", inputElement)
            time.sleep(1)
            inputElement.send_keys(d)
            time.sleep(1)
            wd.find_element(By.LINK_TEXT, str(int(d[-2:]))).click()  # 确认日期
            time.sleep(1)
            # 下载文件
            wd.find_element(By.XPATH, "//*[@name='formdash:j_idt42']").click()
            time.sleep(20)
        except:  # 有时会莫名其妙让你再点一下确认
            wd.find_elements(By.XPATH, "//*[contains(text(), 'Kabul Et ve Devam Et')]")[0].click()
            print('%s - 未下载' % d)
            time.sleep(5)


def craw_to_raw():
    # 读取翻译文档
    trans = pd.read_csv(os.path.join(craw_path, 'trans.csv'))
    craw_name = af.search_file(craw_path)
    craw_name = [craw_name[i] for i, x in enumerate(craw_name) if not x.find('trans') != -1]
    craw_name = [craw_name[i] for i, x in enumerate(craw_name) if not x.find('hourly') != -1]
    craw_name = [craw_name[i] for i, x in enumerate(craw_name) if not x.find('region') != -1]
    if craw_name:  # 如果有新文件
        #  输出文件
        df_hourly = pd.DataFrame()
        df_region = pd.DataFrame()
        for cr in craw_name:
            # 小时数据
            temp_hourly = pd.read_excel(cr, sheet_name='Rapor329', header=2)
            temp_hourly = temp_hourly[temp_hourly['BİRİM'] == 'MWH'].reset_index(drop=True)  # 只要数据
            temp_hourly = temp_hourly[~temp_hourly['KAYNAK ADI'].isin(['TOPLAM', 'TALEP TAHMİN'])].reset_index(
                drop=True)  # 只要分能源数据
            # 提取日期
            date_list = name.findall(cr)[0]
            date_year = pd.to_datetime(date_list).strftime('%Y')
            temp_hourly['date'] = date_list  # 添加日期
            # 输出craw数据
            hourly_path = os.path.join(craw_path, 'hourly', '%s' % date_year)  # 按照年份分类
            if not os.path.exists(hourly_path):  # 如果未生成就生成文件夹
                os.mkdir(hourly_path)
            temp_hourly.to_csv(os.path.join(hourly_path, '%s.csv' % date_list), index=False, encoding='utf_8_sig')
            df_hourly = pd.concat([df_hourly, temp_hourly]).reset_index(drop=True)  # 将结果储存到df中

            # 区域数据
            temp_region = pd.read_excel(cr, sheet_name='Rapor277', header=3).drop(columns=['PUANT ZAMANI'])
            temp_region['date'] = date_list  # 添加日期
            # 输出region数据
            region_path = os.path.join(craw_path, 'region', '%s' % date_year)  # 按照年份分类
            if not os.path.exists(region_path):  # 如果未生成就生成文件夹
                os.mkdir(region_path)
            temp_region.to_csv(os.path.join(region_path, '%s.csv' % date_list), index=False, encoding='utf_8_sig')
            df_region = pd.concat([df_region, temp_region]).reset_index(drop=True)
            # 添加完就删掉
            os.remove(cr)
        # 清洗hourly数据
        df_hourly = df_hourly.set_index(['date', 'KAYNAK ADI', 'KURULU GÜÇ', 'BİRİM']).stack().reset_index().rename(
            columns={'level_4': 'hour', 0: 'mwh'})
        df_hourly['hour'] = df_hourly['hour'].str.replace(':00', '').astype(int) - 1
        df_hourly['datetime'] = pd.to_datetime(df_hourly['date']) + pd.to_timedelta((df_hourly['hour']), unit='h')
        # 整理列名 装机功率暂时删掉 KURULU GÜÇ
        df_hourly = df_hourly.rename(columns={'KAYNAK ADI': 'sector'}).drop(columns=['KURULU GÜÇ', 'BİRİM'])[
            ['datetime', 'sector', 'mwh']]
        # 将土耳其语翻译成英文
        # 先将不能翻译的改一下名
        df_hourly['sector'] = df_hourly['sector'].str.replace('ASFALTİT KÖMÜR', 'Asfaltit')
        df_hourly['sector'] = df_hourly['sector'].str.replace('Asfaltit Kömür', 'Asfaltit')
        df_hourly['sector'] = df_hourly['sector'].str.replace('Barajlı', 'BARAJLI')
        df_hourly['sector'] = df_hourly['sector'].str.replace('Tas Kömür', 'TAŞ KÖMÜR')

        df_result_hourly = pd.merge(df_hourly, trans).sort_values('datetime').reset_index(drop=True)[
            ['datetime', 'english', 'mwh']]
        # 列转行
        df_result_hourly = pd.pivot_table(df_result_hourly, index='datetime', values='mwh',
                                          columns='english').reset_index()
        df_result_hourly.to_csv(os.path.join(raw_path, 'hourly.csv'), index=False, encoding='utf_8_sig')
        # 清洗region数据 # 其实屁都没清理。。。
        df_result_region = pd.pivot_table(df_region, index='date', values='BÖLGE PUANTI (MW)',
                                          columns='BÖLGE ADI').reset_index()
        df_result_region.to_csv(os.path.join(raw_path, 'region.csv'), index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
