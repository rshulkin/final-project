import sqlite3
import requests
import json
import jwt
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
url = "https://api.music.apple.com/v1/catalog/US/charts"
key_id = "688Z3NH7KW"
team_id = "A243U6Q6LD"
secret_key = open("AuthKey_688Z3NH7KW.p8").read()
token_str = None
token_valid_until = None

def generate_token(session_length=12):
    """
    Takes the length of time for the token to be valid for (in hours) as the input and uses this encrypted token to assist with the successful api request.
    """
    global token_str, token_valid_until
    token_exp_time = datetime.now() + timedelta(hours=session_length)
    headers = {
        'alg': "ES256",
        'kid': key_id,
    }
    payload = {
        'iss': team_id,  # issuer
        'iat': int(datetime.now().timestamp()),  # issued at
        'exp': int(token_exp_time.timestamp())  # expiration time
    }
    token_valid_until = token_exp_time
    token = jwt.encode(payload, secret_key, algorithm="ES256", headers=headers)
    token_str = token if type(token) is not bytes else token.decode()
    open("token.str", "w").write(token_str)
    open("token.exp", "w").write(str(token_valid_until.timestamp()))



if "token.str" in os.listdir():
    token_valid_until = datetime.fromtimestamp(float(open("token.exp").read()))

if token_valid_until is None or datetime.now() >= token_valid_until:
    generate_token()
else:
    token_str = open("token.str").read()

# print(token_str)

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token_str}"}
max_songs = 100
response = requests.get(url, headers=headers, params={"types": "songs", "chart": "most-played", "limit": max_songs})
print(response.json())

# using i as an iterating index
# response.json()["results"]["songs"][0]["data"][i]["attributes"]["name"]
# response.json()["results"]["songs"][0]["data"][i]["attributes"]["artistName"]

con = sqlite3.connect("music.db")
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS apple_music_songs 
               (id INTEGER PRIMARY KEY, rank INT, song TEXT, artist_id INT);''')
cur.execute('''CREATE TABLE IF NOT EXISTS apple_music_artists
               (id INTEGER PRIMARY KEY, name TEXT UNIQUE);''')
songs_saved = 0 
for i in range(max_songs):
    song_name = response.json()["results"]["songs"][0]["data"][i]["attributes"]["name"]
    artist_name = response.json()["results"]["songs"][0]["data"][i]["attributes"]["artistName"] 
    cur.execute("INSERT OR IGNORE INTO apple_music_artists (name) VALUES (?);", (artist_name,))
    cur.execute("SELECT id FROM apple_music_artists WHERE name = ?;", (artist_name,))
    artist_id = cur.fetchone()[0]
    cur.execute("SELECT * FROM apple_music_songs WHERE song = ?;", (song_name,))
    if not cur.fetchone():
        cur.execute("INSERT INTO apple_music_songs (rank, song, artist_id) VALUES (?, ?, ?);", (i+1, song_name, artist_id))
        songs_saved += 1
    if songs_saved >= 25:
        break

con.commit()
con.close()
