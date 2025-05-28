import os
import sys
import time
import logging
from flask import Flask, session, request, redirect, render_template, url_for, jsonify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from dotenv import load_dotenv
import spotipy

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if present
load_dotenv()

# Import analysis modules
try:
    from spotify_analysis.artist_analysis import get_top_artists, analyze_genre_distribution
    from spotify_analysis.track_analysis import get_top_tracks, analyze_recent_plays
    from spotify_analysis.mood_analysis import analyze_music_mood
    from spotify_analysis.obscurity_score import calculate_obscurity_score
    logger.info("Successfully imported spotify_analysis modules")
except Exception as e:
    logger.error(f"ERROR IMPORTING MODULES: {e}")
    def get_top_artists(*args, **kwargs): return {"error": "Module import failed"}
    def analyze_genre_distribution(*args, **kwargs): return {"error": "Module import failed"}
    def get_top_tracks(*args, **kwargs): return {"error": "Module import failed"}
    def analyze_recent_plays(*args, **kwargs): return {"error": "Module import failed"}
    def analyze_music_mood(*args, **kwargs): return {"error": "Module import failed"}
    def calculate_obscurity_score(*args, **kwargs): return {"error": "Module import failed"}

# Spotify API scopes - all the permissions we need
SCOPE = "user-read-private user-read-email user-top-read user-read-recently-played playlist-read-private"

# Initialize Flask app
app = Flask(__name__)

# Set up session with stable secret key from environment variable
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    logger.warning("WARNING: Using random secret key - sessions will be invalidated on restart")
    app.secret_key = os.urandom(24)

# Configure session
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

def create_spotify_oauth():
    """Create and configure a SpotifyOAuth object"""
    try:
        client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.environ.get('SPOTIFY_REDIRECT_URI')
        
        logger.info(f"Creating OAuth with redirect URI: {redirect_uri}")
        
        # Don't use cache_path - rely only on session storage
        return SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SCOPE,
            cache_path=None  # Don't use file caching
        )
    except Exception as e:
        logger.error(f"ERROR CREATING OAUTH: {e}")
        raise

def get_token():
    """Get and validate the token from the session, refreshing if needed"""
    try:
        token_info = session.get('token_info', None)
        
        if not token_info:
            logger.info("No token found in session")
            return None

        now = int(time.time())
        is_expired = token_info['expires_at'] - now < 60
        
        if is_expired:
            logger.info("Token is expired, refreshing...")
            sp_oauth = create_spotify_oauth()
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
            
        return token_info
    except Exception as e:
        logger.error(f"ERROR IN get_token: {e}")
        session.clear()  # Clear invalid session
        return None

def get_spotify_client():
    """Get an authenticated Spotify client using the current user's token"""
    try:
        token_info = get_token()
        if not token_info:
            logger.info("No valid token available")
            return None
            
        # Create a fresh client with the current token
        client = spotipy.Spotify(auth=token_info['access_token'])
        
        # Test the client with a basic API call
        try:
            user = client.me()
            logger.info(f"Authenticated as: {user.get('display_name')} ({user.get('id')})")
            return client
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            session.clear()
            return None
            
    except Exception as e:
        logger.error(f"ERROR creating Spotify client: {e}")
        return None

def is_authenticated():
    """Check if the user is authenticated"""
    try:
        return 'token_info' in session and get_token() is not None
    except Exception as e:
        logger.error(f"Error checking authentication: {e}")
        return False

# Routes
@app.route('/')
def index():
    """Landing page - shows login button or redirects to dashboard"""
    logger.info("Route / accessed")
    if not is_authenticated():
        return render_template('login.html')
    return redirect(url_for('dashboard'))

@app.route('/login')
def login():
    """Initialize Spotify OAuth flow"""
    logger.info("Login route accessed")
    try:
        sp_oauth = create_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        logger.info(f"Generated auth URL: {auth_url}")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return render_template('error.html', error=str(e))

@app.route('/callback')
def callback():
    """Handle the OAuth callback from Spotify"""
    logger.info("Callback route accessed")
    try:
        sp_oauth = create_spotify_oauth()
        session.clear()
        code = request.args.get('code')
        
        # If there's an error parameter in the callback, handle it
        if 'error' in request.args:
            error = request.args.get('error')
            logger.error(f"Spotify auth error: {error}")
            return render_template('error.html', 
                error=f"Spotify authorization failed: {error}",
                show_login=True)
        
        try:
            # Force a new token request (don't use cache)
            token_info = sp_oauth.get_access_token(code, check_cache=False)
            session['token_info'] = token_info
            
            # Test the token immediately
            sp = spotipy.Spotify(auth=token_info['access_token'])
            user = sp.me()  # Test API call
            logger.info(f"User authenticated: {user.get('id')} - {user.get('display_name')}")
            
            return redirect(url_for('dashboard'))
            
        except spotipy.oauth2.SpotifyOauthError as oauth_error:
            logger.error(f"OAuth error: {oauth_error}")
            return render_template('error.html', 
                error="Authentication failed. Please try logging in again.",
                show_login=True)
            
    except Exception as e:
        logger.error(f"Error during callback: {e}")
        return render_template('error.html', 
            error=str(e),
            show_login=True)
            
    except Exception as e:
        logger.error(f"Error during callback: {e}")
        return render_template('error.html', error=str(e))

@app.route('/logout')
def logout():
    """Clear the user session"""
    logger.info("Logout route accessed")
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard page showing user's Spotify stats"""
    logger.info("Dashboard route accessed")
    if not is_authenticated():
        logger.info("Not authenticated, redirecting to index")
        return redirect(url_for('index'))
        
    try:
        sp = get_spotify_client()
        if not sp:
            logger.warning("Failed to get Spotify client, redirecting to login")
            return redirect(url_for('login'))
            
        user_info = sp.me()
        logger.info(f"Showing dashboard for: {user_info.get('display_name')}")
        
        # Get top artists
        top_artists_short = get_top_artists(sp, 'short_term')
        top_artists_medium = get_top_artists(sp, 'medium_term')
        top_artists_long = get_top_artists(sp, 'long_term')
        
        # Get top tracks
        top_tracks_short = get_top_tracks(sp, 'short_term')
        top_tracks_medium = get_top_tracks(sp, 'medium_term')
        top_tracks_long = get_top_tracks(sp, 'long_term')
        
        # Get recent plays and mood analysis
        recent = analyze_recent_plays(sp)
        mood = analyze_music_mood(sp)
        
        # Genre distribution
        genre_data = analyze_genre_distribution(sp)
        
        # Calculate obscurity score (THIS WAS MISSING)
        from spotify_analysis.obscurity_score import calculate_obscurity_score
        obscurity_score = calculate_obscurity_score(sp)
        
        return render_template(
            'dashboard.html',
            user_info=user_info,
            top_artists_short=top_artists_short,
            top_artists_medium=top_artists_medium,
            top_artists_long=top_artists_long,
            top_tracks_short=top_tracks_short,
            top_tracks_medium=top_tracks_medium,
            top_tracks_long=top_tracks_long,
            recent=recent,
            mood=mood,
            genre_data=genre_data,
            obscurity_score=obscurity_score,  # ADD THIS LINE
            active_page='dashboard'
        )
    except Exception as e:
        logger.error(f"Error in dashboard route: {e}", exc_info=True)
        return render_template('error.html', error=str(e))

@app.route('/basics')
def basics():
    """Show basic stats about the user's listening habits"""
    logger.info("Basics route accessed")
    if not is_authenticated():
        logger.info("Not authenticated, redirecting to login")
        return redirect(url_for('login'))
        
    try:
        sp = get_spotify_client()
        if not sp:
            logger.warning("Failed to get Spotify client, redirecting to login")
            return redirect(url_for('login'))
            
        # Get user info and top items
        user_info = sp.me()
        
        # Get top artists for different time ranges
        top_artists_short = get_top_artists(sp, 'short_term')
        top_artists_medium = get_top_artists(sp, 'medium_term')
        top_artists_long = get_top_artists(sp, 'long_term')
        
        # Get top tracks for different time ranges
        top_tracks_short = get_top_tracks(sp, 'short_term')
        top_tracks_medium = get_top_tracks(sp, 'medium_term')
        top_tracks_long = get_top_tracks(sp, 'long_term')
        
        # Get other data
        genre_data = analyze_genre_distribution(sp)
        recent = analyze_recent_plays(sp)
        mood = analyze_music_mood(sp)
        obscurity = calculate_obscurity_score(sp)
        
        return render_template(
            'basics.html',
            user_info=user_info,
            # Artists
            top_artists_short=top_artists_short,
            top_artists_medium=top_artists_medium,
            top_artists_long=top_artists_long,
            top_artists=top_artists_medium,  # For backward compatibility
            # Tracks
            top_tracks_short=top_tracks_short,
            top_tracks_medium=top_tracks_medium,
            top_tracks_long=top_tracks_long,
            top_tracks=top_tracks_medium,  # For backward compatibility
            # Other data
            genre_data=genre_data,
            recent=recent,
            mood=mood,
            obscurity=obscurity,
            active_page='basics'
        )
    except Exception as e:
        logger.error(f"Error in basics route: {e}", exc_info=True)
        return render_template('error.html', error=str(e))

@app.route('/music_dna')
def music_dna():
    """Show detailed analysis of the user's musical taste"""
    logger.info("Music DNA route accessed")
    if not is_authenticated():
        logger.info("Not authenticated, redirecting to login")
        return redirect(url_for('login'))
        
    try:
        sp = get_spotify_client()
        if not sp:
            logger.warning("Failed to get Spotify client, redirecting to login")
            return redirect(url_for('login'))
            
        user_info = sp.me()
        
        # Analysis data - ADD RECENT PLAYS
        mood = analyze_music_mood(sp)
        genre_data = analyze_genre_distribution(sp)
        recent = analyze_recent_plays(sp)  # ADD THIS LINE
        
        return render_template(
            'music_dna.html',
            user_info=user_info,
            mood=mood,
            genre_data=genre_data,
            recent=recent,  # ADD THIS LINE
            active_page='music_dna'
        )
    except Exception as e:
        logger.error(f"Error in music_dna route: {e}", exc_info=True)
        return render_template('error.html', error=str(e))

@app.route('/artist_search')
def artist_search():
    """Artist search page"""
    logger.info("Artist search route accessed")
    if not is_authenticated():
        logger.info("Not authenticated, redirecting to login")
        return redirect(url_for('login'))
        
    try:
        sp = get_spotify_client()
        if not sp:
            logger.warning("Failed to get Spotify client, redirecting to login")
            return redirect(url_for('login'))
            
        user_info = sp.me()
        
        return render_template(
            'artist_search.html',
            user_info=user_info,
            active_page='artist_search'
        )
    except Exception as e:
        logger.error(f"Error in artist_search route: {e}", exc_info=True)
        return render_template('error.html', error=str(e))

# API endpoints
@app.route('/api/search-artist')
def search_artist():
    """API endpoint to search for artists"""
    logger.info(f"Search artist API accessed with query: {request.args.get('query')}")
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        sp = get_spotify_client()
        query = request.args.get('query', '')
        
        if not query:
            return jsonify({"error": "No search query provided"}), 400
            
        results = sp.search(q=query, type='artist', limit=5)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in search_artist: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/artist/<artist_id>')
def get_artist_details(artist_id):
    """API endpoint to get artist details"""
    logger.info(f"Artist details API accessed for ID: {artist_id}")
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
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
        })
    except Exception as e:
        logger.error(f"Error in get_artist_details: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Simple endpoint to verify app is running"""
    env_status = {
        "spotify_client_id": bool(os.environ.get('SPOTIFY_CLIENT_ID')),
        "spotify_client_secret": bool(os.environ.get('SPOTIFY_CLIENT_SECRET')),
        "spotify_redirect_uri": os.environ.get('SPOTIFY_REDIRECT_URI'),
        "secret_key": bool(os.environ.get('SECRET_KEY')),
    }
    return jsonify({
        "status": "healthy",
        "environment_variables": env_status,
        "authenticated": is_authenticated()
    })

@app.route('/debug-user')
def debug_user():
    """Debug endpoint to check current user"""
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        sp = get_spotify_client()
        user_info = sp.me()
        return jsonify({
            "user_id": user_info.get('id'),
            "display_name": user_info.get('display_name'),
            "email": user_info.get('email')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error=str(e)), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return render_template('error.html', error=str(e)), 500

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
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)