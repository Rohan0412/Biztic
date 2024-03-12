from flask import Flask
from flask import request
import mysql.connector
from mysql.connector import Error

# Mounting the drive
#from google.colab import drive
#drive.mount('/content/drive')

# Required Basic libraries
import uuid
import pandas as pd
import os
import requests
#from PIL import Image ,ImageOps
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv2
#from google.colab.patches import cv2_imshow
import math
from tqdm import tqdm
import datetime as dt
from scipy import stats
#from skimage import transform
from scipy.spatial.distance import hamming,cosine

# Tensorflow functions
#import tensorflow as tf
#from tensorflow.keras import datasets,layers,Model,optimizers,metrics
#from tensorflow.keras.layers import Dense,Input,Conv2D,MaxPool2D,Activation,Dropout,Flatten,BatchNormalization
#from tensorflow.keras.callbacks import ModelCheckpoint
from datetime import datetime


# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.
#@app.route('/')
@app.route('/index')
def index():
    # Render the page
    page_content = ""
    page_content += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "    
    page_content += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"
    page_content += """<body vLink="white"><table class=customers >"""
    page_content += "<tr>"
    page_content += """<th><a href=/dashboard target=_blank > Dashboard</a></th>"""
    page_content += """<th><a href=/mapping target=_blank > Mapping</a></th>"""
    page_content += """<th><a href=/aps target=_blank > APS</a></th>"""
    page_content += """<th><a href=/checktitle target=_blank > Search By Title</a></th>"""
    page_content += """<th><a href=/check target=_blank > Search By VONLY Asset ID </a></th>"""
    page_content += """<th><a href=/verify target=_blank > WB Mapping Verification </a></th>"""    
    page_content += """<th><a href=/findimdb target=_blank > Find IMDB </a></th>"""    
    page_content += "</tr>"
    page_content += "</table></body>"

    return page_content

# for resetting the Tensorflow graph
os.environ['PYTHONHASHSEED'] = '0'
#tf.keras.backend.clear_session()
# for reproducible result
np.random.seed(0)
# image Size and channels
HEIGHT = 224
WIDTH = 224
NUM_CHANNELS = 3
# loading VGG19 weight of Imagenet Dataset
#base_model = tf.keras.applications.vgg19.VGG19(input_shape=(HEIGHT, WIDTH, NUM_CHANNELS), weights='imagenet') 
# DEFINING The Model such that instead of classification it results the output
# of flatten layer Which we will use as image vector
#model = Model(inputs=base_model.input, outputs=base_model.get_layer("flatten").output)

# Main Directory for the project
PROJ_PATH = '.'

temp_path = os.path.join(PROJ_PATH,'image') #setting image directory inside proj directory to download images for
                                            #comparison
def Image_vector(img_name):
  """ I/p : image name ,O/P : binary vector of image base on gradient"""
  img = cv2.imread(img_name) # reading the image
  std_size = (HEIGHT,WIDTH) # size of image
  rsz_img = cv2.resize(img, std_size, interpolation = cv2.INTER_AREA).astype(np.uint8) # resizing the image and changing dtype to unsigned int8
  vector = model.predict(rsz_img.reshape(1,224,224,3))[0] # Getting the image vector form vgg model that we defined above
  grad = np.diff(vector) #getting the grad
  grad = grad > 0 # #apling the boolean function on gradient values
  return grad


def getColor(value):
    color = ""
    if value <= 25:
        color = "#ff0000"
    if value > 25 and value <= 75:
        color = "#ffb629"
    if value > 75:
        color = "#22b14c"
    return color

def Generate_Main_Table(connection,portal):
    sql_statistics_Query = """SELECT distributed_by_parent,SUM(perc_100),SUM(perc_80), SUM(perc_60),SUM(perc_40),SUM(perc_20),SUM(perc_0), SUM(Bundle),SUM(Total),
                                concat('<a target=_blank href=http://192.168.100.118:4449/drill?portal=%s&studio=',distributed_by_parent,'&percentage=100&bundle=0 >',SUM(perc_100),'</a>'),
                                concat('<a target=_blank href=http://192.168.100.118:4449/drill?portal=%s&studio=',distributed_by_parent,'&percentage=80&bundle=0 >',SUM(perc_80),'</a>'),
                                concat('<a target=_blank href=http://192.168.100.118:4449/drill?portal=%s&studio=',distributed_by_parent,'&percentage=60&bundle=0 >',SUM(perc_60),'</a>'),
                                concat('<a target=_blank href=http://192.168.100.118:4449/drill?portal=%s&studio=',distributed_by_parent,'&percentage=40&bundle=0 >',SUM(perc_40),'</a>'),
                                concat('<a target=_blank href=http://192.168.100.118:4449/drill?portal=%s&studio=',distributed_by_parent,'&percentage=20&bundle=0 >',SUM(perc_20),'</a>'),
                                concat('<a target=_blank href=http://192.168.100.118:4449/drill?portal=%s&studio=',distributed_by_parent,'&percentage=0&bundle=0 >',SUM(perc_0),'</a>')                                
                                FROM (
                                SELECT distributed_by_parent, 
                                sum(CASE WHEN percentage = 100 THEN 1 ELSE 0 END) perc_100 ,
                                sum(CASE WHEN percentage = 80 THEN 1 ELSE 0 END) perc_80 ,
                                sum(CASE WHEN percentage = 60 THEN 1 ELSE 0 END) perc_60 ,
                                sum(CASE WHEN percentage = 40 THEN 1 ELSE 0 END) perc_40 ,
                                sum(CASE WHEN percentage = 20 THEN 1 ELSE 0 END) perc_20 ,
                                sum(CASE WHEN percentage = 0 THEN 1 ELSE 0 END) perc_0 , 
                                0 Bundle,
                                0 Total
                                FROM (
                                SELECT mminner.distributed_by_parent,mi.vonly_asset_id, (
                                SELECT COUNT(DISTINCT portal)
                                FROM movie_ids
                                WHERE portal NOT IN ('%s','wb upc','wb mpm-vvid') AND vonly_asset_id =mi.vonly_asset_id) * 20 AS 'percentage'
                                FROM movie_ids mi
                                INNER JOIN pricm_staging.movies mminner ON mi.portal = mminner.portal and mi.region = mminner.region and mi.portal_item_id = mminner.portal_item_id
                                WHERE mi.platform='%s' AND mi.is_bundle=0
                                GROUP BY mi.vonly_asset_id, mminner.distributed_by_parent) per
                                GROUP BY distributed_by_parent
                                UNION
                                SELECT distributed_by_parent,0,0,0,0,0,0, COUNT(*) Bundle,0
                                FROM (
                                SELECT mminner.distributed_by_parent,mi.vonly_asset_id, (
                                SELECT COUNT(DISTINCT portal)
                                FROM movie_ids
                                WHERE portal NOT IN ('%s','wb upc','wb mpm-vvid') AND vonly_asset_id =mi.vonly_asset_id) * 20 AS 'percentage'
                                FROM movie_ids mi
                                INNER JOIN pricm_staging.movies mminner ON mi.portal = mminner.portal and mi.region = mminner.region and mi.portal_item_id = mminner.portal_item_id
                                WHERE mi.platform='%s' AND mi.is_bundle=1
                                GROUP BY mi.vonly_asset_id, mminner.distributed_by_parent) per
                                GROUP BY distributed_by_parent
                                UNION
                                SELECT distributed_by_parent,0,0,0,0,0,0,0, COUNT(*) Total
                                FROM (
                                SELECT mminner.distributed_by_parent,mi.vonly_asset_id, (
                                SELECT COUNT(DISTINCT portal)
                                FROM movie_ids
                                WHERE portal NOT IN ('%s','wb upc','wb mpm-vvid') AND vonly_asset_id =mi.vonly_asset_id) * 20 AS 'percentage'
                                FROM movie_ids mi
                                INNER JOIN pricm_staging.movies mminner ON mi.portal = mminner.portal and mi.region = mminner.region and mi.portal_item_id = mminner.portal_item_id
                                WHERE mi.platform='%s' 
                                GROUP BY mi.vonly_asset_id, mminner.distributed_by_parent) per
                                GROUP BY distributed_by_parent
                                )
                                a GROUP BY distributed_by_parent """ % (portal,portal,portal,portal,portal,portal,portal,portal,portal,portal,portal,portal)
    print(sql_statistics_Query)
    def_cursor = connection.cursor()        
    def_cursor.execute(sql_statistics_Query)
    records = def_cursor.fetchall()       
    
    page_content = "<center> <table class=customers ><caption>" + portal + " Title Mapping </caption><TR><Th>Studio</Th><Th>100%</Th><Th>80%</Th><Th>60%</Th><Th>40%</Th><Th>20%</Th><Th>Unmapped</Th><Th># Bundles</Th><Th># Titles</Th><Th>100% Portal Mapped</Th><Th>80% or More Portal Mapped</Th><Th>60% or More Portal Mapped</Th><Th>40% or More Portal Mapped</Th><Th>20% or More Portal Mapped</Th><Th>% Unmapped</Th></TR>"
    
    per_100 = 0
    per_80 = 0
    per_60 = 0
    per_40 = 0
    per_20 = 0
    per_unmapped = 0
    bundle = 0
    title = 0
    portal_100 = 0
    portal_80 = 0
    portal_60 = 0
    portal_40 = 0
    portal_20 = 0
    portal_unmapped = 0

    for row in records:      

        portal_100 = round((((row[1] + row[7]) * 100) / row[8]),2)
        portal_80 = round((((row[1] + row[2] + row[7]) * 100) / row[8]),2)
        portal_60 = round((((row[1] + row[2] + row[3] + row[7]) * 100) / row[8]),2)
        portal_40 = round((((row[1] + row[2] + row[3] + row[4] + row[7]) * 100) / row[8]),2)
        portal_20 = round((((row[1] + row[2] + row[3] + row[4] + row[5] + row[7]) * 100) / row[8]),2)
        portal_unmapped = round((((row[6]) * 100) / row[8]),2)

        page_content += "<TR >"
        page_content += "<TD ><B>" + str(row[0]) + "<B></TD>"
        page_content += "<TD nowrap align=right><a  onclick=\"form_submit('" + portal + "','" + str(row[0]) + "',100,0)\" > " + f'{row[1]:,}' + "</a></TD>"
        page_content += "<TD nowrap align=right><a  onclick=\"form_submit('" + portal + "','" + str(row[0]) + "',80,0)\" > " + f'{row[2]:,}' + "</a></TD>"
        page_content += "<TD nowrap align=right><a  onclick=\"form_submit('" + portal + "','" + str(row[0]) + "',60,0)\" > " + f'{row[3]:,}' + "</a></TD>"
        page_content += "<TD nowrap align=right><a  onclick=\"form_submit('" + portal + "','" + str(row[0]) + "',40,0)\" > " + f'{row[4]:,}' + "</a></TD>"
        page_content += "<TD nowrap align=right><a  onclick=\"form_submit('" + portal + "','" + str(row[0]) + "',20,0)\" > " + f'{row[5]:,}' + "</a></TD>"
        page_content += "<TD nowrap align=right><a  onclick=\"form_submit('" + portal + "','" + str(row[0]) + "',0,0)\" > " + f'{row[6]:,}' + "</a></TD>"
        page_content += "<TD nowrap align=right>" + f'{row[7]:,}'  + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{row[8]:,}'  + "</TD>"
        page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_100) + " 1%,white " + str(portal_100) + "%);' >" + str(portal_100) + "%</TD>"
        page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_80) + " 1%,white " + str(portal_80) + "%);' >" + str(portal_80) + "%</TD>"
        page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_60) + " 1%,white " + str(portal_60) + "%);' >" + str(portal_60) + "%</TD>"
        page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_40) + " 1%,white " + str(portal_40) + "%);' >" + str(portal_40) + "%</TD>"
        page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_20) + " 1%,white " + str(portal_20) + "%);' >" + str(portal_20) + "%</TD>"
        page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_unmapped) + " 1%,white " + str(portal_unmapped) + "%);' >" + str(portal_unmapped) + "%</TD>"
        page_content += "</TR>"

        per_100 = per_100 + row[1]
        per_80 = per_80 + row[2]
        per_60 = per_60 + row[3]
        per_40 = per_40 + row[4]
        per_20 = per_20 + row[5]
        per_unmapped = per_unmapped + row[6]
        bundle = bundle + row[7]
        title = title + row[8]
    
    portal_100 = round((((per_100 + bundle) * 100) / title),2)
    portal_80 = round((((per_100 + per_80 + bundle) * 100) / title),2)
    portal_60 = round((((per_100 + per_80 + per_60 + bundle) * 100) / title),2)
    portal_40 = round((((per_100 + per_80 + per_60 + per_40 + bundle) * 100) / title),2)
    portal_20 = round((((per_100 + per_80 + per_60 + per_40 + per_20 + bundle) * 100) / title),2)
    portal_unmapped = round((((per_unmapped) * 100) / title),2)

    page_content += "<TR >"
    page_content += "<TD ><B>Over All<B></TD>"
    page_content += "<TD nowrap align=right>" + f'{per_100:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" +  f'{per_80:,}'+ "</TD>"
    page_content += "<TD nowrap align=right>" +  f'{per_60:,}'+ "</TD>"
    page_content += "<TD nowrap align=right>" +  f'{per_40:,}'+ "</TD>"
    page_content += "<TD nowrap align=right>" +  f'{per_20:,}'+ "</TD>"
    page_content += "<TD nowrap align=right>" +  f'{per_unmapped:,}'+ "</TD>"
    page_content += "<TD nowrap align=right>" +  f'{bundle:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" +  f'{title:,}' + "</TD>"
    page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_100) + " 1%,white " + str(portal_100) + "%);' >" + str(portal_100) + "%</TD>"
    page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_80) + " 1%,white " + str(portal_80) + "%);' >" + str(portal_80) + "%</TD>"
    page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_60) + " 1%,white " + str(portal_60) + "%);' >" + str(portal_60) + "%</TD>"
    page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_40) + " 1%,white " + str(portal_40) + "%);' >" + str(portal_40) + "%</TD>"
    page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_20) + " 1%,white " + str(portal_20) + "%);' >" + str(portal_20) + "%</TD>"
    page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(portal_unmapped) + " 1%,white " + str(portal_unmapped) + "%);' >" + str(portal_unmapped) + "%</TD>"
    page_content += "</TR>"

    #page_content += "<TR ><TD >Total " + studio + " titles</TD><TD nowrap
    #align=right>" + str(total_movies) + "</TD><TD nowrap
    #align=right></TD></TR>"
    page_content += "</table></centre><BR>"
    return page_content

def Generate_Top_Table(connection,studio,portal):
    sql_statistics_Query = """SELECT count(1)
                              FROM (
                              SELECT mi.vonly_asset_id, (SELECT COUNT(DISTINCT portal) FROM movie_ids WHERE portal NOT IN ('%s','wb upc','wb mpm-vvid') AND vonly_asset_id =mi.vonly_asset_id) * 20 AS 'percentage'
                              FROM movie_ids mi
                              INNER JOIN movie_metadata mminner ON mi.id = mminner.vonly_id  AND mminner.search_date='2020-03-16'                                
                              WHERE mi.platform='%s'  AND mminner.distributed_by_parent='%s' and mi.is_bundle=0
                              GROUP BY mi.vonly_asset_id) per """ % (portal,portal,studio)
    print(sql_statistics_Query)
    def_cursor = connection.cursor()        
    def_cursor.execute(sql_statistics_Query)
    records = def_cursor.fetchall()
    
    for row in records:
        total_movies = row[0]
    
    sql_statistics_Query = """SELECT percentage, COUNT(1)
                              FROM (
                              SELECT mi.vonly_asset_id, (SELECT COUNT(DISTINCT portal) FROM movie_ids WHERE portal NOT IN ('%s','wb upc','wb mpm-vvid') AND vonly_asset_id =mi.vonly_asset_id) * 20 AS 'percentage'
                              FROM movie_ids mi
                              INNER JOIN movie_metadata mminner ON mi.id = mminner.vonly_id  AND mminner.search_date='2020-03-16'                                
                              WHERE mi.platform='%s'  AND mminner.distributed_by_parent='%s' and mi.is_bundle=0
                              GROUP BY mi.vonly_asset_id) per
                              GROUP BY percentage order by 1 desc""" % (portal,portal,studio)
    print(sql_statistics_Query)
    def_cursor = connection.cursor()
    def_cursor.execute("SET SESSION group_concat_max_len = 1000000000;")
    def_cursor.execute(sql_statistics_Query)
    records = def_cursor.fetchall()
    
    page_content = "<td><center> <h3>" + portal + " title Mapping for " + studio + "</h3><table border=2 ><TR><Th>Percentage Mapped</Th><Th># Titles</Th><Th>% of Titles</Th></TR>"
    
    for row in records:
        page_content += "<TR ><TD >" + str(row[0]) + "</TD><TD nowrap align=right>" + str(row[1]) + "</TD><TD nowrap align=right>" + str(round(row[1] * 100 / total_movies,2)) + "</TD></TR>"
    
    page_content += "<TR ><TD >Total " + studio + " titles</TD><TD nowrap align=right>" + str(total_movies) + "</TD><TD nowrap align=right></TD></TR>"
    page_content += "</table></centre></td>"
    return page_content

@app.route('/drill', methods=['GET', 'POST'])
def drill():
    # Render the page
    page_content_check = ""
    page_content_check += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content_check += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "    
    page_content_check += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"
    
    if request.method == 'POST':     
        
        studio = request.form['studio']
        portal = request.form['portal']
        percentage = request.form['percentage']
        bundle = request.form['bundle']

        print(studio)
        print(portal)
        print(percentage)
        print(bundle)

        page_content_check += "<script> function form_submit_vonly_asset_id(vonly_asset_id) { document.forms[0].tag.value=vonly_asset_id; document.forms['vonly_asset_id'].submit();} </script> <form method=POST name=vonly_asset_id action=/check target=_blank ><input type=hidden name=tag></form> "
        page_content_check += "<script> function form_submit_title(title) {  document.forms['main'].tag.value=title; document.forms['main'].submit();} </script> <form method=POST name=main action=/checktitle target=_blank ><input type=hidden name=tag></form> "

        try:
            connection_check = mysql.connector.connect(host='192.168.12.102',
                                             database='vonly_data_feed_us_staging',
                                             user='vonly-agent',
                                             password='a714fded-311c-4215-8b8b-5df4086e264b')


            sql_select_Query_check = """  SELECT mminner.distributed_by_parent,mi.vonly_asset_id,title,mi.portal_item_id, (
                                SELECT COUNT(DISTINCT portal)
                                FROM movie_ids
                                WHERE portal NOT IN ('%s','wb upc','wb mpm-vvid') AND vonly_asset_id =mi.vonly_asset_id) * 20 AS 'percentage',
                                (SELECT COUNT(1) FROM movie_ids WHERE portal ='iTunes' AND vonly_asset_id =mi.vonly_asset_id) iTunes,
                                (SELECT COUNT(1) FROM movie_ids WHERE portal ='VUDU' AND vonly_asset_id =mi.vonly_asset_id) VUDU,
                                (SELECT COUNT(1) FROM movie_ids WHERE portal ='Google Play' AND vonly_asset_id =mi.vonly_asset_id) Google,
                                (SELECT COUNT(1) FROM movie_ids WHERE portal ='YouTube' AND vonly_asset_id =mi.vonly_asset_id) YouTube,
                                (SELECT COUNT(1) FROM movie_ids WHERE portal ='Amazon Prime Video' AND vonly_asset_id =mi.vonly_asset_id) Amazon,
                                (SELECT COUNT(1) FROM movie_ids WHERE portal ='Amazon Movies & TV' AND vonly_asset_id =mi.vonly_asset_id) APS,
                                (SELECT COUNT(1) FROM movie_ids WHERE portal ='WB MPM-VVId' AND vonly_asset_id =mi.vonly_asset_id) MPM,
                                (SELECT COUNT(1) FROM movie_ids WHERE portal ='WB UPC' AND vonly_asset_id =mi.vonly_asset_id) UPC
                                FROM movie_ids mi
                                INNER JOIN pricm_staging.movies mminner ON mi.portal = mminner.portal and mi.region = mminner.region and mi.portal_item_id = mminner.portal_item_id
                                WHERE mi.platform='%s' AND mminner.distributed_by_parent='%s' AND mi.is_bundle=%s
                                GROUP BY mi.vonly_asset_id, mminner.distributed_by_parent 
                                HAVING percentage=%s limit 1000 """ % (portal,portal,studio,bundle,percentage)
            print(sql_select_Query_check)
            cursor_check = connection_check.cursor()
            cursor_check.execute("SET SESSION group_concat_max_len = 1000000000;")
            cursor_check.execute(sql_select_Query_check)
            records_check = cursor_check.fetchall()

            page_content_check += "<table class=customers ><CAPTION>Portal:"+portal +" Studio:"+studio +" Percentage:"+ percentage +"</CAPTION><TR><TH>#</TH><TH>Studio</TH><TH>VONLY Asset ID</TH><TH>Title</TH><TH>Portal Item ID</TH><TH>iTunes</TH><TH>VUDU</TH><TH>Google Play</TH><TH>YouTube</TH><TH>Amazon Prime Video</TH><TH>Amazon Movies & TV</TH><TH>WB MPM-VVID</TH><TH>WB UPC</TH><TH>Total Match</TH></TR>"
            #page_content = "<TD>iTunes Images</TD><TD>Amazon
            #Images</TD><TD>VUDU Images</TD><TD>Google Images</TD><TD>YouTube
            #Images</TD><TD>APS Images</TD></TR>"
       
            # print("\nPrinting each Movid ID record")
            i = 1
            for row in records_check:
                page_content_check += "<TR><TD>" + str(i) + "</TD> <TD >" + str(row[0]) + "</TD><TD nowrap> <a  onclick=form_submit_vonly_asset_id('" + str(row[1]) + "') >" + str(row[1]) + " </a> </TD>"
                page_content_check += "<TD> <a  onclick=\"form_submit_title('" + str(row[2]).replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%") + "')\" >" + str(row[2]) + "</a></TD>"
                page_content_check += "<TD>" + str(row[3]) + "</TD>"                
                page_content_check += "<TD>" + str(("","X")[row[5] == 0] ) + "</TD>"
                page_content_check += "<TD>" + str(("","X")[row[6] == 0] ) + "</TD>"
                page_content_check += "<TD>" + str(("","X")[row[7] == 0] ) + "</TD>"
                page_content_check += "<TD>" + str(("","X")[row[8] == 0] )+ "</TD>"
                page_content_check += "<TD>" + str(("","X")[row[9] == 0] ) + "</TD>"
                page_content_check += "<TD>" + str(("","X")[row[10] == 0] ) + "</TD>"
                page_content_check += "<TD>" + str(("","X")[row[11] == 0] ) + "</TD>"
                page_content_check += "<TD>" + str(("","X")[row[12] == 0] ) + "</TD>"
                page_content_check += "<TD>" + str(str(row[4]).count(",")) + "</TD>"        
                i = i + 1

            page_content_check += "</table>"
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if (connection_check.is_connected()):
                connection_check.close()
                cursor_check.close()
                print("MySQL connection is closed")

    return page_content_check

@app.route('/aps_update', methods=['GET', 'POST'])
def aps_update():
    page_content_check = ""
    try:
            connection_check = mysql.connector.connect(host='192.168.12.102',
                                             database='vonly_data_feed_us_staging',
                                             user='vonly-agent',
                                             password='a714fded-311c-4215-8b8b-5df4086e264b')

            cursor_check = connection_check.cursor()
            i=0;
            for key, value in request.form.items():           
                if value == 'on': 
                    cursor_check.execute(key)                
                    i = i + 1
                    connection_check.commit()


            page_content_check += str(i) + " vonly_asset_id updated."

    except Error as e:
            print("Error reading data from MySQL table", e)
    finally:
            if (connection_check.is_connected()):
                connection_check.commit()
                connection_check.close()
                cursor_check.close()
                print("MySQL connection is closed")

    return page_content_check

@app.route('/aps', methods=['GET', 'POST'])
def aps():
    # Render the page
    page_content_check = """<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script> 
    <script type="text/javascript">
        $(document).ready(function(){
            $('#select_all').on('click',function(){
                if(this.checked){
                    $('.checkbox').each(function(){
                        this.checked = true;
                    });
                }else{
                     $('.checkbox').each(function(){
                        this.checked = false;
                    });
                }
            });
    
            $('.checkbox').on('click',function(){
                if($('.checkbox:checked').length == $('.checkbox').length){
                    $('#select_all').prop('checked',true);
                }else{
                    $('#select_all').prop('checked',false);
                }
            });
        });
        </script>
    """
    page_content_check += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content_check += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "    
    page_content_check += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"
    
    page_content_check += "<script> function form_submit_vonly_asset_id(vonly_asset_id) { document.forms[0].tag.value=vonly_asset_id; document.forms['vonly_asset_id'].submit();} </script> <form method=POST name=vonly_asset_id action=/check target=_blank ><input type=hidden name=tag></form> "
    page_content_check += "<script> function form_submit_title(title) {  document.forms['main'].tag.value=title; document.forms['main'].submit();} </script> <form method=POST name=main action=/checktitle target=_blank ><input type=hidden name=tag></form> "
    page_content_check += "<script> function form_submit_aps() {   document.forms['aps'].submit();} </script>"
    page_content_check += "<script> function form_myform_submit() {   form_submit_aps();document.forms['myform'].submit();} </script> "


    if request.method == 'POST':     
        
        #studio = request.form['studio']
        #portal = request.form['portal']
        #percentage = request.form['percentage']
        #bundle = request.form['bundle']

        #print(studio)
        #print(portal)
        #print(percentage)
        #print(bundle)     
        #
        tag = request.form['title']  

        print(tag)

        try:
            connection_check = mysql.connector.connect(host='192.168.12.102',
                                                database='vonly_data_feed_us_staging',
                                                user='vonly-agent',
                                                password='a714fded-311c-4215-8b8b-5df4086e264b')

            sql_select_Query_check = """ SELECT min_title,min_vonly_asset_id,concat('<a href=https://amazon.com/dp/',min_portal_item_id,' target=_blank>', min_portal_item_id ,'</a>') ,m.distributed_by_parent,m.director,m.us_dvd_release_date,
                                        max_title,max_vonly_asset_id, concat('<a href=https://amazon.com/dp/',max_portal_item_id,' target=_blank>', max_portal_item_id ,'</a>') max_portal_item_id
                                        ,n.distributed_by_parent, n.director,n.us_dvd_release_date,
                                        (
                                        SELECT COUNT(1)
                                        FROM movie_ids
                                        WHERE vonly_asset_id=min_vonly_asset_id) min_id_count,
                                        (
                                        SELECT COUNT(1)
                                        FROM movie_ids
                                        WHERE vonly_asset_id=max_vonly_asset_id) max_id_count,
                                        (SELECT image_url FROM movie_metadata mm WHERE mm.portal='amazon movies & tv' AND region='us' and  mm.portal_item_id=min_portal_item_id AND mm.search_date='2020-03-15'),
                                        (SELECT image_url FROM movie_metadata mm WHERE mm.portal='amazon movies & tv' AND region='us' and mm.portal_item_id=max_portal_item_id AND mm.search_date='2020-03-15')                                                                                
                                        FROM 
                                        (
                                        SELECT * FROM (
                                        SELECT title min_title,COUNT(1) min_count,MIN(vonly_asset_id) min_vonly_asset_id, MIN(portal_item_id) min_portal_item_id FROM movie_ids WHERE portal='amazon movies & tv'  
                                        and title like '%s'
                                        GROUP BY title HAVING COUNT(DISTINCT vonly_asset_id)=2 
                                        ) a
                                        INNER JOIN 
                                        (
                                        SELECT title max_title,COUNT(1) max_count, MAX(vonly_asset_id) max_vonly_asset_id, max(portal_item_id) max_portal_item_id FROM movie_ids WHERE portal='amazon movies & tv' 
                                        and title like '%s'
                                        GROUP BY title HAVING COUNT(DISTINCT vonly_asset_id)=2 
                                        ) b ON a.min_title=b.max_title 
                                        ) per 
                                        LEFT OUTER JOIN pricm_staging.movies m ON per.min_portal_item_id=m.portal_item_id AND m.portal='amazon movies & tv' AND m.region='us'
                                        LEFT OUTER JOIN pricm_staging.movies n ON per.max_portal_item_id=n.portal_item_id AND n.portal='amazon movies & tv' AND n.region='us' 
                                        HAVING min_id_count=1 AND max_id_count=1  limit 100   """ %(tag +'%',tag +'%')

            print(sql_select_Query_check)

            cursor_check = connection_check.cursor()
            cursor_check.execute("SET SESSION group_concat_max_len = 1000000000;")
            cursor_check.execute(sql_select_Query_check)
            records_check = cursor_check.fetchall()

            page_content_check += "<form method=POST name=myform action=/aps ><input type=text name=title value=%s> <input type=button value=Search onclick=form_myform_submit() ></form> <form method=POST name=aps action=/aps_update target=_blank > <input type=button value=Update onclick=form_submit_aps() ><BR>" %(tag)
            page_content_check += "<table class=customers ><TR><TH>#</TH><TH><input type=checkbox id=select_all  ></TH><TH>Title</TH><TH>VONLY Asset ID</TH><TH>Portal Item ID Studio Director Release Date</TH><TH>Image</TH>"
            page_content_check += "<TH>Title</TH><TH>VONLY Asset ID</TH><TH>Portal Item ID Studio Director Release Date</TH><TH>Image</TH></TR>"

            i = 1
            for row in records_check:               
                    page_content_check += "<TR><TD>" + str(i) + "</TD>"  
                    page_content_check += "<TD>  <input type=checkbox class=checkbox name=\"UPDATE movie_ids set vonly_asset_id='"+str(row[1])+"' WHERE vonly_asset_id='"+ str(row[7]) +"'; \" ></TD>"
                    page_content_check += "<TD> <a  onclick=\"form_submit_title('" + str(row[0]).replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%") + "')\" >" + str(row[0]) + "</a></TD>"
                    page_content_check += "<TD nowrap> <a  onclick=form_submit_vonly_asset_id('" + str(row[1]) + "') >" + str(row[1]) + " </a> </TD>"                
                    page_content_check += "<TD>" + str(row[2])+ "<BR>" +str(row[3]) + "<BR>"+ str(row[4]) + "<BR>"+ str(row[5]) + "</TD>" 
                    page_content_check += "<TD><img src=" + str(row[14]) + " height=100 width=75 /></TD>"
                    page_content_check += "<TD> <a  onclick=\"form_submit_title('" + str(row[6]).replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%") + "')\" >" + str(row[6]) + "</a></TD>"
                    page_content_check += "<TD nowrap> <a  onclick=form_submit_vonly_asset_id('" + str(row[7]) + "') >" + str(row[7]) + " </a> </TD>"                
                    page_content_check += "<TD>" + str(row[8])+ "<BR>" +str(row[9]) + "<BR>"+ str(row[10]) + "<BR>"+ str(row[11]) + "</TD>"
                    page_content_check += "<TD><img src=" + str(row[15]) + " height=100 width=75 /></TD>"
                    i = i + 1

            page_content_check += "</table></form>"

        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if (connection_check.is_connected()):
                connection_check.close()
                cursor_check.close()
                print("MySQL connection is closed")
    else:
        page_content_check += "<form method=POST name=myform action=/aps ><input type=text name=title> <input type=Submit value=Search onclick=form_myform_submit() ></form> <input type=button value=Update onclick=form_submit_aps() ><BR>"

    return page_content_check

@app.route('/mapping')
def mapping():
    # Render the page
    page_content = ""
    page_content += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 2px;} "
    page_content += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"

    page_content += "<script> function form_submit(portal,studio,percentage,bundle) { document.forms[0].studio.value=studio; document.forms[0].portal.value=portal; document.forms[0].bundle.value=bundle; document.forms[0].percentage.value=percentage; document.forms[0].submit();} </script> <form method=POST name=main action=/drill target=_blank ><input type=hidden name=portal><input type=hidden name=studio><input type=hidden name=bundle><input type=hidden name=percentage></form> "

    try:
        connection = mysql.connector.connect(host='192.168.12.102',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')
        

        page_content += Generate_Main_Table(connection,'iTunes')
        page_content += Generate_Main_Table(connection,'VUDU')
        page_content += Generate_Main_Table(connection,'Google Play')
        page_content += Generate_Main_Table(connection,'YouTube')
        page_content += Generate_Main_Table(connection,'Amazon Prime Video')
        page_content += Generate_Main_Table(connection,'Amazon Movies & TV')
        

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            #cursor.close()
            print("MySQL connection is closed")

    return page_content

@app.route('/findimdb', methods=['GET', 'POST'])
def findimdb():
    # Render the page

    tagtitle = ""
    page_content_checktitle = ""  
    page_content_checktitle += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content_checktitle += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "    
    page_content_checktitle += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"


    if request.method == 'POST':   
        tagtitle = request.form['tag'].replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%")

        form_content_checktitle = "<script> function form_submit_vonly_asset_id(vonly_asset_id) { document.forms[0].tag.value=vonly_asset_id; document.forms['vonly_asset_id'].submit();} </script> <form method=POST name=vonly_asset_id action=/check target=_blank ><input type=hidden name=tag></form> "
        form_content_checktitle += """<form method="POST"> Title: <input type="text" name="tag" size=50 value='%s'> <input type="submit" value="Find"> <input type="submit" value="Update" > """ % (tagtitle)        
        
        update_query = ""
        set_clause = ""
        where_clause = ""
        where = []

        for key, value in request.form.items():
           if key == 'vonly_asset_id':
              set_clause = "UPDATE movie_ids set vonly_asset_id='%s'" % (value)
           if key != 'vonly_asset_id' and key != 'tag' and value == 'on':
                where.append(key)   
           
        where_clause = """ WHERE vonly_asset_id in ('%s') """ % ("','".join(where))     


        try:
            connection_checktitle = mysql.connector.connect(host='192.168.12.102',
                                                database='vonly_data_feed_us_staging',
                                                user='vonly-agent',
                                                password='a714fded-311c-4215-8b8b-5df4086e264b')

            if set_clause != '' and where_clause != '':
                update_query = set_clause + where_clause
                print(update_query)
                cursor_checktitle = connection_checktitle.cursor()               
                cursor_checktitle.execute(update_query)
                connection_checktitle.commit()

            sql_select_Query_checktitle = """SELECT m.title,m.vonly_asset_id, 
                                (SELECT GROUP_CONCAT(concat('<a href=https://itunes.apple.com/us/movie/id',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id) itunes_ids,
                                (SELECT GROUP_CONCAT(concat('<a href=https://amazon.com/dp/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id) amazon_ids, 
                                (SELECT GROUP_CONCAT(concat('<a href=https://www.vudu.com/content/movies/details/1917/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id) vudu_ids,
                                (SELECT GROUP_CONCAT(concat('<a href=https://play.google.com/store/movies/details/title?id=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id) google_ids, 
                                (SELECT GROUP_CONCAT(concat('<a href=https://youtube.com/watch?v=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id) youtube_ids,
                                (SELECT GROUP_CONCAT(concat('<a href=https://tv.apple.com/us/movie/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='appletvapp' and mi.portal='AppleTV_CanonicalId' AND mi.vonly_asset_id=m.vonly_asset_id) aps_ids, 
                                (
                                SELECT GROUP_CONCAT(CONCAT('<img src=''',mmi.image_url,''' height=150 width=150 alt=''',mmi.portal_item_id,''' /><BR>')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('<img src=''',mmi.image_url,''' height=150 width=150 /><BR>')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_urls, 
                                (
                                SELECT GROUP_CONCAT(CONCAT('<img src=''',mmi.image_url,''' height=150 width=150 alt=''',mmi.portal_item_id,''' /><BR>')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_urls,
                                (
                                SELECT GROUP_CONCAT(CONCAT('<img src=''',mmi.image_url,''' height=150 width=150 alt=''',mmi.portal_item_id,''' /><BR>')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_urls, 
                                (
                                SELECT GROUP_CONCAT(CONCAT('<img src=''',mmi.image_url,''' height=150 width=150 alt=''',mmi.portal_item_id,''' /><BR>')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('<img src=''',mmi.image_url,''' height=150 width=150 /><BR>')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id ) aps_urls,
                                mpm.portal_item_id mpm_vvid,
                                concat('<a href=https://www.imdb.com/title/',ii.portal_item_id,' target=_blank>',ii.portal_item_id,'</a>') imdb_id,
                                concat('<img src=''',(select image_url from sandbox.movies where vonly_asset_id=m.vonly_asset_id and platform='IMDB' limit 1 ),''' height=150 width=150 />'),
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']'))
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region AND mi.platform=mmi.platform 
                                WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_urls, 
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']'))
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']'))
                               FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_urls, 
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']'))
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']'))
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id ) aps_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,'')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,''))
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_urls, 
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,''))
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,''))
                               FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_urls, 
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,''))
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,''))
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id ) aps_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_urls, 
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_urls, 
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')')) 
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_urls,
                                (
                                SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')'))  
                                FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region 
                                WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id ) aps_urls
                                FROM movie_ids m
                                LEFT OUTER JOIN  sandbox.movies mm ON m.id=mm.vonly_id AND mm.region=m.region
                                LEFT OUTER JOIN  movie_ids mpm on m.vonly_asset_id=mpm.vonly_asset_id and mpm.platform='wb mpm-vvid'
                                LEFT OUTER JOIN  imdb_ids ii on m.vonly_asset_id=ii.vonly_asset_id 
                                WHERE m.platform not in('Amazon Movies & TV','WB MPM-VVID','WB UPC')  and m.title like '%s' group by m.vonly_asset_id order by m.title """ % (tagtitle + "%")

            print(sql_select_Query_checktitle)
            cursor_checktitle = connection_checktitle.cursor()
            cursor_checktitle.execute("SET SESSION group_concat_max_len = 1000000000;")
            cursor_checktitle.execute(sql_select_Query_checktitle)
            records_checktitle = cursor_checktitle.fetchall()     
            
            page_content_checktitle += "<h3>Search results for: %s </h3>" % (tagtitle)

            page_content_checktitle += "<table class=customers ><TR><TH>Title</TH><TH>VONLY Asset ID</TH><TH>iTunes Portal Item IDs</TH><TH>VUDU Portal Item IDs</TH><TH>Google Portal Item IDs</TH><TH>YouTube Portal Item IDs</TH><TH>Amazon Portal Item IDs</TH><TH>AppleTVApp Portal Item IDs</TH></TR>"
            i = 0;
            for row in records_checktitle:
                color= "#e6f7ff " if i % 2 == 0 else "white" 
                page_content_checktitle += "<TR BGCOLOR="+ color +" ><TD rowspan=2 >" + str(row[0]) + "</TD><TD nowrap><input type=checkbox name=" + str(row[1]) + "> <a  onclick=form_submit_vonly_asset_id('" + str(row[1]) + "') > " + str(row[1]) + "</a><input type=radio name=vonly_asset_id value=" + str(row[1]) + "><BR> " + str(row[16]) + "</TD><TD>"+  str(row[29])+ "<BR>" + str(row[8]) + "<BR>" + str(row[17]) + "<BR>" + str(row[23]) + "</TD><TD>"+  str(row[31]) + "<BR>"+ str(row[10]) + "<BR>" + str(row[19]) +"<BR>" + str(row[25]) +"</TD><TD>"+  str(row[32])+ "<BR>" + str(row[11]) + "<BR>" + str(row[20]) +"<BR>" + str(row[26]) +"</TD><TD>" + str(row[33])+ "<BR>" + str(row[12]) +"<BR>" + str(row[21]) + "<BR>" + str(row[27]) +"</TD><TD>"  + str(row[30]) + "<BR>" + str(row[9]) +"<BR>" + str(row[18]) +"<BR>" + str(row[24]) + "</TD><TD>"+ str(row[34])+ "<BR>" + str(row[13]) +"<BR>" + str(row[22]) +"<BR>" + str(row[28]) + "</TD></TR>"
                page_content_checktitle += "<TR BGCOLOR="+ color +" ><TD>" + str(row[14])   + " <BR> " + str(row[15]) + "</TD><TD>" + str(row[2]) + "</TD><TD>" + str(row[4]) + "</TD><TD>" + str(row[5]) + "</TD><TD>" + str(row[6]) + "</TD><TD>" + str(row[3]) + "</TD><TD>" + str(row[7]) + "</TD></TR>"
                i = i + 1
            page_content_checktitle += "</table></form>"
            
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if (connection_checktitle.is_connected()):
                connection_checktitle.close()
                cursor_checktitle.close()
                print("MySQL connection is closed")
    else:
        form_content_checktitle = """<form method="POST"> Title: <input type="text" name="tag" size=50 > <input type="submit" value="Search"></form>"""    

    return form_content_checktitle + page_content_checktitle

@app.route('/verify')
def verify():
    # Render the page
    page_content = ""

    page_content += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "
    page_content += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"

    try:
        connection = mysql.connector.connect(host='192.168.12.102',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')
        #connection = mysql.connector.connect(host='192.168.100.202',
        #                                 database='vonly_data_feed_us_development',
        #                                 user='vonly-dev',
        #                                 password='z9mtDkpjSsTMjRqhws')

        sql_select_Query = """SELECT m.title,m.vonly_asset_id, 
                            (SELECT GROUP_CONCAT(concat('<a href=https://itunes.apple.com/us/movie/id',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id) itunes_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://amazon.com/dp/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id) amazon_ids, 
                            (SELECT GROUP_CONCAT(concat('<a href=https://www.vudu.com/content/movies/details/1917/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id) vudu_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://play.google.com/store/movies/details/title?id=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id) google_ids, 
                            (SELECT GROUP_CONCAT(concat('<a href=https://youtube.com/watch?v=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id) youtube_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://tv.apple.com/us/movie/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE  mi.platform='AppleTVApp' AND mi.vonly_asset_id=m.vonly_asset_id) aps_ids, 
                            (
                            SELECT GROUP_CONCAT(CONCAT('<img src="',case when mmi.image_url is null then '' else mmi.image_url end ,'" height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN movie_metadata mmi ON mi.id=mmi.vonly_id AND mmi.search_date='2020-03-20'
                            WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN movie_metadata mmi ON mi.id=mmi.vonly_id AND mmi.search_date='2020-03-20'
                            WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_urls, 
                            (
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN movie_metadata mmi ON mi.id=mmi.vonly_id AND mmi.search_date='2020-03-20'
                            WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_urls,
                            (
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN movie_metadata mmi ON mi.id=mmi.vonly_id AND mmi.search_date='2020-03-20'
                            WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_urls, 
                            (
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN movie_metadata mmi ON mi.id=mmi.vonly_id AND mmi.search_date='2020-03-20'
                            WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN movie_metadata mmi ON mi.id=mmi.vonly_id AND mmi.search_date='2020-03-20'
                            WHERE mi.platform='AppleTVApp' AND mi.vonly_asset_id=m.vonly_asset_id ) aps_urls, mpm.portal_item_id mpm_vvid
                            FROM movie_ids m
                            LEFT OUTER JOIN movie_metadata mm ON m.id=mm.vonly_id AND mm.search_date='2020-03-20'
                            LEFT OUTER JOIN  movie_ids mpm on m.vonly_asset_id=mpm.vonly_asset_id and mpm.portal='wb mpm-vvid'
                            WHERE m.platform='itunes' and mm.distributed_by_parent='WB' ORDER BY 1 """
        
        

        print(sql_select_Query)

        cursor = connection.cursor()        
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

        #page_content += "<table class=customers ><TR><TD>Title</TD><TD>VONLY
        #Asset ID</TD><TD>iTunes Portal Item IDs</TD><TD>VUDU Portal Item
        #IDs</TD><TD>Google Portal Item IDs</TD><TD>YouTube Portal Item
        #IDs</TD><TD>Amazon Portal Item IDs</TD><TD>APS Portal Item
        #IDs</TD></TR>"
        page_content += "<table class=customers ><TR><TH>Title</TH><TH>VONLY Asset ID</TH><TH>iTunes Portal Item IDs</TH><TH>VUDU Portal Item IDs</TH><TH>Google Portal Item IDs</TH><TH>YouTube Portal Item IDs</TH><TH>Amazon Portal Item IDs</TH><TH>APS Portal Item IDs</TH></TR>"
        
        for row in records:
            page_content += "<TR><TD rowspan=2 >" + str(row[0]) + "</TD><TD nowrap>" + str(row[1]) + "</TD><TD>" + str(row[8]) + "</TD><TD>" + str(row[10]) + "</TD><TD>" + str(row[11]) + "</TD><TD>" + str(row[12]) + "</TD><TD>" + str(row[9]) + "</TD><TD>" + str(row[13]) + "</TD></TR>"
            page_content += "<TR><TD>" + str(row[14]) + "</TD><TD>" + str(row[2]) + "</TD><TD>" + str(row[4]) + "</TD><TD>" + str(row[5]) + "</TD><TD>" + str(row[6]) + "</TD><TD>" + str(row[3]) + "</TD><TD>" + str(row[7]) + "</TD></TR>"

        page_content += "</table>"
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

    return page_content

@app.route('/verifysandbox')
def verifysandbox():
    # Render the page
    page_content = ""

    page_content += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "
    page_content += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"

    try:
        connection = mysql.connector.connect(host='192.168.12.102',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')
        #connection = mysql.connector.connect(host='192.168.100.202',
        #                                 database='vonly_data_feed_us_development',
        #                                 user='vonly-dev',
        #                                 password='z9mtDkpjSsTMjRqhws')

        sql_select_Query = """SELECT m.title,m.vonly_asset_id, 
                            (SELECT GROUP_CONCAT(concat('<a href=https://itunes.apple.com/us/movie/id',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.portal='itunes' AND mi.vonly_asset_id=m.vonly_asset_id) itunes_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://amazon.com/dp/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.portal='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id) amazon_ids, 
                            (SELECT GROUP_CONCAT(concat('<a href=https://www.vudu.com/content/movies/details/1917/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.portal='vudu' AND mi.vonly_asset_id=m.vonly_asset_id) vudu_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://play.google.com/store/movies/details/title?id=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.portal='google play' AND mi.vonly_asset_id=m.vonly_asset_id) google_ids, 
                            (SELECT GROUP_CONCAT(concat('<a href=https://youtube.com/watch?v=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.portal='youtube' AND mi.vonly_asset_id=m.vonly_asset_id) youtube_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://amazon.com/dp/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.portal='amazon movies & tv' AND mi.vonly_asset_id=m.vonly_asset_id) aps_ids, 
                            (
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end ,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mmi.region=mi.region 
                            WHERE mi.portal='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mmi.region=mi.region 
                            WHERE mi.portal='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_urls, 
                            (
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mmi.region=mi.region 
                            WHERE mi.portal='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_urls,
                            (
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mmi.region=mi.region  
                            WHERE mi.portal='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_urls, 
                            (
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mmi.region=mi.region 
                            WHERE mi.portal='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mmi.region=mi.region 
                            WHERE mi.portal='amazon movies & tv' AND mi.vonly_asset_id=m.vonly_asset_id ) aps_urls, mpm.portal_item_id mpm_vvid
                            FROM movie_ids m
                            LEFT OUTER JOIN sandbox.movies mm ON m.id=mm.vonly_id AND mm.region='US'
                            LEFT OUTER JOIN  movie_ids mpm on m.vonly_asset_id=mpm.vonly_asset_id and mpm.portal='wb mpm-vvid'
                            WHERE m.portal='itunes' and mm.distributed_by_parent='WB' ORDER BY 1  """
        
        

        print(sql_select_Query)

        cursor = connection.cursor()        
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

        #page_content += "<table class=customers ><TR><TD>Title</TD><TD>VONLY
        #Asset ID</TD><TD>iTunes Portal Item IDs</TD><TD>VUDU Portal Item
        #IDs</TD><TD>Google Portal Item IDs</TD><TD>YouTube Portal Item
        #IDs</TD><TD>Amazon Portal Item IDs</TD><TD>APS Portal Item
        #IDs</TD></TR>"
        page_content += "<table class=customers ><TR><TH>Title</TH><TH>VONLY Asset ID</TH><TH>iTunes Portal Item IDs</TH><TH>VUDU Portal Item IDs</TH><TH>Google Portal Item IDs</TH><TH>YouTube Portal Item IDs</TH><TH>Amazon Portal Item IDs</TH><TH>APS Portal Item IDs</TH></TR>"
        
        for row in records:
            page_content += "<TR><TD rowspan=2 >" + str(row[0]) + "</TD><TD nowrap>" + str(row[1]) + "</TD><TD>" + str(row[8]) + "</TD><TD>" + str(row[10]) + "</TD><TD>" + str(row[11]) + "</TD><TD>" + str(row[12]) + "</TD><TD>" + str(row[9]) + "</TD><TD>" + str(row[13]) + "</TD></TR>"
            page_content += "<TR><TD>" + str(row[14]) + "</TD><TD>" + str(row[2]) + "</TD><TD>" + str(row[4]) + "</TD><TD>" + str(row[5]) + "</TD><TD>" + str(row[6]) + "</TD><TD>" + str(row[3]) + "</TD><TD>" + str(row[7]) + "</TD></TR>"

        page_content += "</table>"
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

    return page_content

@app.route('/check', methods=['GET', 'POST'])
def check():
    # Render the page
    form_content_check = ""
    tag = ""
    page_content_check = ""

    page_content_check += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content_check += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "    
    page_content_check += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"
    
    if request.method == 'POST':  

        form_content_check = """<form method="POST"> VONLY Asset ID: <input type="text" name="tag" size=50 value='%s'> <input type="submit" value="Search"> <input type="submit" value="Generate New VONLY Asset ID(s)" >""" % (request.form['tag'])

        tag = request.form['tag']

        update_query = ""
        set_clause = ""
        where_clause = ""
        where = []

        new_vonly_asset_id = uuid.uuid1()
        for key, value in request.form.items():           
           if key != 'tag' and value == 'on':               
               set_clause = "UPDATE movie_ids set vonly_asset_id='%s'" % (new_vonly_asset_id)
               where_clause = " WHERE portal_item_id = '%s'; " % (key)          
               where.append(set_clause + where_clause)

        try:
            connection_check = mysql.connector.connect(host='192.168.12.102',
                                             database='vonly_data_feed_us_staging',
                                             user='vonly-agent',
                                             password='a714fded-311c-4215-8b8b-5df4086e264b')

            if len(where) > 0 :           
                cursor_check = connection_check.cursor()   
                for query in where:
                    cursor_check.execute(query)                
                connection_check.commit()

            sql_select_Query_check = """SELECT 
                                                tis.title AS season_title,
                                                tis.vonly_asset_id AS season_vonly_asset_id,
                                                tis.num AS season_number,
                                                 (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ' ),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='itunes' AND  tie.scope='tv_episode'  ) AS itunes_episodes_list,
                                                (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='amazon prime video' AND  tie.scope='tv_episode'  ) AS amazon_episodes_list,
                                              
                                                 (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='appletvapp'  AND  tie.scope='tv_episode'  ) AS appletvapp_episodes_list,
                                                
                                                
                                                (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='vudu' AND  tie.scope='tv_episode'  ) AS vudu_episodes_list,
                                                
                                                
                                                (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='google play' AND  tie.scope='tv_episode'  ) AS googleplay_episodes_list ,
(select portal_item_id from tv_ids where platform='wb mpm-vvid' and vonly_asset_id=tis.vonly_asset_id) as mpm_vvid                                               
                                            FROM 
                                                tv_ids tis
                                            LEFT OUTER JOIN 
                                                tv_id_mappings tim ON tis.id = tim.season_vonly_id
                                            LEFT OUTER JOIN 
                                                tv_ids tie ON tim.episode_vonly_id = tie.id and tie.scope='tv_episode'                                           
                                            WHERE 
                                                tis.scope ='tv_season' AND tis.platform IN ('itunes', 'amazon prime video', 'appletvapp', 'vudu', 'google play','wb mpm-vvid') 
                                                AND  tis.vonly_asset_id='%s'
                                            GROUP BY 
                                                tis.vonly_asset_id
                                            ORDER BY 
                                                CAST(tis.num AS SIGNED) , CAST(tie.num AS SIGNED) ASC;  """ % (tag)

            print(sql_select_Query_check)
            cursor_check = connection_check.cursor()
            cursor_check.execute("SET SESSION group_concat_max_len = 1000000000;")
            cursor_check.execute(sql_select_Query_check)
            records_check = cursor_check.fetchall()

            page_content_check += "<table class=customers ><TR><TH>Title</TH><TH>VONLY Asset ID</TH><TH>iTunes Portal Item IDs</TH><TH>VUDU Portal Item IDs</TH><TH>Google Portal Item IDs</TH><TH>YouTube Portal Item IDs</TH><TH>Amazon Portal Item IDs</TH><TH>AppleTVApp Portal Item IDs</TH></TR>"

            for row in records_check:
                page_content_check +="<TR BGCOLOR="+ color +" ><TD>"+ str(row[0]) +"</TD><TD>"+ str(row[2]) +"</TD><TD nowrap><input type=checkbox name=" + str(row[1]) + "> <a  onclick=form_submit_vonly_asset_id('" + str(row[1]) + "') > " + str(row[1]) + "</a><input type=radio name=vonly_asset_id value=" + str(row[1]) + "> <BR> <BR> <BR>"+ str(row[8]) +"</TD><TD>"+ str(row[3]) + "</TD><TD>"+ str(row[6]) +"</TD><TD>"+ str(row[7]) +"</TD><TD>"+ str(row[4]) +"</TD><TD>"+ str(row[5]) + "</TD></TR>"
                
            page_content_check += "</table></form>"
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if (connection_check.is_connected()):
                connection_check.close()
                cursor_check.close()
                print("MySQL connection is closed")
    else:
        form_content_check = """<form method="POST"> VONLY Asset ID: <input type="text" name="tag" size=50 > <input type="submit" value="Search"></form>"""    

    return form_content_check + page_content_check

@app.route('/checktitle', methods=['GET', 'POST'])
def checktitle():
    # Render the page

    tagtitle = ""
    page_content_checktitle = ""  
    page_content_checktitle += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content_checktitle += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "    
    page_content_checktitle += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"


    if request.method == 'POST':   
        tagtitle = request.form['tag'].replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%")
        tag_no_title = request.form['tag_no'].replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%")

        form_content_checktitle = "<script> function form_submit_vonly_asset_id(vonly_asset_id) { document.forms[0].tag.value=vonly_asset_id; document.forms['vonly_asset_id'].submit();} </script> <form method=POST name=vonly_asset_id action=/check target=_blank ><input type=hidden name=tag></form> "
        form_content_checktitle += """<form method="POST"> Season Title: <input type="text" name="tag" size=50 value='%s'> Season No:<input type="text" name="tag_no" size=5 value='%s'> <input type="submit" value="Search"> <input type="submit" value="Update" > """ % (tagtitle,tag_no_title)      
        
        update_query = ""
        set_clause = ""
        where_clause = ""
        where = []

        for key, value in request.form.items():
           if key == 'vonly_asset_id':
              set_clause = "UPDATE tv_ids set vonly_asset_id='%s'" % (value)
           if key != 'vonly_asset_id' and key != 'tag' and value == 'on':
                where.append(key)   
           
        where_clause = """ WHERE scope='tv_season' and vonly_asset_id in ('%s') """ % ("','".join(where))     


        try:
            connection_checktitle = mysql.connector.connect(host='192.168.12.102',
                                                database='vonly_data_feed_us_staging',
                                                user='vonly-agent',
                                                password='a714fded-311c-4215-8b8b-5df4086e264b')

            if set_clause != '' and where_clause != '':
                update_query = set_clause + where_clause
                print(update_query)
                cursor_checktitle = connection_checktitle.cursor()               
                cursor_checktitle.execute(update_query)
                connection_checktitle.commit()

            sql_select_Query_checktitle = """  SELECT 
   tis.title AS season_title,
   tis.vonly_asset_id AS season_vonly_asset_id,
   tis.num AS season_number,
   
   
    (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ' ),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='itunes' AND  tie.scope='tv_episode'  ) AS itunes_episodes_list,


    (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='amazon prime video' AND  tie.scope='tv_episode'  ) AS amazon_episodes_list,
                                              
   (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='appletvapp'  AND  tie.scope='tv_episode'  ) AS appletvapp_episodes_list,
                                                
                                                
   (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='vudu' AND  tie.scope='tv_episode'  ) AS vudu_episodes_list,
                                                
                                                
   (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='google play' AND  tie.scope='tv_episode'  ) AS googleplay_episodes_list ,
(select portal_item_id from tv_ids where platform='wb mpm-vvid' and vonly_asset_id=tis.vonly_asset_id) as mpm_vvid,       

(
SELECT GROUP_CONCAT(
       DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://amazon.com/gp/video/detail/',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
       separator '<BR>'
)
 FROM tv_ids ti_1 
   WHERE ti_1.platform = 'amazon prime video' AND ti_1.vonly_asset_id = tis.vonly_asset_id
) AS amazon_ids,


(
SELECT GROUP_CONCAT(
 	DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://www.vudu.com/content/browse/details/title/',ti_1.portal_item_id,'>',ti_1.portal_item_id, '</a>')
       SEPARATOR '<BR>'
   ) 
   FROM tv_ids ti_1 
   WHERE ti_1.platform = 'vudu' AND ti_1.vonly_asset_id = tis.vonly_asset_id
) AS vudu_ids,


(
     SELECT GROUP_CONCAT(
       DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://tv.apple.com/us/season/season/',ti_1.portal_item_id,'?showId=', ti_show.portal_item_id,' >', ti_1.portal_item_id, '</a>') 
       SEPARATOR '<BR>'
   ) 
   FROM tv_ids ti_1
INNER JOIN tv_id_mappings tim ON ti_1.id=tim.season_vonly_id 
INNER JOIN tv_ids ti_show ON tim.show_vonly_id= ti_show.id
   WHERE ti_1.platform = 'appletvapp' AND ti_1.vonly_asset_id = tis.vonly_asset_id AND ti_1.portal = 'AppleTV_CanonicalId'

) AS appletvapp_ids,


(
   SELECT GROUP_CONCAT(
       DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://itunes.apple.com/us/tv-season/title/id',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
       separator '<BR>'
   ) 
   FROM tv_ids ti_1 
   WHERE ti_1.platform = 'itunes' AND ti_1.vonly_asset_id = tis.vonly_asset_id
) AS itunes_ids,


(
   SELECT GROUP_CONCAT(
       DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://play.google.com/store/tv/show/?id=',tsi.portal_item_id,'&hl=en_US&gl=US&cdid=tvseason-',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
       separator '<BR>'
   ) 
       FROM tv_ids ti_1 
       INNER JOIN tv_id_mappings tim ON ti_1.id=tim.season_vonly_id
       INNER JOIN tv_ids tsi ON tim.show_vonly_id=tsi.id
       WHERE ti_1.platform = 'google play' AND ti_1.vonly_asset_id = tis.vonly_asset_id AND ti_1.portal = 'google play'
) AS google_ids,


(
SELECT CONCAT('<table border=1><tr><td>', "Total_episodes", '</td><td>', COUNT(DISTINCT tie.num), '</td></tr></table>')
FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id = timi.episode_vonly_id 
INNER JOIN tv_ids tisi ON tisi.id = timi.season_vonly_id
WHERE tisi.vonly_asset_id = tis.vonly_asset_id AND tisi.platform = 'itunes' AND tie.scope = 'tv_episode') AS itunes_episodes_no,


    (SELECT CONCAT('<table border=1><tr><td>', "Total_episodes", '</td><td>', COUNT(DISTINCT tie.num), '</td></tr></table>')
FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='amazon prime video' AND  tie.scope='tv_episode'  ) AS amazon_episodes_no,
                                              
   (SELECT CONCAT('<table border=1><tr><td>', "Total_episodes", '</td><td>', COUNT(DISTINCT tie.num), '</td></tr></table>')FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='appletvapp'  AND  tie.scope='tv_episode'  ) AS appletvapp_episodes_no,
                                                
                                                
   (SELECT CONCAT('<table border=1><tr><td>', "Total_episodes", '</td><td>', COUNT(DISTINCT tie.num), '</td></tr></table>')FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='vudu' AND  tie.scope='tv_episode'  ) AS vudu_episodes_no,
                                                
                                                
   (SELECT CONCAT('<table border=1><tr><td>', "Total_episodes", '</td><td>', COUNT(DISTINCT tie.num), '</td></tr></table>')FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='google play' AND  tie.scope='tv_episode'  ) AS googleplay_episodes_no 
                                        
  FROM 
      tv_ids tis
  LEFT OUTER JOIN 
      tv_id_mappings tim ON tis.id = tim.season_vonly_id
  LEFT OUTER JOIN 
      tv_ids tie ON tim.episode_vonly_id = tie.id and tie.scope='tv_episode'                                           
  WHERE 
      tis.scope ='tv_season' AND tis.platform IN ('itunes', 'amazon prime video', 'appletvapp', 'vudu', 'google play','wb mpm-vvid') 
      AND  tis.title LIKE '%s' and (tis.num ='%s' or tis.num is null) and tis.title not like '%s'
  GROUP BY 
      tis.vonly_asset_id
  ORDER BY 
      CAST(tis.num AS SIGNED) , CAST(tie.num AS SIGNED) ASC; """ % (tagtitle + "%",tag_no_title,"%complete series%" ) 

            print(sql_select_Query_checktitle)
            cursor_checktitle = connection_checktitle.cursor()
            cursor_checktitle.execute("SET SESSION group_concat_max_len = 1000000000;")
            cursor_checktitle.execute(sql_select_Query_checktitle)
            records_checktitle = cursor_checktitle.fetchall()     
            
            page_content_checktitle += "<h3>Search results for: %s </h3>" % (tagtitle)

            page_content_checktitle += "<table class=customers ><TR><TH>Title</TH><TH>Season_no</TH><TH>VONLY Asset ID <BR> MPM-VVID </TH><TH>iTunes Portal Item IDs</TH><TH>VUDU Portal Item IDs</TH><TH>Google Portal Item IDs</TH><TH>Amazon Portal Item IDs</TH><TH>AppleTVApp Portal Item IDs</TH></TR>"
            i = 0;
            for row in records_checktitle:
                color= "#e6f7ff " if i % 2 == 0 else "white" 
                page_content_checktitle +="<TR BGCOLOR="+ color +" ><TD rowspan=2 >"+ str(row[0]) +"</TD><TD rowspan=2 >"+ str(row[2]) +"</TD><TD nowrap rowspan=2><input type=checkbox name=" + str(row[1]) + "> <a  onclick=form_submit_vonly_asset_id('" + str(row[1]) + "') > " + str(row[1]) + "</a><input type=radio name=vonly_asset_id value=" + str(row[1]) + "> <BR> <BR> <BR>"+ str(row[8]) +"</TD><TD>"+ str(row[3]) + "</TD><TD>"+ str(row[6]) +"</TD><TD>"+ str(row[7]) +"</TD><TD>"+ str(row[4]) +"</TD><TD>"+ str(row[5]) + "</TD></TR>"
                page_content_checktitle += "<TR BGCOLOR="+ color +" ><TD>" + str(row[12]) + " <BR> " + str(row[14]) + "</TD><TD>" + str(row[10]) + " <BR> " + str(row[17]) + "</TD><TD>" + str(row[13]) +  " <BR> " + str(row[18]) + "</TD><TD>" + str(row[9]) + " <BR> " + str(row[15]) +  "</TD><TD>" + str(row[11]) + " <BR> " + str(row[16]) +  "</TD></TR>"
               
                
                i = i + 1
            page_content_checktitle += "</table></form>"
            
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if (connection_checktitle.is_connected()):
                connection_checktitle.close()
                cursor_checktitle.close()
                print("MySQL connection is closed")
    else:
        form_content_checktitle = """<form method="POST"> Season Title: <input type="text" name="tag" size=50 > Season No <input type="text" name="tag_no" size=5 > <input type="submit" value="Search"></form>"""    

    return form_content_checktitle + page_content_checktitle

@app.route('/checkvonly', methods=['GET', 'POST'])
def checkvonly():
    # Render the page
    form_content_check = ""
    tag = ""
    page_content_check = ""

    page_content_check += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content_check += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;} "    
    page_content_check += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"
    
    if request.method == 'POST':  

        form_content_check = """<form method="POST"> VONLY Asset ID: <input type="text" name="tag" size=50 value='%s'> <input type="submit" value="Search"> <input type="submit" value="Generate New VONLY Asset ID(s)" >""" % (request.form['tag'])

        tag = request.form['tag']

        update_query = ""
        set_clause = ""
        where_clause = ""
        where = []

        new_vonly_asset_id = uuid.uuid1()
        for key, value in request.form.items():           
           if key != 'tag' and value == 'on':               
               set_clause = "UPDATE movie_ids set vonly_asset_id='%s'" % (new_vonly_asset_id)
               where_clause = " WHERE portal_item_id = '%s'; " % (key)          
               where.append(set_clause + where_clause)

        try:
            connection_check = mysql.connector.connect(host='192.168.12.102',
                                             database='vonly_data_feed_us_staging',
                                             user='vonly-agent',
                                             password='a714fded-311c-4215-8b8b-5df4086e264b')

            if len(where) > 0 :           
                cursor_check = connection_check.cursor()   
                for query in where:
                    cursor_check.execute(query)                
                connection_check.commit()

            sql_select_Query_check = """ SELECT 
                                                tis.title AS season_title,
                                                tis.vonly_asset_id AS season_vonly_asset_id,
                                                tis.num AS season_number,
                                                 (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ' ),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='itunes' AND  tie.scope='tv_episode'  ) AS itunes_episodes_list,
                                                (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='amazon prime video' AND  tie.scope='tv_episode'  ) AS amazon_episodes_list,
                                              
                                                 (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='appletvapp'  AND  tie.scope='tv_episode'  ) AS appletvapp_episodes_list,
                                                
                                                
                                                (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='vudu' AND  tie.scope='tv_episode'  ) AS vudu_episodes_list,
                                                
                                                
                                                (SELECT  
CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
 FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  tisi.vonly_asset_id=tis.vonly_asset_id AND tisi.platform='google play' AND  tie.scope='tv_episode'  ) AS googleplay_episodes_list
                                                
                                            FROM 
                                                tv_id_mappings tim
                                            LEFT OUTER JOIN 
                                                tv_ids tis ON tim.season_vonly_id = tis.id 
                                            LEFT OUTER JOIN 
                                                tv_ids tie ON tim.episode_vonly_id = tie.id                                            
                                            WHERE 
                                                tis.platform IN ('itunes', 'amazon prime video', 'appletvapp', 'vudu', 'google play') 
                                                AND tis.vonly_asset_id IN (
                                                    SELECT t.vonly_asset_id 
                                                    FROM tv_ids t 
                                                    WHERE scope ='tv_season' AND (t.vonly_asset_id LIKE '%s') 
                                                )
                                            GROUP BY 
                                                tis.vonly_asset_id
                                            ORDER BY 
                                                CAST(tis.num AS SIGNED) , CAST(tie.num AS SIGNED) ASC;  """ % (tag)
            
            print(sql_select_Query_check)
            cursor_check = connection_check.cursor()
            cursor_check.execute("SET SESSION group_concat_max_len = 1000000000;")
            cursor_check.execute(sql_select_Query_check)
            records_check = cursor_check.fetchall()

            page_content_check += "<table class=customers ><TR><TH>Title</TH><TH>VONLY Asset ID</TH><TH>iTunes Portal Item IDs</TH><TH>VUDU Portal Item IDs</TH><TH>Google Portal Item IDs</TH><TH>YouTube Portal Item IDs</TH><TH>Amazon Portal Item IDs</TH><TH>APS Portal Item IDs</TH></TR>"

            for row in records_check:
                color= "#e6f7ff " if i % 2 == 0 else "white" 
                page_content_check +="<TR BGCOLOR="+ color +" ><TD>"+ str(row[0]) +"</TD><TD>"+ str(row[2]) +"</TD><TD nowrap><input type=checkbox name=" + str(row[1]) + "> <a  onclick=form_submit_vonly_asset_id('" + str(row[1]) + "') > " + str(row[1]) + "</a><input type=radio name=vonly_asset_id value=" + str(row[1]) + "></TD><TD>"+ str(row[3]) + "</TD><TD>"+ str(row[6]) +"</TD><TD>"+ str(row[7]) +"</TD><TD>"+ str(row[4]) +"</TD><TD>"+ str(row[5]) + "</TD></TR>"

            page_content_check += "</table></form>"
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if (connection_check.is_connected()):
                connection_check.close()
                cursor_check.close()
                print("MySQL connection is closed")
    else:
        form_content_check = """<form method="POST"> Title: <input type="text" name="tag" size=50 > <input type="submit" value="Search"></form>"""    

    return form_content_check + page_content_check

def Dashboard_Top(connection,where):

    page_content = ""

    caption = "All "

    if  where == 0:
        query = """ SELECT COUNT(1),count(distinct vonly_asset_id) FROM movie_ids mi where 1=1 """ 
        caption = "Title Mapping"
    else:
        query = """ SELECT COUNT(1),count(distinct vonly_asset_id) FROM movie_ids mi where portal not in ('Amazon Movies & TV') """ 
        caption = "Title Mapping without Amazon Movies & TV "
    
    print(query)
    def_cursor = connection.cursor()        
    def_cursor.execute(query)
    records = def_cursor.fetchall()
    
    for row in records:
        title = row[0]
        unique_vonly_asset_ids = row[1]
    
    if  where == 0:
        query = """ SELECT No_of_Portals,COUNT(distinct vonly_asset_id),SUM(No_of_Titles)
                FROM ( SELECT mi.vonly_asset_id, title, 
                (SELECT COUNT(DISTINCT portal) FROM movie_ids WHERE vonly_asset_id =mi.vonly_asset_id) No_of_Portals,
                (SELECT COUNT(1) FROM movie_ids WHERE vonly_asset_id =mi.vonly_asset_id) No_of_Titles
                FROM movie_ids mi
                where 1=1
                GROUP BY mi.vonly_asset_id
                ) per
                GROUP BY No_of_Portals """        
    else:
        query = """ SELECT No_of_Portals,COUNT(distinct vonly_asset_id),SUM(No_of_Titles)
                FROM ( SELECT mi.vonly_asset_id, title, 
                (SELECT COUNT(DISTINCT portal) FROM movie_ids WHERE vonly_asset_id =mi.vonly_asset_id and portal not in ('Amazon Movies & TV')) No_of_Portals,
                (SELECT COUNT(1) FROM movie_ids WHERE vonly_asset_id =mi.vonly_asset_id and portal not in ('Amazon Movies & TV') ) No_of_Titles
                FROM movie_ids mi where mi.portal not in ('Amazon Movies & TV')
                GROUP BY mi.vonly_asset_id ) per
                GROUP BY No_of_Portals """    
    
    print(query)
    def_cursor = connection.cursor()        
    def_cursor.execute(query)
    records = def_cursor.fetchall()
    
    page_content += "<center><table class=customers ><caption> " + caption + " </caption><TR><Th>Portal Mapped</Th><Th># VAIDs</Th><Th># Titles</Th><Th>% of Total</Th></TR>"
    
    for row in records:
        percentage = round(row[2] * 100 / title,2)
        page_content += "<TR ><TD align=center >" + str(row[0]) + "</TD><TD nowrap align=right>" + f'{row[1]:,}' + "</TD><TD nowrap align=right>" + f'{row[2]:,}' + "</TD><TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage) + " 1%,white " + str(percentage) + "%);' >" + str(percentage) + "%</TD></TR>"
    
    page_content += "<TR ><TD align=right>Total </TD><TD nowrap align=right>" + f'{unique_vonly_asset_ids:,}' + "</TD><TD nowrap align=right>" + f'{title:,}' + "</TD><TD nowrap align=right></TD></TR>"
    page_content += "</table></centre>"
    return page_content

def Dashboard_Studio(connection,where):
    page_content = ""
    caption = ""
    if  where == 0:
        query = """ SELECT studio,
                    sum(case when no_of_portals=1 then no_of_titles ELSE 0 END) portal_1,
                    sum(case when no_of_portals=2 then no_of_titles ELSE 0 END) portal_2,
                    sum(case when no_of_portals=3 then no_of_titles ELSE 0 END) portal_3,
                    sum(case when no_of_portals=4 then no_of_titles ELSE 0 END) portal_4,
                    sum(case when no_of_portals=5 then no_of_titles ELSE 0 END) portal_5,
                    sum(case when no_of_portals=6 then no_of_titles ELSE 0 END) portal_6,
                    sum(case when no_of_portals=7 then no_of_titles ELSE 0 END) portal_7,
                    sum(case when no_of_portals=8 then no_of_titles ELSE 0 END) portal_8, 
                    sum(no_of_titles),
                    count(vonly_asset_id)
                    FROM (
                    SELECT 
                    m.vonly_asset_id,(SELECT COUNT(DISTINCT portal) FROM movie_ids WHERE vonly_asset_id=m.vonly_asset_id) no_of_portals,
                    case when m.portal LIKE 'WB%' then 'WB' 
	                      when m.portal not LIKE 'WB%' and length(ma.distributed_by_parent)<=0 then 'Other'  
	                      when ma.distributed_by_parent IS NULL then 'Other'     
                     ELSE ma.distributed_by_parent END studio,
                     (SELECT COUNT(1) FROM movie_ids WHERE vonly_asset_id=m.vonly_asset_id) no_of_titles
                    FROM  movie_ids m 
                    LEFT OUTER JOIN pricm_staging.movies ma ON
                    m.portal=ma.portal AND m.region=ma.region AND m.portal_item_id=ma.portal_item_id 
                    where 1=1
                    GROUP BY m.vonly_asset_id
                    ) per GROUP BY studio """
        caption = "Title Mapping By Studio"
    else:
        query = """ SELECT studio,
                    sum(case when no_of_portals=1 then no_of_titles ELSE 0 END) portal_1,
                    sum(case when no_of_portals=2 then no_of_titles ELSE 0 END) portal_2,
                    sum(case when no_of_portals=3 then no_of_titles ELSE 0 END) portal_3,
                    sum(case when no_of_portals=4 then no_of_titles ELSE 0 END) portal_4,
                    sum(case when no_of_portals=5 then no_of_titles ELSE 0 END) portal_5,
                    sum(case when no_of_portals=6 then no_of_titles ELSE 0 END) portal_6,
                    sum(case when no_of_portals=7 then no_of_titles ELSE 0 END) portal_7,
                    sum(case when no_of_portals=8 then no_of_titles ELSE 0 END) portal_8, 
                    sum(no_of_titles),
                    count(vonly_asset_id)
                    FROM (
                    SELECT 
                    m.vonly_asset_id,(SELECT COUNT(DISTINCT portal) FROM movie_ids WHERE vonly_asset_id=m.vonly_asset_id and portal not in ('Amazon Movies & TV')) no_of_portals,
                    case when m.portal LIKE 'WB%' then 'WB' 
	                      when m.portal not LIKE 'WB%' and length(ma.distributed_by_parent)<=0 then 'Other'  
	                      when ma.distributed_by_parent IS NULL then 'Other'     
                     ELSE ma.distributed_by_parent END studio,
                     (SELECT COUNT(1) FROM movie_ids WHERE vonly_asset_id=m.vonly_asset_id and portal not in ('Amazon Movies & TV')) no_of_titles
                    FROM  movie_ids m 
                    LEFT OUTER JOIN pricm_staging.movies ma ON
                    m.portal=ma.portal AND m.region=ma.region AND m.portal_item_id=ma.portal_item_id and ma.portal not in ('Amazon Movies & TV')
                    where m.portal not in ('Amazon Movies & TV')
                    GROUP BY m.vonly_asset_id
                    ) per GROUP BY studio """
        caption = "Title Mapping By Studio without Amazon Movies & TV "
    
    print(query)
    def_cursor = connection.cursor()        
    def_cursor.execute(query)
    records = def_cursor.fetchall()
    
    total_1 = 0 
    total_2 = 0
    total_3 = 0
    total_4 = 0
    total_5 = 0
    total_6 = 0
    total_7 = 0
    total_8 = 0
    total_9 = 0
    total_10 = 0

    page_content += "<center><table class=customers ><caption> " + caption + " </caption><TR><Th>Studio</Th><Th># VAIDs</Th><Th># Titles</Th><Th>1 Portal</Th><Th>2 Portal</Th><Th>3 Portal</Th><Th>4 Portal</Th><Th>5 Portal</Th><Th>6 Portal</Th><Th>7 Portal</Th><Th>8 Portal</Th></TR>"
    
    for row in records:
        percentage_1 = round(row[1] * 100 / row[9],2)
        percentage_2 = round(row[2] * 100 / row[9],2)
        percentage_3 = round(row[3] * 100 / row[9],2)
        percentage_4 = round(row[4] * 100 / row[9],2)
        percentage_5 = round(row[5] * 100 / row[9],2)
        percentage_6 = round(row[6] * 100 / row[9],2)
        percentage_7 = round(row[7] * 100 / row[9],2)
        percentage_8 = round(row[8] * 100 / row[9],2)

        total_1 = total_1 + row[1]
        total_2 = total_2 + row[2]
        total_3 = total_3 + row[3]
        total_4 = total_4 + row[4]
        total_5 = total_5 + row[5]
        total_6 = total_6 + row[6]
        total_7 = total_7 + row[7]
        total_8 = total_8 + row[8]
        total_9 = total_9 + row[9]
        total_10 = total_10 + row[10]

        page_content += "<TR ><TD >" + str(row[0]) + "</TD>"
        page_content += "<TD nowrap align=right >" + f'{row[10]:,}' + "</TD>"
        page_content += "<TD nowrap align=right >" + f'{row[9]:,}' + "</TD>"
        page_content += "<TD nowrap align=right >" + str(percentage_1) + "%</TD>"
        page_content += "<TD nowrap align=right >" + str(percentage_2) + "%</TD>"
        page_content += "<TD nowrap align=right >" + str(percentage_3) + "%</TD>"
        page_content += "<TD nowrap align=right >" + str(percentage_4) + "%</TD>"
        page_content += "<TD nowrap align=right >" + str(percentage_5) + "%</TD>"
        page_content += "<TD nowrap align=right >" + str(percentage_6) + "%</TD>"
        page_content += "<TD nowrap align=right >" + str(percentage_7) + "%</TD>"
        page_content += "<TD nowrap align=right >" + str(percentage_8) + "%</TD>"        
        page_content += "</TR>"
    

    page_content += "<TR ><TD align=right>Total </TD>"
    page_content += "<TD nowrap align=right>" + f'{total_10:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_9:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_1:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_2:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_3:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_4:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_5:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_6:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_7:,}' + "</TD>"
    page_content += "<TD nowrap align=right>" + f'{total_8:,}' + "</TD>"

    page_content += "</TR>"
    page_content += "</table></centre>"

    return page_content

def Dashboard_Portal(connection):

        page_content = ""

        query = """ SELECT COUNT(DISTINCT vonly_asset_id),count(1) FROM movie_ids """ 
        caption = "Title Mapping by Portal"
        
        print(query)
        def_cursor = connection.cursor()        
        def_cursor.execute(query)
        records = def_cursor.fetchall()

        for row in records:
            total_vonly_asset_id = row[0]
            total_title = row[1]        
        
        query = """ SELECT platform, 
                    (select count(distinct vonly_asset_id) from movie_ids WHERE platform IN ('Amazon Movies & TV',mi.platform)) aps_union_data  ,
                    (select  COUNT(DISTINCT m.vonly_asset_id) from movie_ids m INNER JOIN  movie_ids n ON m.vonly_asset_id=n.vonly_asset_id 
                    WHERE m.platform ='Amazon Movies & TV' AND  n.platform=mi.platform) aps_intersect_data ,
                    (select count(distinct vonly_asset_id) from movie_ids WHERE platform IN ('Amazon Prime Video',mi.platform)) amazon_union_data,
                    (select  COUNT(DISTINCT m.vonly_asset_id) from movie_ids m INNER JOIN  movie_ids n ON m.vonly_asset_id=n.vonly_asset_id 
                    WHERE m.platform ='Amazon Prime Video' AND  n.platform=mi.platform) amazon_intersect_data,
                    (select count(distinct vonly_asset_id) from movie_ids WHERE platform IN ('Google Play',mi.platform)) google_union_data,
                    (select  COUNT(DISTINCT m.vonly_asset_id) from movie_ids m INNER JOIN  movie_ids n ON m.vonly_asset_id=n.vonly_asset_id 
                    WHERE m.platform ='Google Play' AND  n.platform=mi.platform) google_intersect_data,
                    (select count(distinct vonly_asset_id) from movie_ids WHERE platform IN ('iTunes',mi.platform)) itunes_union_data,
                    (select  COUNT(DISTINCT m.vonly_asset_id) from movie_ids m INNER JOIN  movie_ids n ON m.vonly_asset_id=n.vonly_asset_id 
                    WHERE m.platform ='iTunes' AND  n.platform=mi.platform) itunes_intersect_data,
                    (select count(distinct vonly_asset_id) from movie_ids WHERE platform IN ('VUDU',mi.platform)) vudu_union_data,
                    (select  COUNT(DISTINCT m.vonly_asset_id) from movie_ids m INNER JOIN  movie_ids n ON m.vonly_asset_id=n.vonly_asset_id 
                    WHERE m.platform ='VUDU' AND  n.platform=mi.platform) vudu_intersect_data,
                    (select count(distinct vonly_asset_id) from movie_ids WHERE platform IN ('WB MPM-VVId',mi.platform)) mpm_union_data,
                    (select  COUNT(DISTINCT m.vonly_asset_id) from movie_ids m INNER JOIN  movie_ids n ON m.vonly_asset_id=n.vonly_asset_id 
                    WHERE m.platform ='WB MPM-VVId' AND  n.platform=mi.platform) mpm_intersect_data,
                    (select count(distinct vonly_asset_id) from movie_ids WHERE platform IN ('WB UPC',mi.platform)) upc_union_data,
                    (select  COUNT(DISTINCT m.vonly_asset_id) from movie_ids m INNER JOIN  movie_ids n ON m.vonly_asset_id=n.vonly_asset_id 
                    WHERE m.platform ='WB UPC' AND  n.platform=mi.platform) upc_intersect_data,
                    (select count(distinct vonly_asset_id) from movie_ids WHERE platform IN ('YouTube',mi.platform)) youtube_union_data,
                    (select  COUNT(DISTINCT m.vonly_asset_id) from movie_ids m INNER JOIN  movie_ids n ON m.vonly_asset_id=n.vonly_asset_id 
                    WHERE m.platform ='YouTube' AND  n.platform=mi.platform) youtube_intersect_data,
                    (SELECT COUNT(1) FROM movie_ids WHERE platform=mi.platform) title,
                    (SELECT COUNT(DISTINCT vonly_asset_id) FROM movie_ids WHERE platform=mi.platform) vonly_asset_id
                    FROM movie_ids mi
                    GROUP BY platform
                    """
        print(query)
        def_cursor = connection.cursor()        
        def_cursor.execute(query)
        records = def_cursor.fetchall()
            
        page_content += "<center><table class=customers ><caption> " + caption + " </caption><TR><Th>Portal</Th> <Th># VAIDs</Th> <Th># Titles</Th><Th>Amazon Movies & TV</Th><Th>Amazon Prime Video</Th><Th>Google Play</Th><Th>iTunes</Th><Th>VUDU</Th><Th>WB MPM-VVId</Th><Th>WB UPC</Th><Th>YouTube</Th></TR>"
        
        i = 1
        aps_vonly_asset_id =0
        amazon_vonly_asset_id =0
        google_vonly_asset_id =0
        itunes_vonly_asset_id =0
        vudu_vonly_asset_id =0
        mpm_vonly_asset_id =0
        upc_vonly_asset_id =0
        youtube_vonly_asset_id =0

        for row in records:
            percentage_1 = round(row[2] * 100 / row[1],2)
            percentage_2 = round(row[4] * 100 / row[3],2)
            percentage_3 = round(row[6] * 100 / row[5],2)
            percentage_4 = round(row[8] * 100 / row[7],2)
            percentage_5 = round(row[10] * 100 / row[9],2)
            percentage_6 = round(row[12] * 100 / row[11],2)
            percentage_7 = round(row[14] * 100 / row[13],2)
            percentage_8 = round(row[16] * 100 / row[15],2)   
            
            if  i == 1:
                aps_vonly_asset_id = row[2]
            if  i == 2:
                amazon_vonly_asset_id = row[4]
            if  i == 3:
                google_vonly_asset_id = row[6]
            if  i == 4:
                itunes_vonly_asset_id = row[8]
            if  i == 5:
                vudu_vonly_asset_id = row[10]
            if  i == 6:
                mpm_vonly_asset_id = row[12]
            if  i == 7:
                upc_vonly_asset_id = row[14]
            if  i == 8:
                youtube_vonly_asset_id = row[16]

            page_content += "<TR ><TD >" + str(row[0]) + "</TD>"
            page_content += "<TD nowrap align=right >" + f'{row[18]:,}' + "</TD>"
            page_content += "<TD nowrap align=right >" + f'{row[17]:,}' + "</TD>"
            page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage_1) + " 1%,white " + str(percentage_1) + "%);' >" + str(percentage_1) + "%</TD>"
            page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage_2) + " 1%,white " + str(percentage_2) + "%);' >" + str(percentage_2) + "%</TD>"
            page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage_3) + " 1%,white " + str(percentage_3) + "%);' >" + str(percentage_3) + "%</TD>"
            page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage_4) + " 1%,white " + str(percentage_4) + "%);' >" + str(percentage_4) + "%</TD>"
            page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage_5) + " 1%,white " + str(percentage_5) + "%);' >" + str(percentage_5) + "%</TD>"
            page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage_6) + " 1%,white " + str(percentage_6) + "%);' >" + str(percentage_6) + "%</TD>"
            page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage_7) + " 1%,white " + str(percentage_7) + "%);' >" + str(percentage_7) + "%</TD>"
            page_content += "<TD nowrap align=right style='background: -webkit-linear-gradient(left," + getColor(percentage_8) + " 1%,white " + str(percentage_8) + "%);' >" + str(percentage_8) + "%</TD>"
            page_content += "</TR>"   
            i = i  + 1
        
        page_content += "<TR ><TD align=right>Total </TD>"
        page_content += "<TD nowrap align=right>" + f'{total_vonly_asset_id:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{total_title:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{aps_vonly_asset_id:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{amazon_vonly_asset_id:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{google_vonly_asset_id:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{itunes_vonly_asset_id:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{vudu_vonly_asset_id:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{mpm_vonly_asset_id:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{upc_vonly_asset_id:,}' + "</TD>"
        page_content += "<TD nowrap align=right>" + f'{youtube_vonly_asset_id:,}' + "</TD>" 
        page_content += "</TR>"
        page_content += "</table></centre>"
        return page_content

@app.route('/dashboard')
def dashboard():
    # Render the page
    page_content = ""
    page_content += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 2px;} "
    page_content += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: center;  background-color: #002060;  color: white;}</style>"

    page_content += "<script> function form_submit(portal,studio,percentage) { document.forms[0].studio.value=studio; document.forms[0].portal.value=portal; document.forms[0].percentage.value=percentage; document.forms[0].submit();} </script> <form method=POST name=main action=/details target=_blank ><input type=hidden name=portal><input type=hidden name=studio><input type=hidden name=percentage></form> "

    try:
        connection = mysql.connector.connect(host='192.168.12.102',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')
        #connection = mysql.connector.connect(host='192.168.100.202',
        #                                 database='vonly_data_feed_us_development',
        #                                 user='vonly-dev',
        #                                 password='z9mtDkpjSsTMjRqhws')
        
        #page_content += "<table class=customers ><TR><td>"
        page_content+= Dashboard_Top(connection,0)   
        #page_content += "</td><td >"
        #page_content+= Dashboard_Top(connection,1)
        #page_content += "</td></tr></table>"
        page_content +="<BR>"
        page_content += Dashboard_Studio(connection,0)
        #page_content += Dashboard_Studio(connection,1)
        page_content +="<BR>"
        page_content += Dashboard_Portal(connection)

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()            
            print("MySQL connection is closed")

    return page_content

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('192.168.100.222', 4448,debug=True)
