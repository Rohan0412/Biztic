import requests
import json
import re

from lxml import etree
import mysql.connector

import re
import datetime

from json_scrape_6 import list

def store_in_database(product_data_list):
    conn = mysql.connector.connect(user='root', password='1234',
                                   host='127.0.0.1', database='md',
                                   auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    for product_data in product_data_list:
        if product_data is not None:
            cursor.execute('''
                INSERT INTO episodes( scan_date, portal, show_title, episode_title, season_number, episode_number, portal_item_id, content_id, image_url, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
            ''', (product_data[0], product_data[1], product_data[2], product_data[3], product_data[4], product_data[5], product_data[6], product_data[7],product_data[8]))
        else:
            print("Error: product_data is None.")

    conn.commit()
    conn.close()
    
main_table = []
def get_all_data(data):
    
    series_name = data.get("name","")

    for season in data.get("seasons", []):

        for episode in season.get("episodes", []):
            scan = 'yes'
            portal = 'Pluto TV'
            depth = '1'
            scan = (datetime.datetime.now())
            episode_type = episode.get("type", "")
            episode_name = episode.get("name", "")        
            episode_number = episode.get("number", "")
            episode_id = episode.get("_id", "")
            episode_genre = episode.get("genre", "")
            Image_urls = episode.get("covers", {})
            urls = episode.get("stitched", {}).get("urls", [])
            urls_1 = episode.get("stitched", {}).get("sessionURL", [])
            episode_season = episode.get("season", "")

        
            img_url = ""
            for url in urls:
                url_type = url.get("type", "")
                url_value = url.get("url", "")

                for Image in Image_urls:
                    img_url = Image.get("url","")
                    row_1 = (
                        scan,
                        portal,
                        series_name,
                        episode_name,                        
                        episode_season,
                        episode_number,
                        episode_id,
                        url_type,
                        img_url
                        # depth,                        
                        # episode_genre,
                        # url_value,
                        # urls_1,                        
                        # episode_type,
                        
                    )

                
            main_table.append(row_1)
    
        continue

    return(0)


set = set(list)

# no_of_series = len(set)
# no_of_seasons = len(list)
# print("total no. of series =",no_of_series)
# print("total no. of seasons =",no_of_seasons)

# main = []


# r = 0
for id in set:
    # r = r + 1
    url = 'https://api.pluto.tv/v3/vod/series/{}/seasons?deviceType=web'.format(id)
    print(url)
    response = requests.get(url)
    # print(response)
    data = response.json()    
    total = get_all_data(data)
    # main.append(total)
    #print(main_table)
    
    # if r == 5:
    #     break
    
#print(type(main))
store_in_database(main_table)



