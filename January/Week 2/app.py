from flask import Flask
from flask import request
from flask import render_template
import mysql.connector
from mysql.connector import Error

# Mounting the drive
#from google.colab import drive
#drive.mount('/content/drive')

# Required Basic libraries
import html
import uuid
import pandas as pd
import os
import requests
#from PIL import Image ,ImageOps
import matplotlib.pyplot as plt
import numpy as np
#import cv2 as cv2
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
    page_content += ".customers th {  padding-top: 12px;  padding-bottom: 12px;  text-align: left;  color: blue;}</style>"
    page_content += """<body vLink="blue"><table class=customers >"""
    page_content += "<tr>"   
    page_content += """<th><a href=/verify target=_blank > WB Movie Mapping Verification </a></th>"""
    page_content += """<th><a href=/verify_tv target=_blank > WB TV Mapping Verification </a></th>"""
    page_content += """<th><a href=/summary target=_blank > WB Daily Summary </a></th>"""
    page_content += """<th><a href=/upcoming target=_blank > WB Daily Title Review </a></th>"""
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


def getColor(value):
    color = ""
    if value <= 25:
        color = "#ff0000"
    if value > 25 and value <= 75:
        color = "#ffb629"
    if value > 75:
        color = "#22b14c"
    return color
    
@app.route('/detail', methods=['GET', 'POST'])
def detail():
    portal_item_id = ""
    
    if request.method == 'GET':     
        portal_item_id = request.args.get('portal_item_id')
    
    try:
        connection = mysql.connector.connect(host='192.168.12.102',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')

        sql_select_Query = """  SELECT title Title,portal_item_id IMDB,region Country,VAs VonlyAssetIds, case when platform='Amazon Prime Video' then concat('<a href=https://amazon.com/dp/',product_id,' target=_blank>', product_id,'</a>')
        when platform='VUDU' then concat('<a href=https://www.vudu.com/content/movies/details/1917/',product_id,' target=_blank>', product_id,'</a>')  
        when platform='Google Play' then concat('<a href=https://play.google.com/store/movies/details/title?id=',product_id,' target=_blank>', product_id,'</a>')     
        when platform='AppleTVApp' then concat('<a href=https://tv.apple.com/us/movie/',product_id,' target=_blank>', product_id,'</a>')
        when platform='iTunes' then concat('<a href=https://itunes.apple.com/us/movie/id',product_id,' target=_blank>', product_id,'</a>')        else product_id end portal_item_id,platform Platform, 
                                        SUM(EST_Count) EST_Count, SUM(VOD_Count) VOD_Count,SUM(AVOD_Count) AVOD_Count, SUM(SVOD_Count) SVOD_Count,
                                        Studio,distributed_by, MIN(pre_est_date) PreOrder_EST_Date, MIN(pre_vod_date) PreOrder_VOD_Date, 
                                        MIN(est_date) Min_EST_Date, MIN(vod_date) Min_VOD_Date,MIN(avod_date) Min_AVOD_Date, MIN(svod_date) Min_SVOD_Date
                                        FROM
                                         (
                                        SELECT title,portal_item_id,region,VAs,platform,Studio,distributed_by, product_id,
                                        CASE WHEN product='EST' THEN record_count ELSE NULL END EST_Count, 
                                        CASE WHEN product='VOD' THEN record_count ELSE NULL END VOD_Count, 
                                        CASE WHEN product='AVOD' THEN record_count ELSE NULL END AVOD_Count, 
                                        CASE WHEN product='SVOD' THEN record_count ELSE NULL END SVOD_Count, 
                                        CASE WHEN is_preorder=1 AND product='EST' THEN search_date ELSE NULL END pre_est_date, 
                                        CASE WHEN is_preorder=1 AND product='VOD' THEN search_date ELSE NULL END pre_vod_date, 
                                        CASE WHEN is_preorder=0 AND product='EST' THEN search_date ELSE NULL END est_date,
                                         CASE WHEN is_preorder=0 AND product='VOD' THEN search_date ELSE NULL END vod_date,
                                         CASE WHEN is_preorder=0 AND product='AVOD' THEN search_date ELSE NULL END avod_date,
                                         CASE WHEN is_preorder=0 AND product='SVOD' THEN search_date ELSE NULL END svod_date 
                                        FROM
                                         (
                                        SELECT mi.title,ii.portal_item_id,mi.region, mi.vonly_asset_id VAs,mi.portal_item_id product_id 
                                        ,mp.product, mp.is_preorder, MIN(mp.search_date) search_date, COUNT(DISTINCT mp.search_date) record_count, mi.platform, m.distributed_by, m.distributed_by_parent Studio
                                        FROM movie_ids mi
                                        INNER JOIN sandbox.movies m ON mi.id=m.vonly_id AND mi.region=m.region
                                        LEFT OUTER
                                        JOIN movie_prices mp ON mi.id=mp.vonly_id
                                        LEFT OUTER
                                        JOIN imdb_ids ii ON ii.vonly_asset_id=mi.vonly_asset_id
                                        WHERE ii.portal_item_id ='%s' AND mi.portal IN  ('Amazon Prime Video','AppleTV_CanonicalId','Google Play','VUDU','iTunes')
                                        GROUP BY mi.vonly_asset_id, mp.product, mp.is_preorder,mi.platform,mi.portal_item_id
                                        ) A
                                        ) b
                                        GROUP BY VAs,region,platform,product_id order by 7 desc
                                 """  % (portal_item_id)
                                 
        print(sql_select_Query)
        
        # Set the pagination configuration
        page = request.args.get('page', 1, type=int)

        cursor = connection.cursor() 
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        
        print(dir(records))

        
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

    return render_template("detail.html",data=request.form.to_dict(), records=records)
    
@app.route('/summary', methods=['GET', 'POST'])
def summary():
    try:
        connection = mysql.connector.connect(host='192.168.12.102',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')

        sql_select_Query = """  SELECT * FROM (
                                SELECT Date(scan_date) `Date`, 'Upcoming Release' Report,
                                count(distinct case when `status`='No Action' then null ELSE ur.imdb_title_cd end) '# Issues',
                                 COUNT(DISTINCT ur.imdb_title_cd )  '# Titles',Resolution, `status` 
                                FROM pricm_data_from_wb_staging.upcoming_release ur
                                GROUP BY Date(scan_date),Resolution,`status` union
                                SELECT Date(scan_date) `Date`, 'Missing Client',
                                count(distinct case when `status`='No Action' then null ELSE mc.imdb_title_cd end) '# Issues',
                                COUNT(DISTINCT mc.imdb_title_cd) '# Titles',Resolution, `status`  
                                FROM pricm_data_from_wb_staging.missing_client mc
                                GROUP BY Date(scan_date),Resolution,`status` union
                                SELECT Date(scan_date) `Date`, 'Missing Title',
                                count(distinct case when `status`='No Action' then null ELSE mt.imdb_title_cd end) '# Issues',
                                COUNT(DISTINCT mt.imdb_title_cd) '# Titles',Resolution, `status` 
                                FROM pricm_data_from_wb_staging.missing_title mt
                                GROUP BY Date(scan_date),Resolution,`status` ) a
                                ORDER BY 1 desc,2;
                                 """  
        print(sql_select_Query)
        
        # Set the pagination configuration
        page = request.args.get('page', 1, type=int)

        cursor = connection.cursor() 
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        
        print(dir(records))

        
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

    return render_template("summary.html",data=request.form.to_dict(), records=records)


@app.route('/upcoming', methods=['GET', 'POST'])
def upcoming():
    # Render the page
    tablename = ""
    records =  ""
    ROWS_PER_PAGE = 5
    page_content = ""
    status = ""
    resolution = ""    
    title = ""
    remarks = ""   
    scan_date = ""
    where_tag = " where 1=1 "
    
    if request.method == 'POST':
        status = request.form['status'] 
        resolution = request.form['resolution'] 
        scan_date = request.form['scan_date']        
        title = request.form['title']
        remarks = request.form['remarks']
        tablename = request.form['tablename']
             
        if tablename == 'Missing Client':
            tablename='missing_client'
        if tablename == 'Missing Title':
            tablename='missing_title'
        if tablename == 'Upcoming Release':
            tablename='upcoming_release'
             
        if status != '' and status != 'All':
            where_tag = where_tag + " and ur.Status='" + status + "' "
        
        if resolution != '' and resolution != 'All':
            where_tag = where_tag + " and ur.Resolution='" + resolution + "' "
        
        if scan_date != '':
            where_tag = where_tag + " and ur.scan_date ='" + scan_date + "' "            
           
        if title != '':
            where_tag = where_tag + " and ur.title_description like '%" + title + "%' "

        if remarks != '':
            where_tag = where_tag + " and ur.Vonly_Remarks='" + remarks + "' "  
            
    else:
        where_tag = " and 1=0 "
        
    print(where_tag)
    
    try:
        connection = mysql.connector.connect(host='192.168.12.102',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')

        sql_select_Query = """ SELECT DISTINCT m.title,concat('<a href=/detail?portal_item_id=',ur.imdb_title_cd,' >', m.vonly_asset_id,'</a>'),
                 (SELECT GROUP_CONCAT(concat('<a href=https://itunes.apple.com/us/movie/id',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id) itunes_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://amazon.com/dp/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator ' ') FROM movie_ids mi WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id) amazon_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://www.vudu.com/content/movies/details/1917/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id) vudu_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://play.google.com/store/movies/details/title?id=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id) google_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://youtube.com/watch?v=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id) youtube_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://tv.apple.com/us/movie/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id AND mi.portal='AppleTV_CanonicalId') appletvapp_ids,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,') '))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_urls,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('(',mmi.distributed_by_parent,')<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id AND mi.portal='AppleTV_CanonicalId' ) appltvapp_urls, 
                            mpm.portal_item_id mpm_vvid,
                            concat('<a href=https://www.imdb.com/title/',(select portal_item_id from imdb_ids where vonly_asset_id=m.vonly_asset_id limit 1),' target=_blank>',(select portal_item_id from imdb_ids where vonly_asset_id=m.vonly_asset_id limit 1),'</a>'),
                            ur.imdb_title_cd,ur.title_description,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_dir,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,'] '))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_dir,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_dir,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_dir,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_dir,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('[',mmi.director,']<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id AND mi.portal='AppleTV_CanonicalId' ) appltvapp_dir,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,'<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_rd,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,' '))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_rd,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,'<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_rd,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,'<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_rd,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,'<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_rd,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('',mmi.us_theater_release_date,'<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id AND mi.portal='AppleTV_CanonicalId' ) appltvapp_rd,
                                                 (
                            SELECT GROUP_CONCAT(distinct CONCAT('{',mmi.runtime,'}<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_rt,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('{',mmi.runtime,'} '))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_rt,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('{',mmi.runtime,'}<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_rt,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('{',mmi.runtime,'}<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_rt,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('{',mmi.runtime,'}<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_rt,
                            (
                            SELECT GROUP_CONCAT(distinct CONCAT('{',mmi.runtime,'}<BR>'))
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id AND mi.portal='AppleTV_CanonicalId' ) appltvapp_rt
                            FROM pricm_data_from_wb_staging.%s ur
                            LEFT OUTER JOIN imdb_ids m ON ur.imdb_title_cd=m.portal_item_id
                            LEFT OUTER JOIN  movie_ids mpm on m.vonly_asset_id=mpm.vonly_asset_id and mpm.portal='wb mpm-vvid' %s order by 1 """  % (tablename,where_tag) 
               

        print(sql_select_Query)
        
        # Set the pagination configuration
        page = request.args.get('page', 1, type=int)

        cursor = connection.cursor() 
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        
        print(dir(records))

        
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

    return render_template("upcoming.html",data=request.form.to_dict(), records=records) 

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    # Render the page
    records =  ""
    ROWS_PER_PAGE = 5
    page_content = ""
    studio = "WB"
    release_year_start = 1900
    release_year_end = 2200
    title = ""
    va_id = ""
    where_tag = " and 1=1 "
    
    if request.method == 'POST':     
        studio = request.form['studio'] 
        release_year_start = request.form['release_year_start']
        release_year_end = request.form['release_year_end']
        title = request.form['title']
        va_id = request.form['va_id']
        
        print(studio)
        print(release_year_start)
        print(release_year_end)
        print(title)
        print(va_id)
       
        
        if studio != '' and studio != 'All':
            where_tag = where_tag + " and mm.distributed_by_parent='" + studio + "' "
        
        if release_year_start != '':
            where_tag = where_tag + " and year(mm.us_theater_release_date) >=" + release_year_start + " "
            
        if release_year_end != '':
            where_tag = where_tag + " and year(mm.us_theater_release_date) <=" + release_year_end + " "
            
        if title != '':
            where_tag = where_tag + " and m.title like '%" + title + "%' "

        if va_id != '':
            where_tag = where_tag + " and m.vonly_asset_id='" + va_id + "' "    
    else:
        where_tag = " and 1=0 "
   
        
 
    try:
        connection = mysql.connector.connect(host='192.168.12.102',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')

        sql_select_Query = """SELECT m.title ,m.vonly_asset_id,                                                                          
                            (SELECT GROUP_CONCAT(concat('<a href=https://itunes.apple.com/us/movie/id',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id) itunes_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://amazon.com/dp/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id) amazon_ids, 
                            (SELECT GROUP_CONCAT(concat('<a href=https://www.vudu.com/content/movies/details/1917/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id) vudu_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://play.google.com/store/movies/details/title?id=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id) google_ids, 
                            (SELECT GROUP_CONCAT(concat('<a href=https://youtube.com/watch?v=',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id) youtube_ids,
                            (SELECT GROUP_CONCAT(concat('<a href=https://tv.apple.com/us/movie/',mi.portal_item_id,' target=_blank>',mi.portal_item_id,'</a>') separator '<BR>') FROM movie_ids mi WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id AND mi.portal='AppleTV_CanonicalId') appletvapp_ids, 
                            (                                                                             
                            SELECT GROUP_CONCAT(CONCAT('<img src="',case when mmi.image_url is null then '' else mmi.image_url end ,'" height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='itunes' AND mi.vonly_asset_id=m.vonly_asset_id ) itunes_urls,
                            (                                                                             
                            SELECT GROUP_CONCAT(distinct CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='amazon prime video' AND mi.vonly_asset_id=m.vonly_asset_id ) amazon_urls, 
                            (                                                                             
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='vudu' AND mi.vonly_asset_id=m.vonly_asset_id ) vudu_urls,  
                            (                                                                             
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='google play' AND mi.vonly_asset_id=m.vonly_asset_id ) google_urls, 
                            (                                                                             
                            SELECT GROUP_CONCAT(CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 alt=''',mmi.portal_item_id,''' />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='youtube' AND mi.vonly_asset_id=m.vonly_asset_id ) youtube_urls,
                            (                                                                             
                            SELECT GROUP_CONCAT(distinct CONCAT('<img src=''',case when mmi.image_url is null then '' else mmi.image_url end,''' height=150 width=150 />(',mmi.distributed_by_parent,')<BR>')) 
                            FROM movie_ids mi INNER JOIN sandbox.movies mmi ON mi.id=mmi.vonly_id AND mi.region=mmi.region
                            WHERE mi.platform='appletvapp' AND mi.vonly_asset_id=m.vonly_asset_id ) appltvapp_urls, mpm.portal_item_id mpm_vvid,
                            concat('<a href=https://www.imdb.com/title/',(select portal_item_id from imdb_ids where vonly_asset_id=m.vonly_asset_id limit 1),' target=_blank>',(select portal_item_id from imdb_ids where vonly_asset_id=m.vonly_asset_id limit 1),'</a>'),
                            concat('<img src=''',(select image_url from sandbox.movies where vonly_asset_id=m.vonly_asset_id and platform='IMDB' limit 1 ),''' height=150 width=150 />')
                            FROM movie_ids m                                                              
                            INNER JOIN sandbox.movies mm ON m.id=mm.vonly_id AND m.region=mm.region
                            LEFT OUTER JOIN  movie_ids mpm on m.vonly_asset_id=mpm.vonly_asset_id and mpm.portal='wb mpm-vvid'
                            WHERE m.platform='itunes' %s ORDER BY 1 """ % (where_tag)
        
        

        print(sql_select_Query)
        
        # Set the pagination configuration
        page = request.args.get('page', 1, type=int)


        cursor = connection.cursor()        
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        print(dir(records))
        
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

    return render_template("records_all.html",data=request.form.to_dict(), records=records) 
    
@app.route('/verify_tv', methods=['GET', 'POST'])
def verify_tv():
    # Render the page
    records =  ""
    ROWS_PER_PAGE = 5
    page_content = ""
    studio = "WB"
    release_year_start = 1900
    release_year_end = 2200
    title = ""
    va_id = ""
    where_tag = " and 1=1 "
    
    if request.method == 'POST':     
        studio = request.form['studio'] 
        release_year_start = request.form['release_year_start']
        release_year_end = request.form['release_year_end']
        title = request.form['title']
        va_id = request.form['va_id']
        
        print(studio)
        print(release_year_start)
        print(release_year_end)
        print(title)
        print(va_id)
       
        
        if studio != '' and studio != 'All':
            where_tag = where_tag + " and ts_1.distributed_by_parent='" + studio + "' "
        
        if release_year_start != '':
            where_tag = where_tag + " and year(ts_1.us_theater_release_date) >=" + release_year_start + " "
            
        if release_year_end != '':
            where_tag = where_tag + " and year(ts_1.us_theater_release_date) <=" + release_year_end + " "
            
        if title != '':
            where_tag = where_tag + " and ti.title like '%" + title + "%' "

        if va_id != '':
            where_tag = where_tag + " and ti.vonly_asset_id='" + va_id + "' "    
    else:
        where_tag = " and 1=0 "
   
        
 
    try:
        connection = mysql.connector.connect(host='winv-ahd-003',
                                         database='vonly_data_feed_us_staging',
                                         user='vonly-agent',
                                         password='a714fded-311c-4215-8b8b-5df4086e264b')

        sql_select_Query = """  
    SELECT ti.title AS title,case when  ti.num IS NULL then '' ELSE ti.num END  AS num ,ti.vonly_asset_id,   
        (
	 		SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://amazon.com/gp/video/detail/',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
                separator '<BR>'
			)
		    FROM tv_ids ti_1 
            WHERE ti_1.platform = 'amazon prime video' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS amazon_ids,


        (
	 		SELECT GROUP_CONCAT(
		    	DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://www.vudu.com/content/browse/details/title/',ti_1.portal_item_id,'>',ti_1.portal_item_id, '</a>')
                SEPARATOR '<BR>'
            ) 
            FROM tv_ids ti_1 
            WHERE ti_1.platform = 'vudu' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS vudu_ids,


        (
              SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://tv.apple.com/us/season/season/',ti_1.portal_item_id,'?showId=', ti_show.portal_item_id,' >', ti_1.portal_item_id, '</a>') 
                SEPARATOR '<BR>'
            ) 
            FROM tv_ids ti_1
			INNER JOIN tv_id_mappings tim ON ti_1.id=tim.season_vonly_id 
			INNER JOIN tv_ids ti_show ON tim.show_vonly_id= ti_show.id
            WHERE ti_1.platform = 'appletvapp' AND ti_1.vonly_asset_id = ti.vonly_asset_id AND ti_1.portal = 'AppleTV_CanonicalId'

        ) AS appletvapp_ids,


        (
            SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://itunes.apple.com/us/tv-season/title/id',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
                separator '<BR>'
            ) 
            FROM tv_ids ti_1 
            WHERE ti_1.platform = 'itunes' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS itunes_ids,


        (
            SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://play.google.com/store/tv/show/?id=',tsi.portal_item_id,'&hl=en_US&gl=US&cdid=tvseason-',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
                separator '<BR>'
            ) 
                FROM tv_ids ti_1 
                INNER JOIN tv_id_mappings tim ON ti_1.id=tim.season_vonly_id
                INNER JOIN tv_ids tsi ON tim.show_vonly_id=tsi.id
                WHERE ti_1.platform = 'google play' AND ti_1.vonly_asset_id = ti.vonly_asset_id AND ti_1.portal = 'google play'
        ) AS google_ids, 
        
        
        (
            SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<img src=''',case when ts_1.image_url is null then '' else ts_1.image_url end,''' height=150 width=150 alt=''', ts_1.portal_item_id, ''' />(', ts_1.distributed_by_parent, ')<BR>')
            ) 
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'amazon prime video' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS amazon_urls, 


        (
            SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<img src=''', CASE WHEN ts_1.image_url IS NULL THEN '' ELSE ts_1.image_url END, ''' height=150 width=150 alt=''', ts_1.portal_item_id, ''' />(', ts_1.distributed_by_parent, ')<BR>')
            )
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'vudu' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS vudu_urls,


        (	                                                                                
            SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<img src=''', CASE WHEN ts_1.image_url IS NULL THEN '' ELSE ts_1.image_url END, ''' height=150 width=150 alt=''', ts_1.portal_item_id, ''' />(', ts_1.distributed_by_parent,')<BR>')
            ) 
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'appletvapp' AND ti_1.vonly_asset_id = ti.vonly_asset_id and ti_1.portal = 'AppleTV_CanonicalId'
        ) AS appltvapp_urls,


        (                                                                             
            SELECT GROUP_CONCAT(
               DISTINCT CONCAT('<img src="',case when ts_1.image_url is null then '' else ts_1.image_url end ,'" height=150 width=150 alt=''',ts_1.portal_item_id,''' />(',ts_1.distributed_by_parent,')<BR>')
            ) 
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'itunes' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS itunes_urls, 


        (
            SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<img src=''', CASE WHEN ts_1.image_url IS NULL THEN '' ELSE ts_1.image_url END, ''' height=150 width=150 alt=''', ts_1.portal_item_id, ''' />(', ts_1.distributed_by_parent,')<BR>')
            ) 
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'google play' AND ti_1.vonly_asset_id = ti.vonly_asset_id 
        ) AS google_urls,

        
        (
	 		SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<a target="_blank" rel="noopener" href=https://m.imdb.com/title/',im.portal_item_id,'>',im.portal_item_id,'</a>') 
                separator '<BR>'
			)
		    FROM sandbox.tv_imdb_ids im 
            WHERE im.vonly_asset_id = ti.vonly_asset_id
        ) AS imdb,


        (                                                                             
    	    SELECT GROUP_CONCAT(
	  			DISTINCT CONCAT('<img src=''',case when ts_1.image_url is null then '' else ts_1.image_url end,''' height=150 width=150 alt='')<BR>')
	        ) 
    		FROM sandbox.tvshows ts_1
			LEFT OUTER JOIN sandbox.tv_imdb_ids AS ii ON ts_1.vonly_asset_id=ii.vonly_asset_id
			WHERE ts_1.vonly_asset_id = ti.vonly_asset_id
        ) AS IMDB_urls 


    FROM tv_ids ti 
    LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti.id = ts_1.vonly_id AND ti.region = ts_1.region
    WHERE ti.scope = 'tv_season' AND ti.platform = 'vudu'  %s ORDER BY 1 LIMIT 10;  """ % (where_tag)
        
        

        print(sql_select_Query)
        
        # Set the pagination configuration
        page = request.args.get('page', 1, type=int)


        cursor = connection.cursor()        
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        print(dir(records))
        
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

    return render_template("records_tv.html",data=request.form.to_dict(), records=records) 
    
if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('192.168.100.222', 4449,debug=True)
