import json
import requests
import re
import urllib.request
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3
import csv
from lxml import etree

import os
import re
import requests
from datetime import datetime


# url = 'https://api.pluto.tv/v3/vod/series/653b35c0619680001a413d3e/seasons?deviceType=web'


# # Make a GET request to the URL
# response = requests.get(url)
# data = response.json()
# print(data)


url = 'https://api.pluto.tv/v3/vod/series/653b35c0619680001a413d3e/seasons?deviceType=web'

response = requests.get(url)
data = response.json()






print(data)  
