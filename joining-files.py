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

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect("music.db")
cur = conn.cursor()

cur.execute(
    '''
    SELECT apple_music_artists.name
        FROM apple_music_artists JOIN spotify_artists ON spotify_artists.name = apple_music_artists.name
        
    '''
)
res = cur.fetchall()


cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS mutual_artists 
        (id INTEGER PRIMARY KEY, name TEXT UNIQUE);
    '''
    )
result_list = [x[0] for x in res]
# for i in range(len(result_list)):
#     cur.execute(
#     '''
#     INSERT OR IGNORE INTO mutual_artists (name) VALUES (?);
    
#     ''',
#     (result_list[i],)
# )

for i in range(len(result_list)):
    cur.execute("INSERT OR IGNORE INTO mutual_artists (name) VALUES (?)",(result_list[i],))

conn.commit()

