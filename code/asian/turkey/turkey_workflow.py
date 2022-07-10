# 数据来源 Zhu Deng
import time
import re
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

# 路径
file_path = 'K:\\Github\\CM_Power_Database\\data\\asia\\turkey\\craw\\'
file_name = af.search_file(file_path)
name = re.compile(r'NETICESI_(?P<name>.*?).xlsx', re.S)
# 筛选已下载的文件
existing_date = []
for f in file_name:
    existing_date.append(name.findall(f)[0])
# 日期区间
start_date = '2017-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')
date_range = pd.date_range(start_date, end_date, freq='d').strftime('%Y-%m-%d')[:-1]  # 不要最后一天
date_range = [i for i in date_range if i not in existing_date]  # 筛掉已下载的

# 设置备注
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('--headless')
options.add_argument('--disable-gpu')
prefs = {"download.default_directory": file_path}
options.add_experimental_option("prefs", prefs)
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
