import json
import mysql.connector

with open('C:/Users/vonly-ops/Desktop/Biztic VS Code Rohan/categories.json', encoding='utf-8') as f:
    data = json.load(f)

def store_in_database(product_data_list):
    conn = mysql.connector.connect(user='root', password='1234',
                                   host='127.0.0.1', database='md',
                                   auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    for product_data in product_data_list:
        if product_data is not None:
            cursor.execute('''
                INSERT INTO promotions_1 (slug, name, type, genre, rating, originalContentDuration, description, seasonsNumbers)
                VALUES (%s,%s, %s, %s, %s, %s, %s, %s)
            ''', (product_data[0], product_data[1], product_data[2], product_data[3], product_data[4], product_data[5], product_data[6], product_data[7]))
        else:
            print("Error: product_data is None.")

    conn.commit()
    conn.close()

main_table = []

for category in data['categories']:
    if 'items' in category:
        for item in category['items']:
            if 'featuredImage' in item:
                row = (
                    str(item['slug']),
                    str(item['name']),
                    str(item['type']),
                    str(item['genre']),
                    str(item['rating']),
                    str(item['originalContentDuration']),
                    str(item['description']),
                    str(item['seasonsNumbers'])
                )
                main_table.append(row)

store_in_database(main_table)
