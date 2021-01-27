import time,re,datetime,csv,random,requests
from selenium import webdriver
import chromedriver_binary #  mac用
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
# Selectタグが扱えるエレメントに変化させる為の関数を呼び出す
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
#import pc_max_k

#id_visual = pc_max_k.id_ps_m[2][0]
#ps = pc_max_k.id_ps_m[2][1]

url = "https://pcmax.jp/pcm/member.php"

# ログイン
print("開始 pc max")
print(datetime.datetime.now())

driver = webdriver.Chrome()
driver.get(url)  # アドレスを開く
time.sleep(2)
