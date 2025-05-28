import os
import spotipy
from flask import session, current_app
from functools import wraps

def get_spotify_client():
    """Get an authenticated Spotify client from current user's session token"""
    if 'token_info' not in session:
        return None
        
    token_info = session.get('token_info')
    return spotipy.Spotify(auth=token_info['access_token'])