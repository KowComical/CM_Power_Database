# 数据来源 Taochun Sun
import time
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af

# 路径
global_path = './data/n_america/mexicao/'
file_path = os.path.join(global_path, 'craw')
out_path = os.path.join(global_path, 'raw')

# 设置备注
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('--headless')
options.add_argument('--disable-gpu')
# 打开网页
wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # 打开浏览器
wd.get('https://www.cenace.gob.mx/Paginas/SIM/Reportes/EnergiaGeneradaTipoTec.aspx')  # 打开要爬的网址
wd.implicitly_wait(60)
time.sleep(1)
# 点击下载
wd.find_element(By.XPATH, "//*[@name='ctl00$ContentPlaceHolder1$GridRadResultado$ctl00$ctl04$gbccolumn']").click()
time.sleep(5)
# 找到下载的文件
file_name = af.search_file('C:\\')
file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('Generacion Liquidada') != -1]

# 合并新旧文件
df_old = pd.read_csv(os.path.join(file_path, 'history_data.csv'))  # 读取历史数据
df = pd.concat([pd.read_csv(f, header=7) for f in file_name]).reset_index(drop=True)  # 读取最新数据
df_new = pd.concat([df_old, df]).reset_index(drop=True)  # 合并结果
# 去除列名中左边的莫名其妙的空格
for c in df_new.columns:
    df_new = df_new.rename(columns={c: c.lstrip()})
# 清理日期格式
df_new['Dia'] = pd.to_datetime(df_new['Dia'], format='%d/%m/%Y')
df_new['datetime'] = pd.to_datetime(df_new['Dia']) + pd.to_timedelta((df_new['Hora'] - 1), unit='h')  # 小时时间要往前推一个小时
df_new = df_new.drop(columns=['Dia', 'Hora'])
# 删除
df_new = df_new.groupby(['datetime', 'Sistema']).mean().reset_index()  # 数值我看各版本没有差异 这里暂取平均值
df_new.to_csv(os.path.join(file_path, 'out_path.csv'), index=False, encoding='utf_8_sig')
