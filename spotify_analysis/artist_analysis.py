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

# Look for this function and update it:
def analyze_genre_distribution(sp):
    """Analyze the distribution of genres in a user's top artists"""
    # ISSUE: artists_data is being treated as an iterable, but it's the Spotify client
    
    # Replace the function with this corrected version:
    genre_counts = {}
    total_genres = 0
    
    # Get the user's top artists from different time ranges
    time_ranges = ['short_term', 'medium_term', 'long_term']
    
    for time_range in time_ranges:
        # Correctly get artists data from the Spotify client
        results = sp.current_user_top_artists(time_range=time_range, limit=50)
        
        # Now iterate through the actual artist items
        for artist in results['items']:
            if 'genres' in artist:
                for genre in artist['genres']:
                    if genre in genre_counts:
                        genre_counts[genre] += 1
                    else:
                        genre_counts[genre] = 1
                    total_genres += 1
    
    # Calculate percentages and sort
    genre_percentages = {genre: (count / total_genres) * 100 
                         for genre, count in genre_counts.items()}
    
    # Sort genres by percentage (descending)
    sorted_genres = sorted(genre_percentages.items(), 
                          key=lambda x: x[1], 
                          reverse=True)
    
    return {
        'genre_counts': genre_counts,
        'genre_percentages': genre_percentages,
        'sorted_genres': sorted_genres[:20]  # Top 20 genres
    }

def format_number(num):
    """Format large numbers for display (e.g., 1234567 -> 1.2M)"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)