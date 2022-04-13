from urllib.request import urlopen
from xml.sax import parseString
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import sqlite3
import json
import unittest

#this function retrieves data from the html file and stores 
#into lists

r = requests.get("https://en.wikipedia.org/wiki/List_of_most-streamed_songs_on_Spotify")
soup = BeautifulSoup(r.text, "html.parser")

# source_dir = os.path.dirname(__file__)
# full_path = os.path.join(source_dir, "Most-streamed.html")

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+'songs.db')
cur = conn.cursor()

header = []
rank_list = []
song_list = []
streams_list = []
artist_list = []
date_list = []

tabl = soup.find("table", class_="wikitable sortable mw-collapsible")
for i in tabl.find_all('th')[:5]:
    header.append(i.text.strip())
for row in tabl.find_all('tr')[1:101]:
    rank_list.append(row.find('th').text.strip())
    items = row.findAll('td')
    #getting individual items from td's
    song_list.append(items[0].text.strip())
    streams_list.append(items[1].text.strip())
    artist_list.append(items[2].text.strip())
    date_list.append(items[3].text.strip())

cur.execute("CREATE TABLE IF NOT EXISTS Current_streams (rank INTEGER PRIMARY KEY, song TEXT, streams NUMBER, artist TEXT, date TEXT)")
for i in range(len(rank_list[0:25])):
    cur.execute("INSERT OR IGNORE INTO Current_streams (rank, song, streams, artist, date) VALUES (?, ?, ?, ?, ?)",(rank_list[i], song_list[i], streams_list[i], artist_list[i], date_list[i]))

cur.execute(
    '''
    SELECT * FROM Current_streams
    '''
)
current_row = cur.fetchall()[-1][0]


for i in range(current_row,current_row+25):
    cur.execute("INSERT OR IGNORE INTO Current_streams (rank, song, streams, artist, date) VALUES (?, ?, ?, ?, ?)",(rank_list[i], song_list[i], streams_list[i], artist_list[i], date_list[i]))

cur.execute(
    '''
    SELECT * FROM Current_streams
    '''
)
current_row = cur.fetchall()[-1][0]


for i in range(current_row,current_row+25):
    cur.execute("INSERT OR IGNORE INTO Current_streams (rank, song, streams, artist, date) VALUES (?, ?, ?, ?, ?)",(rank_list[i], song_list[i], streams_list[i], artist_list[i], date_list[i]))

cur.execute(
    '''
    SELECT * FROM Current_streams
    '''
)
current_row = cur.fetchall()[-1][0]


for i in range(current_row,current_row+25):
    cur.execute("INSERT OR IGNORE INTO Current_streams (rank, song, streams, artist, date) VALUES (?, ?, ?, ?, ?)",(rank_list[i], song_list[i], streams_list[i], artist_list[i], date_list[i]))
conn.commit()







