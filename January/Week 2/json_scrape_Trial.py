import requests
import json
import re

from lxml import etree
import mysql.connector

import re
from datetime import datetime

from json_scrape_6 import list

def store_in_database(product_data_list, max_platform_length=50):
    conn = mysql.connector.connect(user='root', password='1234',
                                   host='127.0.0.1', database='md',
                                   auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    for product_data in product_data_list:
        
            
        cursor.execute('''
            INSERT INTO tv_shows(platform,depth,episode_type,episode_name,episode_number,episode_id,url_type,episode_genre,episode_season)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (product_data[0], product_data[1], product_data[2], product_data[3], product_data[4], product_data[5], product_data[6], product_data[7],product_data[8]))
        
    conn.commit()
    conn.close()

# def get_all_data(data):
#     main_table = []

#     for season in data.get("seasons", []):

#         for episode in season.get("episodes", []):
#             scan = 'yes'
#             platform = 'Pluto TV'
#             depth = '1'
#             episode_type = episode.get("type", "")
#             episode_name = episode.get("name", "")
#             episode_number = episode.get("number", "")
#             episode_id = episode.get("_id", "")
#             episode_genre = episode.get("genre", "")
#             Image_urls = episode.get("covers", {})
#             urls = episode.get("stitched", {}).get("urls", [])
#             urls_1 = episode.get("stitched", {}).get("sessionURL", [])
#             episode_season = episode.get("season", "")

#             img_url = ""
#             for url in urls:
#                 url_type = url.get("type", "")
#                 url_value = url.get("url", "")

#                 for Image in Image_urls:
#                     img_url = Image.get("url", "")
#                     row_1 = (
#                         platform,
#                         depth,
#                         episode_type,
#                         episode_name,
#                         episode_number,
#                         episode_id,
#                         url_type,
#                         episode_genre,
#                         episode_season
#                     )

#             main_table.append(row_1)

#     return main_table

set_ids = set(list)

r = 0
for show_id in set_ids:
    r = r + 1
    url = 'https://api.pluto.tv/v3/vod/series/{}/seasons?deviceType=web'.format(show_id)
    print(url)
    response = requests.get(url)
    data = response.json()
    # print(data)
    # total = get_all_data(data)
    # print(total)

    main_table_1 = []
    for season in data.get("seasons", []):
        for episode in season.get("episodes", []):
            scan = 'yes'
            platform = 'Pluto TV'
            depth = '1'
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
                    img_url = Image.get("url", "")
                    row_1 = (
                        platform,
                        depth,
                        episode_type,
                        episode_name,
                        episode_number,
                        episode_id,
                        url_type,
                        episode_genre,
                        episode_season
                    )
                    main_table_1.append(row_1)

    if r == 3:
        break

main_table_1 = [tuple(map(str, item)) for item in main_table_1]

# Now you can use `main_table_1` for further processing or store it in the database
# print(main_table_1)
    

# print(main_table_1)

# main_table_1 = [tuple(map(str, item)) for item in main_table_1]

store_in_database(main_table_1)
