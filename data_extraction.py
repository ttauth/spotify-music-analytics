import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load credentials from .env file
load_dotenv(dotenv_path='spotify.env') 
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
# Authenticate with Spotify API
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-top-read")

# Get access token
token_info = sp_oauth.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=token_info)


# Example function to get top tracks
def get_top_tracks():
    results = sp.current_user_top_tracks(time_range='medium_term', limit=10)
    for idx, track in enumerate(results['items']):
        print(f"{idx+1}. {track['name']} by {track['artists'][0]['name']}")

# Fetch top tracks
get_top_tracks()
