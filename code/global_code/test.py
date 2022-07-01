from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import sys

sys.getdefaultencoding()
sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af
import time
import os
import pandas as pd
import logging

logging.getLogger('WDM').setLevel(logging.NOTSET)  # 关闭运行chrome时的打印内容

# 修改默认下载路径
c_options = webdriver.ChromeOptions()
download_path = 'C:\\'
prefs = {'download.default_directory': download_path}
c_options.add_experimental_option('prefs', prefs)

# 开始模拟
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=c_options)  # 打开浏览器

driver.implicitly_wait(60)
driver.get('https://lsce:lsce2021BPwd@staging.datascarbonmonitor.wedodata.dev/admin/')  # 登录网址

driver.find_element(By.XPATH, "//a[@data-source='energy_global']").click()  # 点击energy global这一行
time.sleep(5)
driver.find_element(By.XPATH, "//a[@class='row_downloadbt']").click()

#
file_name = af.search_file(download_path)
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('energy_global_datas') != -1]
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('csv') != -1][0]
df = pd.read_csv(file_name)
out_path = './data/'
df.to_csv(os.path.join(out_path, 'test.csv'), index=False, encoding='utf_8_sig')
