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
import matplotlib.pyplot as plt
import numpy as np

#this function retrieves data from the html file and stores 
#into lists

r = requests.get("https://en.wikipedia.org/wiki/List_of_most-streamed_songs_on_Spotify")
soup = BeautifulSoup(r.text, "html.parser")

# source_dir = os.path.dirname(__file__)
# full_path = os.path.join(source_dir, "Most-streamed.html")

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect('music.db')
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

cur.execute("CREATE TABLE IF NOT EXISTS spotify_songs (rank INTEGER PRIMARY KEY, song TEXT, streams NUMBER, artist_id INT, date TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS spotify_artists (id INTEGER PRIMARY KEY, name TEXT UNIQUE);")

songs_saved = 0
for i in range(len(song_list)):
    cur.execute("INSERT OR IGNORE INTO spotify_artists (name) VALUES (?)",(artist_list[i],))
    cur.execute("SELECT id FROM spotify_artists WHERE name = ?;", (artist_list[i],))
    artist_id = cur.fetchone()[0]
    cur.execute("SELECT * FROM spotify_songs WHERE song = ? AND artist_id = ?;", (song_list[i], artist_id))
    if not cur.fetchone():
        cur.execute("INSERT OR IGNORE INTO spotify_songs (rank, song, streams, artist_id, date) VALUES (?, ?, ?, ?, ?)",(rank_list[i], song_list[i], streams_list[i], artist_id, date_list[i]))
        songs_saved += 1
    if songs_saved >= 25:
        break

cur.execute("SELECT name, COUNT(spotify_songs.artist_id) AS songs_in_spotify_top100 FROM spotify_artists JOIN spotify_songs ON artist_id = spotify_artists.id GROUP BY spotify_artists.id ORDER BY songs_in_spotify_top100 ASC;")
spotify_top_artists = cur.fetchall()
conn.commit()
conn.close()

results = dict(spotify_top_artists)

objects = results.keys()
y_pos = np.arange(len(objects))
performance = results.values()
plt.rc("ytick", labelsize = 6)
plt.barh(y_pos, performance, align='center', color = "red")
plt.yticks(y_pos, objects)
plt.xticks(np.arange(5))
plt.xlabel("Number of Songs in Spotify's Top 100 Songs of All Time")
plt.ylabel('Artists')
plt.title("Spotify Top Artists")

plt.show()
