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

for i in range(len(result_list)):
    cur.execute("INSERT OR IGNORE INTO mutual_artists (name) VALUES (?)",(result_list[i],))

conn.commit()

cur.execute("SELECT name, COUNT(spotify_songs.artist_id) AS songs_in_spotify_top100 FROM spotify_artists JOIN spotify_songs ON artist_id = spotify_artists.id GROUP BY spotify_artists.id ORDER BY songs_in_spotify_top100 ASC;")
spotify_top_artists = cur.fetchall()
conn.commit()

cur.execute("SELECT name, COUNT(apple_music_songs.id) AS songs_in_apple_top100 FROM apple_music_artists JOIN apple_music_songs ON artist_id = apple_music_artists.id GROUP BY apple_music_artists.id ORDER BY songs_in_apple_top100 ASC;")
apple_top_artists = cur.fetchall()

conn.commit()

# spotify chart
results_s = dict(spotify_top_artists)

objects = results_s.keys()
y_pos = np.arange(len(objects))
performance = results_s.values()
plt.rc("ytick", labelsize = 6)
plt.barh(y_pos, performance, align='center', color = "red")
plt.yticks(y_pos, objects)
plt.xticks(np.arange(5))
plt.xlabel("Number of Songs in Spotify's Top 100 Songs of All Time")
plt.ylabel('Artists')
plt.tick_params(axis='y', labelsize=3)
plt.title("Spotify Top Artists")

plt.show()

# apple music chart
results_m = dict(apple_top_artists)

objects = results_m.keys()
y_pos = np.arange(len(objects))
performance = results_m.values()
plt.rc("ytick", labelsize = 6)
plt.barh(y_pos, performance, align='center', color = "red")
plt.yticks(y_pos, objects)
plt.xticks(np.arange(21))
plt.xlabel("Number of Songs in Apple's Top 100")
plt.ylabel('Artists')
plt.tick_params(axis='y', labelsize=3)
plt.title("Top Artists on Apple Music's Chart")

plt.show()

# plotting mutual data side by side
cur.execute("SELECT name, COUNT(mutual_artists.id) AS apple_mutual_artists FROM mutual_artists JOIN apple_music_songs ON artist_id = mutual_artists.id GROUP BY mutual_artists.id ORDER BY apple_mutual_artists ASC;")
mutual_songs_m = cur.fetchall()
dict_m = dict(mutual_songs_m)

cur.execute("SELECT name, COUNT(mutual_artists.id) AS spotify_mutual_artists FROM mutual_artists JOIN spotify_songs ON artist_id = mutual_artists.id GROUP BY mutual_artists.id ORDER BY spotify_mutual_artists ASC;")
mutual_songs_s = cur.fetchall()
dict_s = dict(mutual_songs_s)

# Define Data

# x_axis = np.arange(len(dict_m.keys()))
# apple = dict_m.keys()
# spotify = dict_s.keys()

# Multi bar Chart

# plt.bar(x_axis -0.2, dict_m.values(), width=0.4, label = 'Apple Music')
# plt.bar(x_axis +0.2, dict_s.values(), width=0.4, label = 'Spotify')


# plt.xticks(x_axis, dict_m.keys())
# plt.tick_params(axis='x', labelsize=5)
# plt.title("Artists in the Spotify overall Charts and Current Apple Charts")
# plt.xlabel("Artist Name")
# plt.ylabel("Number of Songs in Respective Top 100 Chart")
# plt.legend()
# plt.show()

# visualization for top artists x streams on spotify
cur.execute("SELECT mutual_artists.name, spotify_artists.streams FROM spotify_artists JOIN mutual_artists ON mutual_artists.name = spotify_artists.name;")
top_artists_streams = cur.fetchall()

dict_t = dict(top_artists_streams)
dict_top = dict(sorted(dict_t.items(), key = lambda x: x[1]))

names = list(dict_top.keys())
values = list(dict_top.values())
plt.ylabel('Artists')
plt.xlabel('Number of Streams on Top Streaming Song')
plt.bar(range(len(dict_top)), values, tick_label=names)
plt.tick_params(axis='x', labelsize=6)
plt.title("Top Artists Currently and Overall: Their Top Streamed Song")
plt.show()


#average songs artists have in the top overall charts, if they have songs in both 
# current top 100 (apple) and overall top 100 (spotify)
avg_songs_in_overall = sum(dict_s.values()) / len(dict_s.keys()) 
print(avg_songs_in_overall)

# average songs in current top charts for artists who have songs in both charts
avg_songs_in_current = sum(dict_m.values()) / len(dict_m.keys()) 
print(avg_songs_in_current)


