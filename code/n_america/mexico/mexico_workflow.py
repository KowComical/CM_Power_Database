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
from global_code import global_all as g

# 路径
global_path = './data/n_america/mexico/'
file_path = os.path.join(global_path, 'craw')
out_path = os.path.join(global_path, 'raw')


def main():
    # 数据爬取
    craw()
    # 数据预处理
    craw_to_raw()
    # 数据处理并输出
    g.mexico()
    # 提取最新日期
    af.updated_date('Mexico')


def craw():
    # 设置备注
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    prefs = {"download.default_directory": file_path}
    options.add_experimental_option("prefs", prefs)
    # 打开网页
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # 打开浏览器
    wd.get('https://www.cenace.gob.mx/Paginas/SIM/Reportes/EnergiaGeneradaTipoTec.aspx')  # 打开要爬的网址
    wd.implicitly_wait(60)
    time.sleep(1)

    wd.find_element(By.XPATH,
                    "//*[@name='ctl00$ContentPlaceHolder1$GridRadResultado$ctl00$ctl04$gbccolumn']").click()  # 点击下载
    time.sleep(10)

    file_name = af.search_file(file_path)
    file_name = [file_name[i] for i, x in enumerate(file_name) if not x.find('history') != -1]

    df_new = pd.concat([pd.read_csv(f, header=7) for f in file_name]).reset_index(drop=True).fillna(0)  # 读取最新数据
    # 去除列名中左边的莫名其妙的空格
    for c in df_new.columns:
        df_new = df_new.rename(columns={c: c.lstrip()})
    # 清理日期格式
    df_new['Dia'] = pd.to_datetime(df_new['Dia'], format='%d/%m/%Y')
    df_new['datetime'] = pd.to_datetime(df_new['Dia']) + pd.to_timedelta((df_new['Hora'] - 1), unit='h')  # 小时时间要往前推一个小时
    df_new = df_new.drop(columns=['Dia', 'Hora'])

    df_old = pd.read_csv(os.path.join(file_path, 'history_data.csv'))  # 读取历史数据
    df_new = pd.concat([df_old, df_new]).reset_index(drop=True)  # 合并结果
    df_new['datetime'] = pd.to_datetime(df_new['datetime'])
    df_new = df_new.groupby(['datetime', 'Sistema']).mean().reset_index()  # 数值我看各版本没有差异 这里暂取平均值
    df_new.to_csv(os.path.join(file_path, 'history_data.csv'), index=False, encoding='utf_8_sig')
    # 删除新下载的文件
    for f in file_name:
        os.remove(f)


def craw_to_raw():
    df_history = pd.read_csv(os.path.join(file_path, 'history_data.csv'))
    # 处理能源类型
    df_history = df_history.rename(columns={'Eolica': 'wind', 'Fotovoltaica': 'solar',
                                            'Biomasa': 'biomass', 'Carboelectrica': 'coal',
                                            'Geotermoelectrica': 'geothermal', 'Hidroelectrica': 'hydro',
                                            'Nucleoelectrica': 'nuclear',
                                            'Termica Convencional': 'conventional thermal', 'Sistema': 'system',
                                            'Turbo Gas': 'gas', 'Ciclo Combinado': 'combined cycle',
                                            'Combustion Interna': 'internal combustion'})
    # 能源类型汇总
    df_history['coal'] = df_history['coal']
    df_history['gas'] = df_history['gas'] + df_history['combined cycle']
    df_history['oil'] = df_history['internal combustion'] + df_history['conventional thermal']
    df_history['nuclear'] = df_history['nuclear']
    df_history['hydro'] = df_history['hydro']
    df_history['wind'] = df_history['wind']
    df_history['solar'] = df_history['solar']
    df_history['other'] = df_history['biomass'] + df_history['geothermal']
    col_list = ['datetime', 'coal', 'gas', 'oil', 'solar', 'wind', 'hydro', 'nuclear', 'other']
    df_history = df_history[col_list]
    df_history.to_csv(os.path.join(out_path, 'raw_data.csv'), index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    main()
