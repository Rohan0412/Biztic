import json

with open('C:/Users/vonly-ops/Desktop/Biztic VS Code Rohan/categories.json', encoding='utf-8') as f:
    data = json.load(f)

def get_all_cat_data(data):
    main_table = []

    for category in data['categories']:
        if 'items' in category:
            for item in category['items']:
                if 'featuredImage' in item:
                    if  str(item['type']) != "series" :
                        continue
                    
                    row_1 = (
                        str(category['name']),
                        str(category['_id']),
                        str(category['plutoOfficeOnly']),
                        str(category['offset']),
                        str(category['page']),
                        str(category['totalItemsCount']),
                        str(item['_id']),
                        str(item['slug']),
                        str(item['name']),
                        str(item['summary']),
                        str(item['description']),
                        str(item['originalContentDuration']),
                        str(item['rating']),
                        str(item['featuredImage']),
                        str(item['genre']),
                        str(item['type']),
                        str(item['seasonsNumbers'])
                    )
                    main_table.append(row_1)
                                        
    return(main_table)

f = get_all_cat_data(data)

list = []

for i in f:
    list.append(i[6])
    
    
# print(list)
    