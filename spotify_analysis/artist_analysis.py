def get_top_artists(spotify_client, time_range='medium_term', limit=20):
    """Get user's top artists"""
    results = spotify_client.current_user_top_artists(time_range=time_range, limit=limit)
    
    artists_data = []
    for i, item in enumerate(results['items']):
        artist_info = {
            'rank': i + 1,
            'name': item['name'],
            'genres': ', '.join(item['genres'][:3]),
            'popularity': item['popularity'],
            'followers': f"{item['followers']['total']:,}"
        }
        artists_data.append(artist_info)
    
    return artists_data

def analyze_genre_distribution(spotify_client, time_range='medium_term'):
    """Analyze genre distribution across top artists"""
    artists = get_top_artists(spotify_client, time_range=time_range, limit=50)
    
    # Flatten all genres from all artists
    all_genres = []
    for artist in artists:
        genres = artist.get('genres', '').split(', ')
        all_genres.extend([g for g in genres if g])
    
    # Count occurrences
    genre_counts = {}
    for genre in all_genres:
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    # Sort by count
    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_genres