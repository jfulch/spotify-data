import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import time
from flask import Flask, session, request, redirect, render_template, url_for, jsonify

# Import your analysis modules
from spotify_analysis.artist_analysis import get_top_artists, analyze_genre_distribution
from spotify_analysis.track_analysis import get_top_tracks, analyze_recent_plays
from spotify_analysis.mood_analysis import analyze_music_mood
from spotify_analysis.obscurity_score import calculate_obscurity_score

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

# Spotify scopes
SCOPE = "user-read-private user-read-email user-top-read user-read-recently-played playlist-read-private user-follow-read"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    # Create Spotify OAuth instance
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Create a new SpotifyOAuth instance
    sp_oauth = create_spotify_oauth()
    
    # Get auth token from Spotify
    token_info = sp_oauth.get_access_token(request.args.get('code'))
    
    # Store in user's session
    session['token_info'] = token_info
    
    return redirect(url_for('dashboard'))

def get_spotify_client():
    """Get a spotify client for the current user's session"""
    if 'token_info' not in session:
        return redirect(url_for('login'))
        
    token_info = session.get('token_info', {})
    
    # Check if token needs refresh
    if is_token_expired(token_info):
        # Create oauth and use it to refresh the token
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
        
    # Create a NEW client for THIS user with THEIR token
    return spotipy.Spotify(auth=token_info['access_token'])

@app.route('/dashboard')
def dashboard():
    """Redirect to the basics page"""
    if not is_authenticated():
        return redirect(url_for('login'))
        
    return redirect(url_for('basics'))

@app.route('/basics')
def basics():
    """Display the basics page with top artists, tracks, genres"""
    if not is_authenticated():
        return redirect(url_for('login'))
        
    # Get Spotify client
    sp = get_spotify_client()
    
    # Get user info
    user_info = sp.current_user()
    
    # Get top artists for different time ranges
    top_artists_short = get_top_artists(sp, time_range='short_term')
    top_artists_medium = get_top_artists(sp, time_range='medium_term')
    top_artists_long = get_top_artists(sp, time_range='long_term')
    
    # Get top tracks
    top_tracks_short = get_top_tracks(sp, time_range='short_term')
    top_tracks_medium = get_top_tracks(sp, time_range='medium_term')
    top_tracks_long = get_top_tracks(sp, time_range='long_term')
    
    # Genre analysis for all time periods
    top_genres_short = analyze_genre_distribution(top_artists_short)
    top_genres_medium = analyze_genre_distribution(top_artists_medium)
    top_genres_long = analyze_genre_distribution(top_artists_long)
    
    # Recent plays
    recent = analyze_recent_plays(sp)
    
    return render_template('basics.html',
                          active_page='basics',
                          user_info=user_info,
                          top_artists_short=top_artists_short,
                          top_artists_medium=top_artists_medium,
                          top_artists_long=top_artists_long,
                          top_tracks_short=top_tracks_short,
                          top_tracks_medium=top_tracks_medium,
                          top_tracks_long=top_tracks_long,
                          top_genres_short=top_genres_short,
                          top_genres_medium=top_genres_medium,
                          top_genres_long=top_genres_long,
                          recent=recent)

@app.route('/music-dna')
def music_dna():
    """Display the Music DNA page with audio features, mood, uniqueness"""
    if not is_authenticated():
        return redirect(url_for('login'))
        
    # Get Spotify client
    sp = get_spotify_client()
    
    # Get user info
    user_info = sp.current_user()
    
    # Music mood analysis
    mood = analyze_music_mood(sp)
    
    # Recent data for listening schedule
    recent = analyze_recent_plays(sp)
    
    # Calculate obscurity score
    obscurity_score = calculate_obscurity_score(sp)
    
    return render_template('music_dna.html',
                          active_page='music_dna',
                          user_info=user_info,
                          mood=mood,
                          recent=recent,
                          obscurity_score=obscurity_score)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )

@app.route('/artist-search')
def artist_search():
    """Display the artist search page"""
    if not is_authenticated():
        return redirect(url_for('login'))
        
    return render_template('artist_search.html', active_page='artist_search', user_info=get_spotify_client().current_user())

@app.route('/api/search-artist')
def search_artist():
    """API endpoint to search for artists"""
    if not is_authenticated():
        return {"error": "Not authenticated"}, 401
        
    query = request.args.get('query', '')
    if not query:
        return {"error": "No search query provided"}, 400
    
    try:
        sp = get_spotify_client()
        results = sp.search(q=query, type='artist', limit=10)
        return jsonify(results)
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/api/artist/<artist_id>')
def get_artist_details(artist_id):
    """API endpoint to get detailed information about an artist"""
    if not is_authenticated():
        return {"error": "Not authenticated"}, 401
    
    try:
        sp = get_spotify_client()
        # Get artist details
        artist = sp.artist(artist_id)
        
        # Get artist's top tracks
        top_tracks = sp.artist_top_tracks(artist_id)
        
        # Get artist's albums
        albums = sp.artist_albums(artist_id, album_type='album', limit=5)
                
        return jsonify({
            "artist": artist,
            "top_tracks": top_tracks,
            "albums": albums
            # Remove related_artists from the response entirely
        })
    except Exception as e:
        return {"error": str(e)}, 500

def is_authenticated():
    """Check if the user is logged in with a valid token"""
    return 'token_info' in session

def is_token_expired(token_info):
    """Check if the token is expired"""
    if not token_info:
        return True
    
    now = int(time.time())
    return token_info['expires_at'] - now < 60

if __name__ == '__main__':
    environment = os.environ.get('FLASK_ENV', 'production')
    
    if environment == 'development':
        # Local development with SSL
        app.run(
            debug=True, 
            host='127.0.0.1',
            port=8888,
            ssl_context=('/Users/jfulch/.ssl/cert.pem', '/Users/jfulch/.ssl/key.pem')
        )
    else:
        # Production/deployment settings
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)