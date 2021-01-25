# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 19:24:23 2020

@author: seiji
"""
import time,re,datetime,csv,random,requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
# Selectタグが扱えるエレメントに変化させる為の関数を呼び出す
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pc_max_k

id_visual = pc_max_k.id_ps_m[2][0]
ps = pc_max_k.id_ps_m[2][1]

url = "https://pcmax.jp/pcm/member.php"

while True:
    # ログイン
    print("開始 pc max")
    print(datetime.datetime.now())

    driver = webdriver.Chrome()
    driver.get(url)  # アドレスを開く
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 0);")  # 先頭にスクロール
    driver.find_element_by_id("login-tab").click()  # 登録済みの方
    time.sleep(2)

    driver.find_element_by_css_selector("#login-tab").click()  # 登録済みの方
    driver.find_element_by_name('login_id').send_keys(id_visual)  # idを入力
    time.sleep(1)  # 待つ
    driver.find_element_by_name('login_pw').send_keys(ps)  # passを入力
    time.sleep(1)  # 待つ
    driver.find_element_by_name("login").click()  # ログイン
    time.sleep(5)  # 待つ
    WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located)  # 待つ
    ###################################################################
    # 検索
    try:
        time.sleep(6)
        driver.find_element_by_css_selector(
            ".header-nav-a.header-nav-a4"
            ).click()
    except:
        driver.find_element_by_id("cp_can").click()
        time.sleep(3)
        driver.find_element_by_css_selector(".header-nav-a.header-nav-a4").click()

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located)#待つ
    # 年齢のドロップダウンリスト入力
    time.sleep(5)
    from_age=driver.find_element_by_id('commondityItem')
    from_age_a=Select(from_age)
    from_age_a.select_by_value("18")

    to_age=driver.find_element_by_id('makerItem')
    to_age_a=Select(to_age)
    to_age_a.select_by_value("25")

    time.sleep(3.5) # 待つ
    driver.find_element_by_css_selector("#image_button").click()#検索実行

    # 1ページ27件、強制スクロール2回で計81件取得
    for i in range(2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1) # 待つ

    pcmax_source = driver.page_source
    soup = BeautifulSoup(pcmax_source, 'html.parser')
    sp_naiyou=soup.find_all("div",class_="list")

    name_s_regex_sp= re.compile(r'(\s)+') #スペースタグ改行の削除
    name_style=re.compile(r'<style>[\s\S]*?</style>')#styleタグ(？)を削除
    name_end_regex_sp= re.compile(r'&amp;search')#idの後ろを置き換え
    name_start_regex_sp= re.compile(r'profile_detail.php\?user_id=')#idの前を置き換え
    name_diary_regex_sp= re.compile(r'diary_write.png')#日記アリを置き換え
    name_keiji_regex_sp= re.compile(r'document_letter_edit')#掲示板アリを置き換え
    name_wakaba_regex_sp= re.compile(r'wakaba.gif')#掲示板アリを置き換え
    name_nanika_regex_sp= re.compile(r'<.*?>')
            # リストを作成
    p_sp=[]
    for f in sp_naiyou:
        g=name_start_regex_sp.sub(">id:",str(f))#idのまえに「id:」を挿入
        g0=name_style.sub("",g)
        h0=name_end_regex_sp.sub(" 名前:<",g0)#idのあとに(名前の前に)「_名前：」を挿入
        h1=name_diary_regex_sp.sub(" >日記:0<",h0)#     
        h2=name_keiji_regex_sp.sub(" >掲示板:0<",h1)#  
        h3=name_wakaba_regex_sp.sub(" >若葉：0<",h2)#  
        i=name_nanika_regex_sp.sub("",h3)
        j=name_s_regex_sp.sub(" ",i)
        p_sp.append(j)
        
    #ID取得
    id_list=[]
    re_id=re.compile(r'id:(\d{6,8})')
    for id_ in p_sp:
        p_id=re_id.findall(id_)
        # findallはリストを返すのでインデックスを指定
        id_list.append(p_id[0])
    
    #リスト用日時作成
    d_t=datetime.datetime.now()
    jikoku=d_t.strftime('%Y-%m-%d %H:%M:%S')
    
    # lp01はループ01という意味
    purofu=[]
    for lp01 in range(len(p_sp)):
        purofu.append([jikoku,lp01+1,id_list[lp01],p_sp[lp01]])
    
    with open('pcmax_02.csv', 'a', encoding='CP932', errors='replace',newline='') as f:
        writer = csv.writer(f)
        writer.writerows(purofu)
        
    #画像の取得 img タグを含むものを取得しプロフの画像のみを選別
    sp_naiyou_gazou=soup.find_all("img")
    gazou_url_list01=[]
    for ga01 in sp_naiyou_gazou:
        if "copyright=" in str(ga01):
            gazou_url_list01.append(ga01)
    
     #画像の取得 上のリストからリクエストのURLのリストを作成
    gazou_url_list02=[]
    for ga02 in range(0,len(gazou_url_list01)):
        ga03 = gazou_url_list01[ga02].get('src')
        gazou_url_list02.append(ga03)
    
    #ファイル名にするためIDを取得
    id_list_g=[]
    id_list_sub=[]
    #    まず、"copyright=" があるブロックを抽出
    for ids in sp_naiyou:
        if "copyright=" in str(ids):
            id_list_sub.append(ids)
    #　　　ブロックからidを抽出
    re_rist=re.compile(r'(?<=id=)(.*)(?=&amp;search)')
    for id01 in range(len(id_list_sub)):
        a01=re_rist.search(str(id_list_sub[int(id01)]))
        id_list_g.append(a01.group())  
            
    output_folder= Path(r'C:\Users\seiji\Downloads\pc_max')
    # requestsに突っ込むためのクッキーを取得
    cookies = driver.get_cookies()
    # セッションid(SID)はインデックス[0]
    cookie ={cookies[0]["name"]:cookies[0]["value"]}
        
    for i001 in range(0,len(gazou_url_list02)):
        image =requests.get(gazou_url_list02[int(i001)],cookies=cookie)
        save_path=output_folder.joinpath((r"{}.jpg").format(id_list_g[int(i001)]))
        open(save_path, 'wb').write(image.content)
        time.sleep(0.05)
        
    driver.quit()
    
    print("終了")
    
    print(datetime.datetime.now())
    
    #次の時間までスリープ
    s_num=random.randint(0,1200)#60*20 0-20分のランダムな秒数
    kankaku_junkou=2#巡行間隔を時間単位で指定
    tugino_jikoku=datetime.datetime.now()+datetime.timedelta(minutes=s_num/60+(kankaku_junkou*60)-10)
    #上の数字に間隔時間ｘ60を足したものから10（分）を引く
    kettei_kankaku_fun=((kankaku_junkou*3600+s_num-600)//60)
    print("次のデータ取得は{1:}分後、{0:%H}時{0:%M}分です".format(tugino_jikoku,kettei_kankaku_fun))
    
    time.sleep(kankaku_junkou*3600+s_num-600)