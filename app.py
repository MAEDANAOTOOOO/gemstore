import streamlit as st
from time import sleep
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 
import datetime as dt

base_url = 'https://gemstore.tokyo/collections/'
dict = {
    'tops':'tops?page={}',
    'outer':'outer?page={}',
    'bottoms':'bottoms?page={}',
    'set-up':'set-up?page={}',
    'shoes':'shoes?page={}',
    'accessory':'accessory?page={}',
    'bag':'bag?page={}',
    'smartphone-case':'smartphone-case?page={}'
}
sec_list = ['tops','outer','bottoms','set-up','shoes','accessory','bag','smartphone-case']

desktop_dir = os.path.expanduser('~/Desktop') 
dt_now = dt.datetime.now()
yyyymmddhhss = dt_now.strftime('%Y%m%d%H%M')
directory_name = u'gemstoreデータ抽出_' + yyyymmddhhss
top_path = f'{desktop_dir}/{directory_name}'
img_path = f'{desktop_dir}/{directory_name}/img'

def make_folder(top_path,img_path):
    os.makedirs(top_path)
    os.makedirs(img_path)

st.title('gemstore データDLアプリ')

sections = st.multiselect('検索したいジャンルを選択してください', 
sec_list , default = sec_list)

if not sections:
    st.error('少なくとも1つ選んでください')
        
section_list = []
for section in sections:
    section_list.append(dict[section])


st.write("#### 希望のダウンロードパターンを選択してください")
st.write("##### パターン①　　所要時間：12時間")
if st.button("CSVと画像データのダウンロード"):
    try:
        st.write("ダウンロードを開始しました")
        make_folder(top_path,img_path)
        st.write("STEP1：格納用フォルダの作成が完了しました。")
        st.write("商品ページURLの取得中です")

        bar = st.progress(0)
        latest_iteration = st.empty()
        goods_list=[]
        for num,section_page in enumerate(section_list):
            bar.progress((num+1)/len(section_list))
            latest_iteration.text(f'{num+1} / {len(section_list)}の計算中')

            section_url = base_url + section_page
            for i in range(1000):
                page_url = section_url.format(i+1)
                page_r = requests.get(page_url)
                page_r.raise_for_status()
                sleep(1)
                page_soup = BeautifulSoup(page_r.content,'lxml')

                if page_soup.select('h2:-soup-contains("商品が見つかりません")') :
                    break

                goods_tags = page_soup.select('ul#product-grid >li>div>div>div.card__content h3>a')
                for goods_tag in goods_tags:
                    goods_list.append(goods_tag.get('href'))

        st.write("STEP2：全商品ページURLの取得が完了しました。")
        st.write(f"アイテム数は{len(goods_list)}個です")
        st.write("STEP3：商品の詳細データをダウンロード中")

        bar = st.progress(0)
        latest_iteration = st.empty()
        item_list = []
        for num,goods in enumerate(goods_list):
            bar.progress((num+1)/len(goods_list))
            latest_iteration.text(f'{num+1} / {len(goods_list)}のダウンロード中')

            goods_url = 'https://gemstore.tokyo' + goods
            goods_r = requests.get(goods_url)
            goods_r.raise_for_status()
            sleep(1)
            soup = BeautifulSoup(goods_r.content,'lxml')
            
            title = soup.select_one('div.product__info-wrapper h1.product__title').text
            title = title.replace('\n','')
            title = title.strip()
            name = title[-6:]
            
            price = soup.select_one('div.price__regular span.price-item').text
            price = price.replace('\n','')
            price = price.strip()
            
            color_tags = soup.select('div.product__info-wrapper fieldset:-soup-contains("カラー") input')
            color_list =[]
            for color_tag in color_tags:
                color = color_tag['value']
                color_list.append(color)
            colors = '・'.join(color_list)       
            
            size_tags = soup.select('div.product__info-wrapper fieldset:-soup-contains("サイズ") input')
            size_list =[]
            for size_tag in size_tags:
                size = size_tag['value']
                size_list.append(size)
            sizes = '・'.join(size_list)

            snipet_tags = soup.select('div.product__description')
            snipet_list = []
            for snipet_tag in snipet_tags:
                snipet = snipet_tag.text
                snipet_list.append(snipet)
            snipets = '。'.join(snipet_list) 
            snipets = snipets.replace('\n','')
            snipets = snipets.replace('続きを読む','')
            snipets = snipets.strip()
                
            img_tags = soup.select('div.product__media-wrapper slider-component:first-of-type>ul>li>div img')
            sku_list = []
            for img_tag in img_tags:
                sku_img = 'https:' + img_tag.get('src')
                sku_list.append(sku_img)

            i = 1
            for target in sku_list:
                re = requests.get(target)
                sleep(1)
                with open(f'{img_path}/{name}_{i}.jpeg','wb') as f:
                    f.write(re.content)
                i += 1
            
            item_list.append({
                '商品名':title,
                '価格':price,
                '色':colors,
                'サイズ':sizes,
                '商品概要':snipets
            })      
        df = pd.DataFrame(item_list)
        df.to_csv(f'{top_path}/gemstoreデータ抽出.csv',index=None,encoding='utf-8-sig')

        st.write("ダウンロードが成功しました")

    except:
        st.error('エラーが起きています。コードを確認してください')

st.write("##### パターン②　　所要時間：2時間")
if st.button("CSVのみダウンロード"):
    try:
        st.write("ダウンロードを開始しました")

        make_folder(top_path,img_path)
        st.write("STEP1：格納用フォルダの作成が完了しました。")
        st.write("商品ページURLの取得中です")

        bar = st.progress(0)
        latest_iteration = st.empty()
        goods_list=[]
        for num,section_page in enumerate(section_list):
            bar.progress((num+1)/len(section_list))
            latest_iteration.text(f'{num+1} / {len(section_list)}の計算中')

            section_url = base_url + section_page
            for i in range(1000):
                page_url = section_url.format(i+1)
                page_r = requests.get(page_url)
                page_r.raise_for_status()
                sleep(1)
                page_soup = BeautifulSoup(page_r.content,'lxml')

                if page_soup.select('h2:-soup-contains("商品が見つかりません")') :
                    break

                goods_tags = page_soup.select('ul#product-grid >li>div>div>div.card__content h3>a')
                for goods_tag in goods_tags:
                    goods_list.append(goods_tag.get('href'))
        st.write("STEP2：全商品ページURLの取得が完了しました。")
        st.write(f"アイテム数は{len(goods_list)}個です")
        st.write("STEP3：商品の詳細データをダウンロード中")
        bar = st.progress(0)
        latest_iteration = st.empty()
        item_list = []
        for num,goods in enumerate(goods_list):
            bar.progress((num+1)/len(goods_list))
            latest_iteration.text(f'{num+1} / {len(goods_list)}のダウンロード中')

            goods_url = 'https://gemstore.tokyo' + goods
            goods_r = requests.get(goods_url)
            goods_r.raise_for_status()
            sleep(1)
            soup = BeautifulSoup(goods_r.content,'lxml')
            
            title = soup.select_one('div.product__info-wrapper h1.product__title').text
            title = title.replace('\n','')
            title = title.strip()
            name = title[-6:]
            
            price = soup.select_one('div.price__regular span.price-item').text
            price = price.replace('\n','')
            price = price.strip()
            
            color_tags = soup.select('div.product__info-wrapper fieldset:-soup-contains("カラー") input')
            color_list =[]
            for color_tag in color_tags:
                color = color_tag['value']
                color_list.append(color)
            colors = '・'.join(color_list)       
            
            size_tags = soup.select('div.product__info-wrapper fieldset:-soup-contains("サイズ") input')
            size_list =[]
            for size_tag in size_tags:
                size = size_tag['value']
                size_list.append(size)
            sizes = '・'.join(size_list)

            snipet_tags = soup.select('div.product__description')
            snipet_list = []
            for snipet_tag in snipet_tags:
                snipet = snipet_tag.text
                snipet_list.append(snipet)
            snipets = '。'.join(snipet_list) 
            snipets = snipets.replace('\n','')
            snipets = snipets.replace('続きを読む','')
            snipets = snipets.strip()
            
            item_list.append({
                '商品名':title,
                '価格':price,
                '色':colors,
                'サイズ':sizes,
                '商品概要':snipets
            })      
        df = pd.DataFrame(item_list)
        df.to_csv(f'{top_path}/gemstoreデータ抽出.csv',index=None,encoding='utf-8-sig')

        st.write("ダウンロードが成功しました")

    except:
        st.error('エラーが起きています。コードを確認してください')