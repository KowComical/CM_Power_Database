# 数据来源 Taochun Sun
import time
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys

sys.dont_write_bytecode = True
sys.path.append('./code/')
from global_code import global_function as af

end_year = int(datetime.now().strftime('%Y'))  # 当前年
end_date = (pd.to_datetime(datetime.now().strftime('%Y%m%d')) + relativedelta(months=1)).strftime('%Y-%m')  # 当前月加一个月

# 路径
global_path = './data/s_america/chile/'
file_path = os.path.join(global_path, 'craw')
out_path = os.path.join(global_path, 'raw')
# 读取已下载的
file_name = af.search_file(file_path)
year_list = []
month_list = []
for y in range(2012, end_year + 1):
    for m in range(0, 12):
        test_date = '%s-%s' % (y, m + 1)
        if not [file_name[i] for i, x in enumerate(file_name) if x.find(test_date) != -1]:  # 如果还没下载
            year_list.append(y)
            month_list.append(m)


def main():
    craw()
    craw_to_raw()


def craw():
    # 设置备注
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-ssl-errors=yes')  # 这两条会解决页面显示不安全问题
    options.add_argument('--ignore-certificate-errors')
    prefs = {"download.default_directory": file_path}
    options.add_experimental_option("prefs", prefs)
    # 打开网页
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # 打开浏览器
    wd.get('https://www.coordinador.cl/operacion/graficos/operacion-real/generacion-real/')  # 打开要爬的网址
    wd.implicitly_wait(60)
    time.sleep(1)

    # 模拟下载
    for ye, mo in zip(year_list, month_list):
        new_date = '%s-%s' % (ye, str(mo + 1).zfill(2))
        if new_date < end_date:
            wd.find_element(By.XPATH, "//*[@id='datepicker777-519_2']").click()  # 点击选日期
            wd.find_element(By.XPATH, "//*[@value=%s]" % str(ye)).click()  # 选择年
            wd.find_element(By.XPATH, "//option[@value=%s]" % str(mo)).click()  # 选择月
            wd.find_element(By.XPATH,
                            "//button[@class='ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all']").click()  # 点击确定
            wd.find_element(By.XPATH, "//input[@id='tipo-xlsx']").click()  # 选择xlsx格式
            wd.find_element(By.XPATH,
                            "//*[@class='cen_btn cen_btn-primary cen_reset-margin download-file-marginal']").click()  # 点击下载
            time.sleep(5)


def craw_to_raw():
    # 清理craw
    df = pd.concat([pd.read_excel(f, header=3) for f in file_name]).reset_index(drop=True)
    df = df.drop(columns=['Total', 'Hora 25', 'Coordinado', 'Tipo', 'Grupo reporte', 'Llave', 'Central'])
    df = df[df['Central'] != 'Total'].reset_index(drop=True)
    df = df.groupby(['Subtipo', 'Fecha']).sum().reset_index()
    # 行转列
    df = df.set_index(['Subtipo', 'Fecha']).stack().reset_index().rename(columns={'level_2': 'hour', 0: 'mwh'})
    df['hour'] = df['hour'].str.replace('Hora ', '').astype(int)
    df['datetime'] = pd.to_datetime(df['Fecha']) + pd.to_timedelta((df['hour'] - 1), unit='h')  # 小时时间要往前推一个小时
    df = df.drop(columns=['Fecha', 'hour'])
    # 列转行
    df = pd.pivot_table(df, index='datetime', values='mwh', columns='Subtipo').reset_index()
    # 删掉最后一天的数据 不准确
    now = datetime.now().strftime('%Y-%m-%d')
    df = df[df['datetime'] < now].reset_index(drop=True)
    # 改名
    df = df.rename(columns={'Biomasa': 'biomass', 'Carbón': 'coal',
                            'Cogeneracion': 'cogeneration', 'Diésel': 'diesel',
                            'Embalse': 'reservoir', 'Eólica': 'wind', 'Geotérmica': 'geothermal',
                            'Pasada': 'pass'})
    # 输出
    df.to_csv(os.path.join(out_path, 'raw_data.csv'), index=False, encoding='utf_8_sig')
    # 删除最后一个月的数据
    os.remove(max(file_name))


if __name__ == '__main__':
    main()
