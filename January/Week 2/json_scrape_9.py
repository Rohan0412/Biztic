import requests
import json
import re

from lxml import etree
import mysql.connector

import re
import datetime

with open('C:/Users/vonly-ops/Desktop/Biztic VS Code Rohan/peacock.json', encoding='utf-8') as f:
    data = json.load(f)

print(data)


# main_table = []
# def get_all_data(data):
    
#     series_name = data.get("name","")

#     for season in data.get("seasons", []):

#         for episode in season.get("episodes", []):
#             scan = 'yes'
#             portal = 'Pluto TV'
#             depth = '1'
#             scan = (datetime.datetime.now())
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
#                     img_url = Image.get("url","")
#                     row_1 = (
#                         scan,
#                         portal,
#                         series_name,
#                         episode_name,                        
#                         episode_season,
#                         episode_number,
#                         episode_id,
#                         url_type,
#                         img_url
#                         # depth,                        
#                         # episode_genre,
#                         # url_value,
#                         # urls_1,                        
#                         # episode_type,
                        
#                     )

                
#             main_table.append(row_1)
    
#         continue

#     return(0)


# set = set(list)

# # no_of_series = len(set)
# # no_of_seasons = len(list)
# # print("total no. of series =",no_of_series)
# # print("total no. of seasons =",no_of_seasons)

# # main = []


# # r = 0
# for id in set:
#     # r = r + 1
#     url = 'https://api.pluto.tv/v3/vod/series/{}/seasons?deviceType=web'.format(id)
#     print(url)
#     response = requests.get(url)
#     # print(response)
#     data = response.json()    
#     total = get_all_data(data)
#     # main.append(total)
#     #print(main_table)
    
#     # if r == 5:
#     #     break
    
# #print(type(main))
# store_in_database(main_table)



