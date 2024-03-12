import json
import mysql.connector
import datetime

with open('C:/Users/vonly-ops/Desktop/Biztic VS Code Rohan/January/Week 2/Vs code/seasons.json', encoding='utf-8') as f:
    data = json.load(f)
    
def store_in_database(product_data_list):
    conn = mysql.connector.connect(user='root', password='1234',
                                   host='127.0.0.1', database='md',
                                   auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    a = (datetime.datetime.now())

    

    for product_data in product_data_list:
        if product_data is not None:
            cursor.execute('''
                INSERT INTO promotions (scan_date,portal,depth,category, title, position, content_id, container_type, child_media_type, container_url,created_at,updated_at, detail_page_url,image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now(),%s, %s)
            ''', (product_data[0], product_data[1], product_data[2], product_data[3], product_data[4], product_data[5], product_data[6],product_data[7],product_data[8],product_data[9],product_data[10],product_data[11]))
        else:
            print("Error: product_data is None.")

    conn.commit()
    conn.close()
    

main_table = []

for season in data.get("seasons", []):

    for episode in season.get("episodes", []):
        scan = (datetime.datetime.now())
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
    
    
        img_url = ""
        for url in urls:
            url_type = url.get("type", "")
            url_value = url.get("url", "")

            for Image in Image_urls:
                img_url = Image.get("url","")
                row_1 = (
                    scan,
                    platform,
                    depth,
                    episode_type,
                    episode_name,
                    episode_number,
                    episode_id,
                    url_type,
                    episode_genre,
                    url_value,
                    urls_1,
                    img_url
                )
                break

               
        main_table.append(row_1)
 
    continue

print(main_table)
# store_in_database(main_table)

