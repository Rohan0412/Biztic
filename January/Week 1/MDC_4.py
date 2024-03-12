import requests
import re
# import urllib.request
# import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# import sqlite3
# import csv
from lxml import etree

import mysql.connector

def store_in_database(product_data_list):
    conn = mysql.connector.connect(user='root', password='1234',
                              host='127.0.0.1', database='md',
                              auth_plugin='mysql_native_password')    
    cursor = conn.cursor()
    
    for product_data in product_data_list:    
        cursor.execute(''' INSERT INTO products (title, price_old, price_new, discount,created_at,updated_at,category) VALUES (%s,%s,%s,%s,now(),now(),%s) ''',( product_data[0], product_data[1], product_data[2],   product_data[3], product_data[4]))

    conn.commit()
    conn.close()


def get_html_code(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# def get_all_links(html_code,url):
        
#     soup = BeautifulSoup(html_code, 'html.parser')

#     dom = etree.HTML(str(soup))

#     list_titles = dom.xpath("//ul[@class='megamenu']/li/a")
    
#     main_links = []

#     for title in list_titles:
#         product_urls = urljoin(url,title.get('href'))
#         main_links.append(product_urls)


#     if not product_urls:
#         print("No product links found.")
    
#     return main_links


def get_prod_links(html_code,url):

    soup = BeautifulSoup(html_code, 'html.parser')

    dom = etree.HTML(str(soup))

    list_titles = dom.xpath("./div[@class='products-list row nopadding-xs']/div/div/div/div/a")

    final_links = []
    
    for i in list_titles:
        product_urls = urljoin(url,i.get('href'))
        final_links.append(product_urls)

    if not final_links:
        print("No product links found.")

    return final_links 


def scrape_product_details(url):
    print("get document for :",url)
    
    next_page_url=''

    pattern = re.compile('(?:.*?)/(.*?)(?:\\?|$)')
    match = re.search(pattern, url)

    if match:
        category = match.group(1)
        # Remove incremental values (if any)
        category = re.sub(r'\d+$', '', category)

    category = category.replace('/mdcomputers.in/','')

    html_code = get_html_code(url)
    
    product_data_list = []
    
    if html_code:
        soup = BeautifulSoup(html_code, 'html.parser')
        
        dom = etree.HTML(str(soup))

        product_list = dom.xpath("//div[@class='products-list row nopadding-xs']/div/div/div/div/a")

        for product in product_list:
            title_elem = product.xpath(".//div[@class='title-product']/h1/span")            
            title = title_elem[0].text.strip() 
            # product_url_elem = product.xpath(".//div[@class='right-block right-b']/h4/a")
            # product_url = product_url_elem[0].get('href').strip() if product_url_elem else 'URL not found'
            price_old_elem = product.xpath(".//span[@class='save-amount-details-prices strike-line']")
            price_old = price_old_elem[0].text.strip() if price_old_elem else 'Old Price not found'
            price_new_elem = product.xpath(".//span[@class='price-new']/span")
            price_new = price_new_elem[0].text.strip()if price_new_elem else 'New Price not found'
            discount_elem =  product.xpath(".//span[@class='discount-percentage']") 
            discount = discount_elem[0].text.strip() if discount_elem else 'Discount not found'            
            # print(f"Title: {title}")
            # print(f"URL: {product_url}")
            # print(f"Old Price: {price_old}")
            # print(f"New Price: {price_new}")
            # print(f"Discount: {discount}")
            product_data = (title, price_old, price_new, discount,category)
            product_data_list.append(product_data)
                       
        store_in_database(product_data_list)
           
        next_page_node = dom.xpath(".//ul[@class='pagination']/li/a")    
        
        for next_link in next_page_node:
            if next_link.text == '>':
               next_page_url = next_link.get('href')
        
        if next_page_url!= '':
            scrape_product_details(next_page_url)
            
    else:
        print("Error: HTML code is not available.")        
    

def scrape_all_details(url):
    html_code = get_html_code(url)
    if html_code:
        # all_urls = get_all_links(html_code,url)
        product_urls = get_prod_links(html_code,url)
        for product_url in product_urls:                
            scrape_product_details(product_url)    
            

main_url = 'https://mdcomputers.in'
scrape_all_details(main_url)