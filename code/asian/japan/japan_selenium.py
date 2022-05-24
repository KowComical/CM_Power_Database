from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import sys
import re

sys.dont_write_bytecode = True

sys.path.append('./code/')
from global_code import global_function as af


def main():
    japan_selenium()


def japan_selenium():
    # chrome驱动路径
    chromedriver = './data/#global_rf/selenium/chromedriver.exe'  # chrome路径
    # 修改默认下载路径
    c_options = webdriver.ChromeOptions()
    out_path = './data/asia/japan/raw/month/'
    download_path = 'C:\\'
    # file_path = af.create_folder(download_path, 'kow')
    prefs = {'download.default_directory': download_path}
    c_options.add_experimental_option('prefs', prefs)

    # 判断是否更新了新的文件需要下载
    file_name = af.search_file(out_path)

    name = re.compile(r'month/(?P<name>.*?)_', re.S)  # 从路径找出国家
    date = [name.findall(f)[0] for f in file_name]
    date = max(date)
    date = '%s年%s月' % (date[:4], int(date[-2:]))

    # 开始模拟
    wd = webdriver.Chrome(chromedriver, options=c_options)  # 打开浏览器
    wd.get('https://occtonet3.occto.or.jp/public/dfw/RP11/OCCTO/SD/LOGIN_login#')  # 打开要爬的网址
    # 不知道为啥每次都会自动弹出另外一个不需要的窗口 所以先把不需要的关掉
    # noinspection PyBroadException
    try:
        handles = wd.window_handles
        wd.switch_to.window(handles[1])
        wd.close()  # 转到不需要的窗口并关闭
        wd.switch_to.window(handles[0])  # 切回原来的窗口
    except:
        pass
    wd.implicitly_wait(60)
    wd.find_element(By.ID, 'menu1-6').click()
    wd.find_element(By.ID, 'menu1-6-3-1').click()
    handles = wd.window_handles
    wd.switch_to.window(handles[1])  # 切到需要的窗口

    select = Select(wd.find_element(By.ID, 'ktgr'))
    select.select_by_value('7')  # 从下拉菜单里选取需要的数据内容
    wd.find_element(By.ID, 'searchBtn').click()

    # 如果要下载的月份文件已经存在了 则pass
    test = wd.find_element(By.ID, 'table3_rows_0__infNm')
    if date in test.text:
        print('还未更新')
    else:
        print('start download...')
        wd.find_element(By.ID, 'table3_rows_0__pdfCsvBtn').click()
        time.sleep(10)
        # 找到确认下载并点击确认
        confirm_text = 'ui-button-text'
        wd.find_elements(By.CLASS_NAME, confirm_text)[2].click()
        time.sleep(30)
        upload_github(chromedriver, download_path)
    wd.quit()


def upload_github(chromedriver, download_path):
    # 定位到下载的文件
    print('start searching file...')
    file_name = af.search_file(download_path)
    print('finding needed file...')
    file_name = [file_name[i] for i, x in enumerate(file_name) if x.find('csv') != -1][0]
    # 模拟上传到github
    driver = webdriver.Chrome(chromedriver)
    time.sleep(1)
    driver.get('https://github.com/login')
    time.sleep(3)
    # 定位并输入账号密码
    login = driver.find_element(By.NAME, 'login')
    password = driver.find_element(By.NAME, 'password')
    time.sleep(0.5)

    login.send_keys('KowComical')
    time.sleep(1)
    password.send_keys('Xuanrenkow1122')
    time.sleep(1)

    button = driver.find_element(By.NAME, 'commit')
    button.click()
    time.sleep(2)

    driver.get('https://github.com/KowComical/CM_Power_Database/upload/master/data/asia/japan/raw/month')

    upload_file = driver.find_element(By.XPATH, '//*[@id="upload-manifest-files-input"]')
    upload_file.send_keys(file_name)
    time.sleep(10)

    commit_upload = driver.find_element(By.XPATH, '//*[@id="js-repo-pjax-container"]/div[2]/div/form/button')
    commit_upload.click()
    time.sleep(5)
    driver.quit()


if __name__ == '__main__':
    main()
