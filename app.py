import streamlit as st
from time import sleep
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 
import datetime as dt
import numpy as np

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

st.title('gemstore データDLアプリ')

sections = st.multiselect('検索したいジャンルを選択してください', 
sec_list , default = sec_list)
if not sections:
    st.error('少なくとも1つ選んでください')
        
section_list = []
for section in sections:
    section_list.append(dict[section])


if st.button("ダウンロードデータの生成"):
    try:
        st.write("ダウンロードを開始しました")
        st.write("STEP1：商品ページURLの取得中です")

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
                goods_tags = page_soup.select('div#ProductGridContainer ul#product-grid >li>div>div>div.card__content h3>a')
                for goods_tag in goods_tags:
                    goods_list.append(goods_tag.get('href'))

        st.write("全商品ページURLの取得が完了しました。")
        st.write(f"アイテム数は{len(goods_list)}個です")
        st.write("STEP2：商品の詳細データを取得中です")

        bar = st.progress(0)
        latest_iteration = st.empty()
        item_list = []
        df_obj = pd.DataFrame()
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
            
            df1 = pd.DataFrame(sku_list,columns=[title])
            df1.index = np.arange(1,len(df1)+1)
            df1 = df1.T
            df1 = df1.add_prefix("SKU画像_")
            df_obj = pd.concat([df_obj,df1])

            item_list.append({
                '商品名':title,
                '価格':price,
                '色':colors,
                'サイズ':sizes,
                '商品概要':snipets
            })  

        df2 = pd.DataFrame(item_list)
        # df_objの型をdf2に合わせる
        df_obj = df_obj.reset_index().rename(columns={'index':'商品名'})
        # df_objとdf2をマージする
        merge_df = df2.merge(df_obj)
        csv = merge_df.to_csv().encode('utf-8')

        st.write("ダウンロードデータの生成が完了しました")

    except:
        st.error('エラーが起きています。コードを確認してください')

st.download_button(
    label = 'Download data as CSV',
    data = csv,
    file_name=f'{directory_name}.csv',
    mime='text/csv',
)