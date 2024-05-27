import os
from dotenv import load_dotenv
import spotipy
import sqlite3
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

# Load credentials from spotify.env file
load_dotenv(dotenv_path='spotify.env')
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Authenticate with Spotify API
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-top-read user-read-recently-played")
sp = spotipy.Spotify(auth_manager=sp_oauth)

# Connect to sqlite3 database
conn = sqlite3.connect('spotify_data.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS top_tracks (
    id TEXT PRIMARY KEY,
    name TEXT,
    artist TEXT,
    album TEXT,
    release_date TEXT,
    popularity INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS top_genres (
    genre TEXT PRIMARY KEY,
    count INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS listening_history (
    played_at TEXT,
    track_id TEXT,
    track_name TEXT,
    artist_name TEXT,
    PRIMARY KEY (played_at, track_id)
)
''')

# Fetch top tracks
def get_top_tracks():
    results = sp.current_user_top_tracks(time_range='medium_term', limit=50)
    tracks = []
    for idx, track in enumerate(results['items']):
        track_info = {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'popularity': track['popularity']
        }
        tracks.append(track_info)
        print(f"{idx+1}. {track['name']} by {track['artists'][0]['name']}")
    
    return pd.DataFrame(tracks)

# Fetch top genres
def get_top_genres():
    results = sp.current_user_top_artists(limit=50)
    genres = []
    for artist in results['items']:
        genres.extend(artist['genres'])
    genre_counts = pd.Series(genres).value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']
    return genre_counts

# Fetch listening history
def get_listening_history():
    results = sp.current_user_recently_played(limit=50)
    history = []
    for item in results['items']:
        track_info = {
            'played_at': item['played_at'],
            'track_id': item['track']['id'],
            'track_name': item['track']['name'],
            'artist_name': item['track']['artists'][0]['name']
        }
        history.append(track_info)
    return pd.DataFrame(history)

# Fetch data and save to database
top_tracks_df = get_top_tracks()
top_genres_df = get_top_genres()
listening_history_df = get_listening_history()

top_tracks_df.to_sql('top_tracks', conn, if_exists='replace', index=False)
top_genres_df.to_sql('top_genres', conn, if_exists='replace', index=False)
listening_history_df.to_sql('listening_history', conn, if_exists='replace', index=False)

conn.commit()
conn.close()

