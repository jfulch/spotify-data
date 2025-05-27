print("=============== APPLICATION STARTING ===============")
import sys
import os
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
try:
    print(f"Directory contents: {os.listdir('.')}")
except Exception as e:
    print(f"Could not list directory: {e}")

print("--- Environment Variables ---")
required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI', 'SECRET_KEY']
for var in required_vars:
    value = os.environ.get(var)
    print(f"{var}: {'✓ Set' if value else '✗ MISSING'}")

try:
    # Standard imports
    import time
    from flask import Flask, session, request, redirect, render_template, url_for, jsonify
    from spotipy.oauth2 import SpotifyOAuth
    from dotenv import load_dotenv
    import spotipy
    print("Basic imports successful")
    
    # Try to import analysis modules with error handling
    try:
        from spotify_analysis.artist_analysis import get_top_artists, analyze_genre_distribution
        from spotify_analysis.track_analysis import get_top_tracks, analyze_recent_plays
        from spotify_analysis.mood_analysis import analyze_music_mood
        from spotify_analysis.obscurity_score import calculate_obscurity_score
        print("Successfully imported spotify_analysis modules")
    except Exception as e:
        print(f"ERROR IMPORTING MODULES: {e}")
        # Define fallback functions to prevent app from crashing
        def get_top_artists(*args, **kwargs): return {"error": "Module import failed"}
        def analyze_genre_distribution(*args, **kwargs): return {"error": "Module import failed"}
        def get_top_tracks(*args, **kwargs): return {"error": "Module import failed"}
        def analyze_recent_plays(*args, **kwargs): return {"error": "Module import failed"}
        def analyze_music_mood(*args, **kwargs): return {"error": "Module import failed"}
        def calculate_obscurity_score(*args, **kwargs): return {"error": "Module import failed"}
except Exception as e:
    print(f"CRITICAL ERROR DURING IMPORTS: {e}")
    import traceback
    traceback.print_exc()

# Load environment variables
load_dotenv()

# Spotify API scopes
SCOPE = "user-read-private user-read-email user-top-read user-read-recently-played playlist-read-private"

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Remove filesystem session type - it causes issues on Railway
# app.config['SESSION_TYPE'] = 'filesystem'

app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
app.debug = True  # Enable debug mode for more verbose errors

print("Flask app initialized with config:", app.config)

# Utility functions
def create_spotify_oauth():
    try:
        client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.environ.get('SPOTIFY_REDIRECT_URI')
        
        print(f"OAuth config: ID length={len(client_id) if client_id else 0}, "
              f"Secret length={len(client_secret) if client_secret else 0}, "
              f"Redirect={redirect_uri}")
        
        return SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SCOPE
        )
    except Exception as e:
        print(f"ERROR CREATING OAUTH: {e}")
        raise

def get_token():
    try:
        token_info = session.get('token_info', None)
        print(f"Token info from session: {'Present' if token_info else 'Missing'}")
        
        if not token_info:
            print("No token found in session")
            return None

        now = int(time.time())
        is_expired = token_info['expires_at'] - now < 60
        
        if is_expired:
            print("Token is expired, refreshing...")
            sp_oauth = create_spotify_oauth()
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
            
        return token_info
    except Exception as e:
        print(f"ERROR IN get_token: {e}")
        return None

def get_spotify_client():
    try:
        token_info = get_token()
        if not token_info:
            print("Could not get token")
            return None
        return spotipy.Spotify(auth=token_info['access_token'])
    except Exception as e:
        print(f"ERROR creating Spotify client: {e}")
        return None

def is_authenticated():
    try:
        return 'token_info' in session
    except Exception as e:
        print(f"Error checking authentication: {e}")
        return False

# Health check route for debugging
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

# Routes
try:
    @app.route('/')
    def index():
        print("Route / accessed")
        if not is_authenticated():
            return render_template('login.html')
        return redirect(url_for('dashboard'))

    @app.route('/login')
    def login():
        print("Login route accessed")
        try:
            sp_oauth = create_spotify_oauth()
            auth_url = sp_oauth.get_authorize_url()
            print(f"Generated auth URL: {auth_url}")
            return redirect(auth_url)
        except Exception as e:
            print(f"Error during login: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/callback')
    def callback():
        print("Callback route accessed with args:", request.args)
        try:
            sp_oauth = create_spotify_oauth()
            session.clear()
            code = request.args.get('code')
            token_info = sp_oauth.get_access_token(code)
            session['token_info'] = token_info
            print("Successfully got token info")
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Error during callback: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/logout')
    def logout():
        print("Logout route accessed")
        session.clear()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    def dashboard():
        print("Dashboard route accessed")
        if not is_authenticated():
            print("Not authenticated, redirecting to index")
            return redirect(url_for('index'))
            
        try:
            sp = get_spotify_client()
            if not sp:
                raise Exception("Could not get Spotify client")
                
            user_info = sp.me()
            print(f"Got user info for: {user_info.get('display_name', 'Unknown')}")
            
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
                active_page='dashboard'
            )
        except Exception as e:
            print(f"Error in dashboard route: {e}")
            import traceback
            traceback.print_exc()
            return render_template('error.html', error=str(e))

    # Add your other routes (basics, music_dna, artist_search) here
    # ...

    # API routes for artist search
    @app.route('/api/search-artist')
    def search_artist():
        print("Search artist route accessed with query:", request.args.get('query'))
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
            print(f"Error in search_artist: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/artist/<artist_id>')
    def get_artist_details(artist_id):
        print(f"Artist details route accessed for ID: {artist_id}")
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
            
            # No longer getting related artists since the API is deprecated
            
            return jsonify({
                "artist": artist,
                "top_tracks": top_tracks,
                "albums": albums
            })
        except Exception as e:
            print(f"Error in get_artist_details: {e}")
            return jsonify({"error": str(e)}), 500
except Exception as e:
    print(f"ERROR DEFINING ROUTES: {e}")
    import traceback
    traceback.print_exc()

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Global error handler caught: {str(e)}")
    return jsonify({"error": str(e)}), 500

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