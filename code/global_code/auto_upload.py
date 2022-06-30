from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pyautogui
import time
import sys

sys.dont_write_bytecode = True

file_path = './data/global/Global_PM_corT.csv'

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # 打开浏览器
driver.implicitly_wait(60)
driver.get('https://lsce:lsce2021BPwd@staging.datascarbonmonitor.wedodata.dev/admin/')  # 登录网址

driver.find_element(By.XPATH, "//a[@data-source='energy_global']").click()  # 点击energy global这一行
driver.find_element(By.XPATH, "//label[@class='custom-file-upload']").click()  # 点击上传
time.sleep(5)
pyautogui.write(file_path)  # 输入文件
time.sleep(1)
pyautogui.press('enter')  # 点击确定

driver.find_element(By.XPATH, "//button[@class='enabled']").click()  # 点击确认上传
time.sleep(5)
driver.find_element(By.XPATH, "//div[@class='active_radiobt']").click()  # 点击active
time.sleep(5)
driver.close()  # 关闭
