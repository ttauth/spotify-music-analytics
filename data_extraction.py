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
    name TEXT,
    artist TEXT,
    album TEXT,
    release_date TEXT,
    popularity_score INTEGER
)
''')
print("Table 'top_tracks' created or already exists.")

cursor.execute('''
CREATE TABLE IF NOT EXISTS top_genres (
    genre TEXT,
    occurrences INTEGER
)
''')
print("Table 'top_genres' created or already exists.")

cursor.execute('''
CREATE TABLE IF NOT EXISTS listening_history (
    track_name TEXT,
    artist_name TEXT,
    played_duration_ms INTEGER,
    play_count INTEGER
)
''')
print("Table 'listening_history' created or already exists.")

# Fetch top tracks
def get_top_tracks():
    results = sp.current_user_top_tracks(time_range='medium_term', limit=20)
    tracks = []
    for track in results['items']:
        track_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'popularity_score': track['popularity']
        }
        tracks.append(track_info)
        print(f"{track['name']} by {track['artists'][0]['name']}")
    
    return pd.DataFrame(tracks)

# Fetch top genres
def get_top_genres():
    results = sp.current_user_top_artists(limit=10)
    genres = []
    for artist in results['items']:
        genres.extend(artist['genres'])
    genre_counts = pd.Series(genres).value_counts().reset_index()
    genre_counts.columns = ['genre', 'occurrences']  # 'occurrences' represents the number of times each genre appears among the top artists
    return genre_counts

# Fetch listening history
def get_listening_history():
    results = sp.current_user_recently_played(limit=50)
    history = {}
    for item in results['items']:
        track_name = item['track']['name']
        if track_name not in history:
            history[track_name] = {
                'track_name': track_name,
                'artist_name': item['track']['artists'][0]['name'],
                'played_duration_ms': item['track']['duration_ms'],
                'play_count': 1
            }
        else:
            history[track_name]['play_count'] += 1
            history[track_name]['played_duration_ms'] += item['track']['duration_ms']
    
    history_df = pd.DataFrame(history.values())
    return history_df

# Fetch data and save to database
top_tracks_df = get_top_tracks()
top_genres_df = get_top_genres()
listening_history_df = get_listening_history()

print("Saving top tracks to database...")
top_tracks_df.to_sql('top_tracks', conn, if_exists='replace', index=False)
print("Saving top genres to database...")
top_genres_df.to_sql('top_genres', conn, if_exists='replace', index=False)
print("Saving listening history to database...")
listening_history_df.to_sql('listening_history', conn, if_exists='replace', index=False)

print("Data saved to database successfully.")

# Verify the tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables in the database:", cursor.fetchall())

conn.commit()
conn.close()
