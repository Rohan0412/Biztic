from flask import Flask
from flask import request
import mysql.connector
from mysql.connector import Error

# Mounting the drive
#from google.colab import drive
#drive.mount('/content/drive')

# Required Basic libraries
import uuid
#import pandas as pd
import os
import requests
#from PIL import Image ,ImageOps
#import matplotlib.pyplot as plt
#import numpy as np
#import cv2 as cv2
#from google.colab.patches import cv2_imshow
import math
#from tqdm import tqdm
import datetime as dt
#from scipy import stats
#from skimage import transform
#from scipy.spatial.distance import hamming,cosine

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
    page_content += """<th><a href=/checktitle target=_blank > Search By Title</a></th>"""
    page_content += """<th><a href=/check target=_blank > Search By VONLY Asset ID </a></th>"""    
    page_content += "</tr>"
    page_content += "</table></body>"

    return page_content

# for resetting the Tensorflow graph
os.environ['PYTHONHASHSEED'] = '0'
#tf.keras.backend.clear_session()
# for reproducible result
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

def getColor(value):
    color = ""
    if value <= 25:
        color = "#ff0000"
    if value > 25 and value <= 75:
        color = "#ffb629"
    if value > 75:
        color = "#22b14c"
    return color

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
    page_content_check += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px;vertical-align: top;} "    
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
               set_clause = "UPDATE tv_ids set vonly_asset_id='%s'" % (new_vonly_asset_id)
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
                                            tis.num AS season_number,
                                            tis.vonly_asset_id AS season_vonly_asset_id,
   
                                        (SELECT 
                                            GROUP_CONCAT(title,'<BR>','<input type="checkbox" name=', portal_item_id, '> ', portal_item_id) 
                                        FROM 
                                            tv_ids 
                                        WHERE 
                                            platform='wb mpm-vvid' AND
                                            vonly_asset_id=tis.vonly_asset_id) as mpm_vvid,

                                        (SELECT 
                                            GROUP_CONCAT(
                                            DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://itunes.apple.com/us/tv-season/title/id',IFNULL(ti_1.portal_item_id," "),'>','<input type=checkbox name=',IFNULL(ti_1.portal_item_id," "),'>',IFNULL(ti_1.portal_item_id," "),'</a>',
                                            '<BR><BR>',
                                            CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'),
                                            '<BR>',
                                            IFNULL(ti_1.title," "),'(',IFNULL(ti_1.num," "),')' ,
                                            '<BR><BR>',
                                            (SELECT 
                                                CONCAT('<table>',IFNULL (GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ' )," "),'</table>')
                                            FROM 
                                                vonly_data_feed_us_staging.tv_ids tie
                                            INNER JOIN 
                                                tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                            INNER JOIN 
                                                tv_ids tisi on tisi.id=timi.season_vonly_id
                                            WHERE  
                                                tisi.id IN ( SELECT 
                                                                t.id 
                                                            FROM 
                                                                tv_ids t 
                                                            WHERE 
                                                                t.portal_item_id=ti_1.portal_item_id AND 
                                                                platform = 'itunes') 
                                            AND 
                                                tisi.platform='itunes' AND  tie.scope='tv_episode'  ),
                                            '<BR>',
                                            'Episodes:',
                                            (SELECT 
                                                COUNT(DISTINCT tie.num) 
                                            FROM 
                                                vonly_data_feed_us_staging.tv_ids tie
                                            INNER JOIN 
                                                tv_id_mappings timi ON tie.id = timi.episode_vonly_id 
                                            INNER JOIN 
                                                tv_ids tisi ON tisi.id = timi.season_vonly_id
                                            WHERE tisi.vonly_asset_id = tis.vonly_asset_id AND
                                                  tisi.platform = 'itunes' AND 
                                                  tie.scope = 'tv_episode'),'<BR>') 
                                                  separator '<BR>'
                                            ) 
                                        FROM 
                                            tv_ids ti_1
                                        INNER JOIN 
                                            sandbox.tvshows ts ON ts.vonly_id = ti_1.id 
                                        WHERE 
                                            ti_1.platform = 'itunes' AND ti_1.vonly_asset_id = tis.vonly_asset_id
                                        ) AS itunes_final, 

                                        (SELECT 
                                            GROUP_CONCAT(
                                            DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://www.vudu.com/content/browse/details/title/',IFNULL(ti_1.portal_item_id," "),'>','<input type=checkbox name=',IFNULL(ti_1.portal_item_id," "),'>',IFNULL(ti_1.portal_item_id," "), '</a>',
                                            '<BR><BR>',
                                            CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'),
                                            '<BR>',
                                            IFNULL(ti_1.title," "),'(',IFNULL(ti_1.num," "),')' ,
                                            '<BR><BR>',
                                            (SELECT 
                                                CONCAT('<table>',IFNULL( GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ')," "),'</table>')
                                            FROM 
                                                vonly_data_feed_us_staging.tv_ids tie
                                            INNER JOIN 
                                                tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                            INNER JOIN 
                                                tv_ids tisi on tisi.id=timi.season_vonly_id
                                            WHERE  tisi.id IN ( SELECT 
                                                                    t.id 
                                                                FROM 
                                                                    tv_ids t 
                                                                WHERE 
                                                                    t.portal_item_id=ti_1.portal_item_id AND
                                                                    platform = 'vudu')
                                            AND 
                                                tisi.platform='vudu' AND  tie.scope='tv_episode'  ),
                                            '<BR>',
                                            'Episodes:',
                                            (SELECT 
                                                COUNT(DISTINCT tie.num) 
                                            FROM 
                                                vonly_data_feed_us_staging.tv_ids tie
                                            INNER JOIN 
                                                tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                            INNER JOIN 
                                                tv_ids tisi on tisi.id=timi.season_vonly_id
                                            WHERE  
                                                tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                tisi.platform='vudu' AND 
                                                tie.scope='tv_episode'  ),
                                            '<BR>')
                                            SEPARATOR '<BR>'
                                            ) 
                                        FROM 
                                            tv_ids ti_1
                                        INNER JOIN 
                                            sandbox.tvshows ts ON ts.vonly_id = ti_1.id  
                                        WHERE 
                                            ti_1.platform = 'vudu' AND
                                            ti_1.vonly_asset_id = tis.vonly_asset_id
                                        ) AS vudu_final,  

                                        (SELECT 
                                            GROUP_CONCAT(
                                            DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://play.google.com/store/tv/show/?id=',IFNULL(tsi.portal_item_id," "),'&hl=en_US&gl=US&cdid=tvseason-',IFNULL(ti_1.portal_item_id," "),'>','<input type=checkbox name=',IFNULL(ti_1.portal_item_id," "),'>',IFNULL(ti_1.portal_item_id," "),'</a>',
                                            '<BR><BR>',
                                            CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'),
                                            '<BR>',
                                            IFNULL(ti_1.title," "),'(',IFNULL(ti_1.num," "),')' ,
                                            '<BR><BR>',
                                            (SELECT 
                                                CONCAT(' ','<table>',IFNULL (GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ')," "),'</table>')
                                                FROM 
                                                    vonly_data_feed_us_staging.tv_ids tie
                                                INNER JOIN 
                                                    tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                INNER JOIN 
                                                    tv_ids tisi on tisi.id=timi.season_vonly_id
                                                WHERE  
                                                    tisi.id IN ( SELECT 
                                                                    t.id 
                                                                FROM 
                                                                    tv_ids t 
                                                                WHERE 
                                                                    t.portal_item_id=ti_1.portal_item_id AND
                                                                    platform = 'google play')
                                                AND 
                                                    tisi.platform='google play' AND
                                                    tie.scope='tv_episode'  ),
                                                '<BR>',
                                                'Episodes:',
                                                ( SELECT 
                                                    COUNT(DISTINCT tie.num) 
                                                FROM 
                                                    vonly_data_feed_us_staging.tv_ids tie
                                                INNER JOIN 
                                                    tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                INNER JOIN 
                                                    tv_ids tisi on tisi.id=timi.season_vonly_id
                                                WHERE  
                                                    tisi.vonly_asset_id=tis.vonly_asset_id AND 
                                                    tisi.platform='google play' AND
                                                    tie.scope='tv_episode'),
                                                '<BR>') 
                                            separator '<BR>'
                                            ) 
                                            FROM 
                                                tv_ids ti_1 
                                            INNER JOIN 
                                                tv_id_mappings tim ON ti_1.id=tim.season_vonly_id
                                            INNER JOIN 
                                                tv_ids tsi ON tim.show_vonly_id=tsi.id
                                            INNER JOIN 
                                                sandbox.tvshows ts ON ts.vonly_id = ti_1.id 
                                            WHERE 
                                                ti_1.platform = 'google play' AND
                                                ti_1.vonly_asset_id = tis.vonly_asset_id AND
                                                ti_1.portal = 'google play'
                                        ) AS google_final,

                                        (SELECT 
                                            GROUP_CONCAT(
                                            DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://amazon.com/gp/video/detail/',IFNULL(ti_1.portal_item_id," "),'>','<input type=checkbox name=',IFNULL(ti_1.portal_item_id," "),'>',IFNULL(ti_1.portal_item_id," "),'</a>',
                                            '<BR><BR>',
                                            CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'),
                                            '<BR>',
                                            IFNULL(ti_1.title," "),'(',IFNULL(ti_1.num," "),')' ,
                                            '<BR><BR>',
                                            (SELECT  
                                                CONCAT('<table>',IFNULL (GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ')," "),'</table>')
                                            FROM 
                                                vonly_data_feed_us_staging.tv_ids tie
                                            INNER JOIN 
                                                tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                            INNER JOIN 
                                                tv_ids tisi on tisi.id=timi.season_vonly_id
                                            WHERE  
                                                tisi.id IN ( SELECT 
                                                                t.id 
                                                            FROM 
                                                                tv_ids t 
                                                            WHERE 
                                                                t.portal_item_id=ti_1.portal_item_id AND
                                                                platform = 'Amazon Prime Video')
                                            AND 
                                                tisi.platform='amazon prime video' AND
                                                tie.scope='tv_episode'  ),
                                            '<BR>',
                                            'Episodes:',
                                            (SELECT 
                                                COUNT(DISTINCT tie.num) 
                                            FROM 
                                                vonly_data_feed_us_staging.tv_ids tie
                                            INNER JOIN 
                                                tv_id_mappings timi ON tie.id = timi.episode_vonly_id 
                                            INNER JOIN 
                                                tv_ids tisi ON tisi.id = timi.season_vonly_id
                                            WHERE 
                                                tisi.vonly_asset_id = tis.vonly_asset_id AND 
                                                tisi.platform = 'Amazon Prime Video' AND 
                                                tie.scope = 'tv_episode'),
                                            '<BR>') 
                                            separator '<BR>'
                                                    )
                                            FROM 
                                                tv_ids ti_1
                                            INNER JOIN 
                                                sandbox.tvshows ts ON ts.vonly_id = ti_1.id  
                                            WHERE 
                                                ti_1.platform = 'amazon prime video' AND
                                                ti_1.vonly_asset_id = tis.vonly_asset_id
                                            ) AS amazon_final,
                                            
                                            (SELECT 
                                                GROUP_CONCAT(
                                                DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://tv.apple.com/us/season/season/',IFNULL(ti_1.portal_item_id," "),'?showId=', IFNULL(ti_show.portal_item_id," "),' >', '<input type=checkbox name=',IFNULL(ti_1.portal_item_id," "),'>',IFNULL(ti_1.portal_item_id," "), '</a>',
                                                '<BR><BR>',
                                                CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'),
                                                '<BR>',
                                                IFNULL(ti_1.title," "),'(',IFNULL(ti_1.num," "),')' ,
                                                '<BR><BR>',
                                                (SELECT 
                                                    CONCAT('<table>',IFNULL (GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ')," "),'</table>')
                                                FROM 
                                                    vonly_data_feed_us_staging.tv_ids tie
                                                INNER JOIN 
                                                    tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                INNER JOIN 
                                                    tv_ids tisi on tisi.id=timi.season_vonly_id
                                                WHERE  
                                                    tisi.id IN ( SELECT 
                                                                    t.id 
                                                                FROM 
                                                                    tv_ids t 
                                                                WHERE 
                                                                    t.portal_item_id=ti_1.portal_item_id AND 
                                                                    platform = 'appletvapp') AND tisi.platform='appletvapp'  AND  tie.scope='tv_episode'  ),
                                                '<BR>',
                                                'Episodes:',
                                                (SELECT 
                                                    COUNT(DISTINCT tie.num) 
                                                FROM 
                                                    vonly_data_feed_us_staging.tv_ids tie
                                                INNER JOIN 
                                                    tv_id_mappings timi ON tie.id = timi.episode_vonly_id 
                                                INNER JOIN 
                                                    tv_ids tisi ON tisi.id = timi.season_vonly_id
                                                WHERE tisi.vonly_asset_id = tis.vonly_asset_id AND
                                                      tisi.platform = 'appletvapp' AND 
                                                      tie.scope = 'tv_episode'),
                                                '<BR>') 
                                                SEPARATOR '<BR>'
                                                ) 
                                            FROM 
                                                tv_ids ti_1
                                            INNER JOIN 
                                                tv_id_mappings tim ON ti_1.id=tim.season_vonly_id 
                                            INNER JOIN 
                                                tv_ids ti_show ON tim.show_vonly_id= ti_show.id
                                            INNER JOIN 
                                                sandbox.tvshows ts ON ts.vonly_id = ti_1.id 
                                            WHERE 
                                                ti_1.platform = 'appletvapp' AND
                                                ti_1.vonly_asset_id = tis.vonly_asset_id AND
                                                ti_1.portal = 'AppleTV_CanonicalId'
                                        ) AS appletvapp_final
                                                                    

                                        FROM 
                                            tv_ids tis
                                        LEFT OUTER JOIN 
                                            tv_id_mappings tim ON tis.id = tim.season_vonly_id
                                        LEFT OUTER JOIN 
                                            tv_ids tie ON tim.episode_vonly_id = tie.id and tie.scope='tv_episode'                                           
                                        WHERE 
                                            (tis.scope ='tv_season' or tis.scope IS NULL) AND tis.platform IN ('itunes', 'amazon prime video', 'appletvapp', 'vudu', 'google play','wb mpm-vvid') 
                                        AND  tis.vonly_asset_id='%s'
                                        GROUP BY 
                                            tis.vonly_asset_id
                                        ORDER BY 
                                            CAST(tis.num AS SIGNED) , CAST(tie.num AS SIGNED) ASC """ % (tag)

            print(sql_select_Query_check)
            cursor_check = connection_check.cursor()
            cursor_check.execute("SET SESSION group_concat_max_len = 1000000000;")
            cursor_check.execute(sql_select_Query_check)
            records_check = cursor_check.fetchall()

            page_content_check += "<table class=customers ><TR><TH>Title</TH><TH>Season_no</TH><TH>VONLY Asset ID</TH><TH>iTunes Portal Item IDs</TH><TH>VUDU Portal Item IDs</TH><TH>Google Portal Item IDs</TH><TH>Amazon Portal Item IDs</TH><TH>AppleTVApp Portal Item IDs</TH></TR>"
            
            i = 0;
            for row in records_check:
                color= "#e6f7ff " if i % 2 == 0 else "white" 
                page_content_check +="<TR BGCOLOR="+ color +" ><TD rowspan=2 >"+ str(row[0]) +"</TD><TD rowspan=2 >"+ str(row[1]) +"</TD><TD nowrap rowspan=2><input type=checkbox name=" + str(row[2]) + "> <a  onclick=form_submit_vonly_asset_id('" + str(row[2]) + "') > " + str(row[2]) + "</a><input type=radio name=vonly_asset_id value=" + str(row[2]) + "> <BR> <BR> <BR>"+ str(row[3]) +"</TD><TD>" + str(row[4]) + "</TD><TD>" + str(row[5]) + "</TD><TD>" + str(row[6]) +  "</TD><TD>" + str(row[7]) + "</TD><TD>" + str(row[8]) +"</TD></TR>"
                
                # page_content_check += "<TR BGCOLOR="+ color +" ><TD>" + str(row[9]) + "</TD><TD>" + str(row[10]) + "</TD><TD>" + str(row[11]) +  "</TD><TD>" + str(row[12]) + "</TD><TD>" + str(row[13]) +"</TD></TR>"
               
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
        form_content_check = """<form method="POST"> VONLY Asset ID: <input type="text" name="tag" size=50 > <input type="submit" value="Search"></form>"""    

    return form_content_check + page_content_check

@app.route('/checktitle', methods=['GET', 'POST'])
def checktitle():
    # Render the page

    tagtitle = ""
    tag_no_title = ""
    checkbox = 0
    not_tag = ""
    mpm = ""
    
    page_content_checktitle = ""  
    page_content_checktitle += "<style>.customers {  font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;  border-collapse: collapse;  width: 100%;}"
    page_content_checktitle += ".customers td, .customers th {  border: 1px solid #ddd;  padding: 8px; vertical-align: top;} "    
    page_content_checktitle += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  background-color: #002060;  color: white;}</style>"


    if request.method == 'POST':   
        not_tag = request.form['nottag'].replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%")
        tagtitle = request.form['tag'].replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%")
        tag_no_title = request.form['tag_no'].replace("'","%").replace(":","%").replace("-","%").replace("?","%").replace("!","%").replace(",","%").replace(".","%").replace(")","%").replace("(","%").replace("\\","%").replace("/","%")
        mpm = request.form['mpm']
        checkbox_value = request.form.get('my_checkbox')
        
        
        
        print (checkbox_value)
        
        if checkbox_value==None:
            ch_value=""
        else:
            ch_value="checked"
            
        if checkbox_value:
            checkbox=1

        form_content_checktitle = "<script> function form_submit_vonly_asset_id(vonly_asset_id) { document.forms[0].tag.value=vonly_asset_id; document.forms['vonly_asset_id'].submit();} function form_clear() {    document.getElementById('main').reset();;} </script> <form method=POST name=vonly_asset_id action=/check target=_blank ><input type=hidden name=tag></form> "
        form_content_checktitle += """<form method="POST" name=main> Season Title: <input type="text" name="tag" size=20 value='%s'> Season No: <input type="text" name="tag_no" size=5 value='%s'> Season Bundle: <input type="checkbox" id = "my_checkbox" name="my_checkbox" %s > Season Not Title: <input type="text" name="nottag" size=20 value='%s'> MPM-VVID: <input type="text" name="mpm" size=20 value='%s'> <input type="submit" value="Search"> <input type="reset" value="Clear" OnClick="form_clear()"> <input type="submit" value="Update"  >  """ % (tagtitle,tag_no_title,ch_value,not_tag,mpm)      
        
        # form_content_checktitle = "<script> function form_submit_vonly_asset_id(vonly_asset_id) { document.forms[0].tag.value=vonly_asset_id; document.forms['vonly_asset_id'].submit();} function form_clear() {    document.getElementById('main').reset();;} </script> <form method=POST name=vonly_asset_id action=/check target=_blank ><input type=hidden name=tag></form> "
        # form_content_checktitle += """<form method="POST" name=main> Season Title: <input type="text" name="tag" size=20 value='%s'> Season No: <input type="text" name="tag_no" size=5 value='%s'> Season Bundle: <input type="checkbox" id = "my_checkbox" name="my_checkbox" %s > Season Not Title: <input type="text" name="nottag" size=20 value='%s'> MPM-VVID: <input type="text" name="mpm" size=20 value='%s'> <input type="submit" value="Search"> <input type="reset" value="Clear" OnClick="form_clear()"> <input type="submit" value="Update"  >  """ % (
        # tagtitle, tag_no_title, ch_value, not_tag, mpm)
        

        update_query = ""
        set_clause = ""
        where_clause = ""
        where = []
        
        if not_tag =='':
            not_tag = ''
        else:            
            not_tag = not_tag + '%'
            
        if tag_no_title =='all':
            tag_no_title = '%'
        

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

            sql_select_Query_checktitle = """ SELECT 
                                                   GROUP_CONCAT(Distinct tis.title separator '<BR><BR>') AS season_title,
                                                   tis.vonly_asset_id AS season_vonly_asset_id,
                                                   tis.num AS season_number,
                                                   
                                                    (SELECT  
                                                        CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ' ),'</table>')
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                        tisi.platform='itunes' AND
                                                        tie.scope='tv_episode') AS itunes_episodes_list,

                                                    (SELECT  
                                                        CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                        tisi.platform='amazon prime video' AND
                                                        tie.scope='tv_episode'  ) AS amazon_episodes_list,
                                              
                                                    (SELECT  
                                                        CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND 
                                                        tisi.platform='appletvapp'  AND
                                                        tie.scope='tv_episode'  ) AS appletvapp_episodes_list,
                                                
                                                
                                                    (SELECT  
                                                        CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                        tisi.platform='vudu' AND
                                                        tie.scope='tv_episode'  ) AS vudu_episodes_list,
                                                
                                                
                                                    (SELECT  
                                                        CONCAT('<table>',GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' '),'</table>')
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                        tisi.platform='google play' AND
                                                        tie.scope='tv_episode'  ) AS googleplay_episodes_list ,


                                                    (SELECT  
                                                        GROUP_CONCAT(distinct title,'<BR>',portal_item_id) 
                                                    FROM 
                                                        tv_ids 
                                                    WHERE 
                                                        scope='tv_season' AND
                                                        platform='wb mpm-vvid' AND
                                                        vonly_asset_id=tis.vonly_asset_id) as mpm_vvid,   


                                                    (SELECT 
                                                        GROUP_CONCAT(
                                                        DISTINCT CONCAT(IFNULL(ti_1.title,""),'(',IFNULL(ti_1.num,""),')' ,'<BR>','<a target="_blank" rel="noopener" href=https://amazon.com/gp/video/detail/',IFNULL(ti_1.portal_item_id,""),'>',IFNULL(ti_1.portal_item_id,""),'</a>' ,
                                                        '<BR>',
                                                        CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'))
                                                        separator '<BR><BR>'
                                                        ) 
                                                    FROM 
                                                        tv_ids ti_1 
                                                    INNER JOIN 
                                                        sandbox.tvshows ts ON ts.vonly_id = ti_1.id
                                                    WHERE 
                                                        ti_1.platform = 'amazon prime video' AND 
                                                        ti_1.vonly_asset_id =tis.vonly_asset_id) AS amazon_ids,

                                                    (SELECT 
                                                        GROUP_CONCAT(
                                                        DISTINCT CONCAT(IFNULL(ti_1.title,""),'(',IFNULL(ti_1.num,""),')' ,'<BR>','<a target="_blank" rel="noopener" href=https://www.vudu.com/content/browse/details/title/',IFNULL(ti_1.portal_item_id,""),'>',IFNULL(ti_1.portal_item_id,""), '</a>','<BR>',
                                                        CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'))
                                                        SEPARATOR '<BR><BR>'
                                                        ) 
                                                    FROM 
                                                        tv_ids ti_1 
                                                    INNER JOIN 
                                                            sandbox.tvshows ts ON ts.vonly_id = ti_1.id
                                                    WHERE 
                                                        ti_1.platform = 'vudu' AND 
                                                        ti_1.vonly_asset_id = tis.vonly_asset_id) AS vudu_ids,

                                                    (
                                                    SELECT 
                                                    GROUP_CONCAT(
                                                    DISTINCT CONCAT(IFNULL(ti_1.title,""),'(',IFNULL(ti_1.num,""),')' ,'<BR>','<a target="_blank" rel="noopener" href=https://tv.apple.com/us/season/season/',IFNULL(ti_1.portal_item_id,""),'?showId=', IFNULL(ti_show.portal_item_id,""),' >', IFNULL(ti_1.portal_item_id,""), '</a>','<BR>',
                                                    CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'))
                                                    SEPARATOR '<BR><BR>'
                                                    ) 
                                                    FROM 
                                                    tv_ids ti_1
                                                    INNER JOIN 
                                                    tv_id_mappings tim ON ti_1.id=tim.season_vonly_id 
                                                    INNER JOIN 
                                                    tv_ids ti_show ON tim.show_vonly_id= ti_show.id
                                                    INNER JOIN 
                                                    sandbox.tvshows ts ON ts.vonly_id = ti_1.id
                                                    WHERE 
                                                    ti_1.platform = 'appletvapp' AND 
                                                    ti_1.vonly_asset_id = tis.vonly_asset_id AND 
                                                    ti_1.portal = 'AppleTV_CanonicalId') AS appletvapp_ids,

                                                    (
                                                    SELECT 
                                                        GROUP_CONCAT(
                                                        DISTINCT CONCAT(IFNULL(ti_1.title,""),'(',IFNULL(ti_1.num,""),')' ,'<BR>','<a target="_blank" rel="noopener" href=https://itunes.apple.com/us/tv-season/title/id',IFNULL(ti_1.portal_item_id,""),'>',IFNULL(ti_1.portal_item_id,""),'</a>','<BR>',
                                                        CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'))
                                                        SEPARATOR '<BR><BR>'
                                                        ) 
                                                    FROM 
                                                        tv_ids ti_1 
                                                    INNER JOIN 
                                                            sandbox.tvshows ts ON ts.vonly_id = ti_1.id
                                                    WHERE 
                                                        ti_1.platform = 'itunes' AND 
                                                        ti_1.vonly_asset_id = tis.vonly_asset_id) AS itunes_ids,

                                                    (
                                                    SELECT 
                                                        GROUP_CONCAT(
                                                        DISTINCT CONCAT(IFNULL(ti_1.title,""),'(',IFNULL(ti_1.num,""),')' ,'<BR>','<a target="_blank" rel="noopener" href=https://play.google.com/store/tv/show/?id=',IFNULL(tsi.portal_item_id,""),'&hl=en_US&gl=US&cdid=tvseason-',IFNULL(ti_1.portal_item_id,""),'>',IFNULL(ti_1.portal_item_id,""),'</a>','<BR>',
                                                        CONCAT('<table border=3>',
                                                        CASE
                                                            WHEN ts.director = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Director: ",'</td><td>',ts.director,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.actors = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Actors: ",'</td><td>',ts.actors,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.writers = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Writers: ",'</td><td>',ts.writers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.producers = ' ' THEN ' ' 
                                                            ELSE IFNULL(concat('<tr><td>',"Producers: ",'</td><td>',ts.producers,'</td></tr>')," ")
                                                        END,
                                                        CASE
                                                            WHEN ts.produced_by_parent = ' ' THEN ' ' 
                                                            ELSE IFNULL(CONCAT('<tr><td>',"Studio: ",'</td><td>',ts.produced_by_parent,'</td></tr>')," ")
                                                        END
                                                        ,
                                                        '</table>'))
                                                        SEPARATOR '<BR><BR>'
                                                        ) 
                                                    FROM 
                                                        tv_ids ti_1 
                                                    INNER JOIN 
                                                        tv_id_mappings tim ON ti_1.id=tim.season_vonly_id
                                                    INNER JOIN 
                                                        tv_ids tsi ON tim.show_vonly_id=tsi.id
                                                    INNER JOIN 
                                                            sandbox.tvshows ts ON ts.vonly_id = ti_1.id
                                                    WHERE 
                                                        ti_1.platform = 'google play' AND 
                                                        ti_1.vonly_asset_id = tis.vonly_asset_id AND 
                                                        ti_1.portal = 'google play') AS google_ids,                                               


                                                    (SELECT 
                                                        COUNT(DISTINCT tie.num) 
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id = timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi ON tisi.id = timi.season_vonly_id
                                                    WHERE 
                                                        tisi.vonly_asset_id = tis.vonly_asset_id AND
                                                        tisi.platform = 'itunes' AND
                                                        tie.scope = 'tv_episode') AS itunes_episodes_no,

                                                    (SELECT 
                                                        COUNT(DISTINCT tie.num) 
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                        tisi.platform='amazon prime video' AND
                                                        tie.scope='tv_episode'  ) AS amazon_episodes_no,
                                            
                                                    (SELECT  
                                                        COUNT(DISTINCT tie.num) 
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                        tisi.platform='appletvapp'  AND
                                                        tie.scope='tv_episode'  ) AS appletvapp_episodes_no,
                                                                                                
                                                                                                
                                                    (SELECT 
                                                        COUNT(DISTINCT tie.num) 
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                        tisi.platform='vudu' AND
                                                        tie.scope='tv_episode'  ) AS vudu_episodes_no,
                                                                                                
                                                                                                
                                                    ( SELECT 
                                                        COUNT(DISTINCT tie.num) 
                                                    FROM 
                                                        vonly_data_feed_us_staging.tv_ids tie
                                                    INNER JOIN 
                                                        tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
                                                    INNER JOIN 
                                                        tv_ids tisi on tisi.id=timi.season_vonly_id
                                                    WHERE  
                                                        tisi.vonly_asset_id=tis.vonly_asset_id AND
                                                        tisi.platform='google play' AND
                                                        tie.scope='tv_episode'  ) AS googleplay_episodes_no 
                                        
                                                    FROM 
                                                        tv_ids tis
                                                    LEFT OUTER JOIN 
                                                        tv_id_mappings tim ON tis.id = tim.season_vonly_id
                                                    LEFT OUTER JOIN 
                                                        tv_ids tie ON tim.episode_vonly_id = tie.id and tie.scope='tv_episode'                                           
                                                    WHERE 
                                                        (
                                                        (tis.scope ='tv_season' or tis.scope IS NULL) AND
                                                        tis.platform IN ('itunes', 'amazon prime video', 'appletvapp', 'vudu', 'google play','wb mpm-vvid') AND 
                                                        (case 
                                                            when '%s' = '1' 
                                                                then (tis.title LIKE '%s' or tis.title like '%s' or tis.title like '%s' or tis.title like '%s' or tis.title like '%s')
                                                            ELSE 
                                                                (tis.title like '%s' AND tis.title not like '%s' AND tis.title not like '%s' AND tis.title not like '%s'  AND tis.title not like '%s')
                                                            END) AND
                                                            (tis.num = '%s' or tis.num is null) AND
                                                            tis.title not like '%s' ) OR
                                                            (tis.portal_item_id='%s' and tis.platform='wb mpm-vvid')
                                                    GROUP BY 
                                                        tis.vonly_asset_id
                                                    ORDER BY 
                                                        CAST(tis.num AS SIGNED) DESC , tis.title """ % (str(checkbox),tagtitle + "%",tagtitle + "%_-_%",tagtitle + "%bundle%",tagtitle + "%complete season%",tagtitle + '%complete series%',tagtitle + "%",tagtitle + "%_-_%",tagtitle + "%bundle%",tagtitle + "%complete season%",'%complete series%',tag_no_title, not_tag,mpm )
    
            
            page_content_checktitle += "<h3>Search results for: %s </h3>" % (tagtitle)

            page_content_checktitle += "<table class=customers ><TR><TH>Title</TH><TH>Season_no</TH><TH>VONLY Asset ID <BR> MPM-VVID </TH><TH>iTunes Portal Item IDs</TH><TH>VUDU Portal Item IDs</TH><TH>Google Portal Item IDs</TH><TH>Amazon Portal Item IDs</TH><TH>AppleTVApp Portal Item IDs</TH></TR>"
            
            if tagtitle=='': 
                page_content_checktitle += "</table></form>"
                
                return form_content_checktitle + page_content_checktitle
            
            print("*************************************")
            print(sql_select_Query_checktitle)
            print("*************************************")
            # print(tag_no_title,tagtitle,"yoyoyoyo",checkbox," h i ",checkbox_value)
            cursor_checktitle = connection_checktitle.cursor()
            cursor_checktitle.execute("SET SESSION group_concat_max_len = 1000000000;")
            cursor_checktitle.execute(sql_select_Query_checktitle)
            records_checktitle = cursor_checktitle.fetchall() 
            #r tis.title like '%s' or tis.title like '%s'     
            #tagtitle + "%_-_%",tagtitle + "%bundle%",
            
            i = 0;
            for row in records_checktitle:
                color= "#e6f7ff " if i % 2 == 0 else "white" 
                page_content_checktitle +="<TR BGCOLOR="+ color +" ><TD rowspan=2 >"+ str(row[0]) +"</TD><TD rowspan=2 >"+ str(row[2]) +"</TD><TD nowrap rowspan=2><input type=checkbox name=" + str(row[1]) + "> <a  onclick=form_submit_vonly_asset_id('" + str(row[1]) + "') > " + str(row[1]) + "</a><input type=radio name=vonly_asset_id value=" + str(row[1]) + "> <BR> <BR> <BR>"+ str(row[8]) +"</TD><TD>" + str(row[12]) + " <BR><BR> Episode(s): " + str(row[14]) + "</TD><TD>" + str(row[10]) + " <BR><BR> Episode(s): " + str(row[17]) + "</TD><TD>" + str(row[13]) +  " <BR><BR> Episode(s): " + str(row[18]) + "</TD><TD>" + str(row[9]) + " <BR><BR> Episode(s): " + str(row[15]) +  "</TD><TD>" + str(row[11]) + " <BR><BR> Episode(s): " + str(row[16]) +  "</TD></TR>"
                page_content_checktitle += "<TR BGCOLOR="+ color +" ><TD>"+ str(row[3]) + "</TD><TD>"+ str(row[6]) +"</TD><TD>"+ str(row[7]) +"</TD><TD>"+ str(row[4]) +"</TD><TD>"+ str(row[5]) + "</TD></TR>"
                
               
                
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
        form_content_checktitle = "<script> function validate() { if (document.forms[0].tag.value=='') { alert('Please enter title to search'); return false; }else {document.forms[0].submit(); return true;} } </script>"
        form_content_checktitle = form_content_checktitle + """<form method="POST"> Season Title: <input type="text" name="tag" size=20 > Season No: <input type="text" name="tag_no" size=5 > Season Bundle:<input type="checkbox" id = "my_checkbox" name="my_checkbox">  Season Not Title: <input type="text" name="nottag" size=20 > MPM-VVID: <input type="text" name="mpm" size=20 >  <input type="submit" value="Search" OnClick="return validate()"> <input type="reset" value="Clear"></form>"""    

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

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('192.168.100.222', 4448,debug=True)
