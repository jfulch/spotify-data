
def analyze_music_mood(spotify_client, time_range='medium_term'):
    """Analyze the 'mood' of your music based on genres instead of audio features"""
    tracks = get_top_tracks(spotify_client, time_range=time_range, limit=50)
    
    # Since we don't have audio features, let's analyze based on your top artists' genres
    artists_results = spotify_client.current_user_top_artists(time_range=time_range, limit=20)
    
    # Collect genres and their occurrence count
    genres = {}
    for artist in artists_results['items']:
        for genre in artist['genres']:
            genres[genre] = genres.get(genre, 0) + 1
    
    # Analyze mood based on genre keywords
    happy_keywords = ['pop', 'dance', 'edm', 'happy']
    angry_keywords = ['metal', 'hardcore', 'punk', 'death']
    sad_keywords = ['sad', 'blues', 'emo', 'soul']
    chill_keywords = ['chill', 'ambient', 'lofi', 'acoustic']
    
    mood_scores = {
        'happy': 0,
        'angry': 0,
        'sad': 0,
        'chill': 0
    }
    
    # Calculate mood scores based on genre keywords
    for genre, count in genres.items():
        for keyword in happy_keywords:
            if keyword in genre.lower():
                mood_scores['happy'] += count
        for keyword in angry_keywords:
            if keyword in genre.lower():
                mood_scores['angry'] += count
        for keyword in sad_keywords:
            if keyword in genre.lower():
                mood_scores['sad'] += count
        for keyword in chill_keywords:
            if keyword in genre.lower():
                mood_scores['chill'] += count
    
    # Determine dominant mood
    dominant_mood = max(mood_scores.items(), key=lambda x: x[1])[0] if any(mood_scores.values()) else 'balanced'
    
    # Map to mood descriptions
    mood_descriptions = {
        'happy': 'Happy & Energetic',
        'angry': 'Angry & Intense',
        'sad': 'Sad & Emotional',
        'chill': 'Relaxed & Chill',
        'balanced': 'Balanced'
    }
    
    return {
        'mood': mood_descriptions[dominant_mood],
        'genre_analysis': {
            'top_genres': sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5],
            'mood_scores': mood_scores
        },
        'danceability_interpretation': "Likely danceable" if dominant_mood in ['happy', 'chill'] else "Less danceable"
    }

def get_top_tracks(spotify_client, time_range='medium_term', limit=20):
    """Get user's top tracks with audio features"""
    results = spotify_client.current_user_top_tracks(time_range=time_range, limit=limit)
    
    tracks_data = []
    for i, item in enumerate(results['items']):
        track_info = {
            'rank': i + 1,
            'title': item['name'],
            'artist': item['artists'][0]['name'],
            'album': item['album']['name'],
            'popularity': item['popularity']
        }
        tracks_data.append(track_info)
    
    return tracks_data

def get_top_tracks_with_audio_features(spotify_client, time_range='medium_term', limit=20):
    """Get user's top tracks with audio features - safely handles API limits"""
    results = spotify_client.current_user_top_tracks(time_range=time_range, limit=limit)
    
    tracks_data = []
    batch_size = 5  # Process in small batches to avoid API limitations
    
    for i in range(0, min(len(results['items']), limit), batch_size):
        batch_items = results['items'][i:i+batch_size]
        track_ids = [item['id'] for item in batch_items]
        
        try:
            audio_features = spotify_client.audio_features(track_ids)
            
            # Process this batch of tracks with their audio features
            for j, (item, features) in enumerate(zip(batch_items, audio_features)):
                if features:  # Check if features is not None
                    track_info = {
                        'rank': i + j + 1,
                        'title': item['name'],
                        'artist': item['artists'][0]['name'],
                        'album': item['album']['name'],
                        'popularity': item['popularity'],
                        'danceability': features['danceability'],
                        'energy': features['energy'],
                        'tempo': int(features['tempo']),
                        'valence': features['valence']
                    }
                else:
                    # Use basic info if audio features aren't available
                    track_info = {
                        'rank': i + j + 1,
                        'title': item['name'],
                        'artist': item['artists'][0]['name'],
                        'album': item['album']['name'],
                        'popularity': item['popularity']
                    }
                tracks_data.append(track_info)
        
        except Exception as e:
            print(f"Error fetching audio features: {e}")
            # Add tracks with basic info when audio features fail
            for j, item in enumerate(batch_items):
                track_info = {
                    'rank': i + j + 1,
                    'title': item['name'],
                    'artist': item['artists'][0]['name'],
                    'album': item['album']['name'],
                    'popularity': item['popularity']
                }
                tracks_data.append(track_info)
    
    return tracks_data

def analyze_recent_plays(spotify_client, limit=50):
    """Analyze recently played tracks"""
    try:
        results = spotify_client.current_user_recently_played(limit=limit)
        
        # Analyze by time of day
        hour_distribution = {i: 0 for i in range(24)}
        artist_frequency = {}
        
        for item in results['items']:
            # Convert timestamp to hour
            played_at = item['played_at']
            hour = int(played_at.split('T')[1].split(':')[0])
            hour_distribution[hour] += 1
            
            # Count artist plays
            artist = item['track']['artists'][0]['name']
            artist_frequency[artist] = artist_frequency.get(artist, 0) + 1
        
        return {
            'hour_distribution': hour_distribution,
            'peak_listening_hour': max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else None,
            'top_recent_artists': sorted(artist_frequency.items(), key=lambda x: x[1], reverse=True)[:5] if artist_frequency else []
        }
    except Exception as e:
        print(f"Error analyzing recent plays: {e}")
        return {
            'hour_distribution': {},
            'peak_listening_hour': None,
            'top_recent_artists': []
        }