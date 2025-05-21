def get_top_artists(spotify_client, time_range='medium_term', limit=20):
    results = spotify_client.current_user_top_artists(time_range=time_range, limit=limit)
    artists = []
    
    for i, item in enumerate(results['items']):
        artist = {
            'name': item['name'],
            'rank': i + 1,
            'genres': ', '.join(item['genres'][:3]) if item['genres'] else 'No genres available',
            'popularity': item['popularity'],
            'followers': format_number(item['followers']['total']),
            'id': item['id']
        }
        artists.append(artist)
    
    return artists

def analyze_genre_distribution(artists_data):
    """
    Analyze genre distribution from a list of artists
    
    Parameters:
    - artists_data: List of artist dictionaries from get_top_artists()
    
    Returns:
    - List of (genre, count) tuples sorted by count
    """
    genres = {}
    
    # Count genres
    for artist in artists_data:
        # Split genres (they might be in "genre1, genre2" format from get_top_artists)
        artist_genres = artist['genres'].split(', ')
        
        for genre in artist_genres:
            if genre == 'No genres available':
                continue
                
            if genre in genres:
                genres[genre] += 1
            else:
                genres[genre] = 1
    
    # Sort by count
    sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    return sorted_genres[:10]  # Return top 10 genres

def format_number(num):
    """Format large numbers for display (e.g., 1234567 -> 1.2M)"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)