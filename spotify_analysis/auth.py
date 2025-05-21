# auth.py
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_spotify_client():
    """Create and return an authenticated Spotify client"""
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', "https://localhost:8888/callback")
    
    scope = "user-top-read user-read-recently-played playlist-read-private"
    
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=".spotify_token_cache",
        open_browser=True
    )
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp