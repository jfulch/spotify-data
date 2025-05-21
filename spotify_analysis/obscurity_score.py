def calculate_obscurity_score(spotify_client):
    """Calculate how unique/obscure the user's music taste is"""
    # Get user's top artists
    top_artists = spotify_client.current_user_top_artists(limit=50, time_range='medium_term')
    
    # Calculate average popularity (Spotify's popularity is 0-100)
    if not top_artists['items']:
        return 50  # Default value if no artists
        
    total_popularity = sum(artist['popularity'] for artist in top_artists['items'])
    avg_popularity = total_popularity / len(top_artists['items'])
    
    # Invert the scale - lower popularity means higher obscurity
    # Convert to 0-100 scale where 100 is most obscure
    obscurity_score = int(100 - avg_popularity)
    
    return obscurity_score