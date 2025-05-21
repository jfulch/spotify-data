from track_analysis import get_top_tracks

def analyze_music_mood(spotify_client, time_range='medium_term'):
    """Analyze the 'mood' of your music based on genres instead of audio features"""
    try:
        # Get top tracks with audio features
        tracks = get_top_tracks(spotify_client, time_range=time_range, limit=50)
        
        # Try to calculate averages, but fall back to genre analysis if needed
        try:
            # Calculate averages if audio features are available
            avg_valence = sum(t.get('valence', 0) for t in tracks) / len(tracks)
            avg_energy = sum(t.get('energy', 0) for t in tracks) / len(tracks)
            avg_danceability = sum(t.get('danceability', 0) for t in tracks) / len(tracks)
            
            # Interpret mood
            if avg_valence > 0.6 and avg_energy > 0.6:
                mood = "Happy & Energetic"
            elif avg_valence < 0.4 and avg_energy > 0.6:
                mood = "Angry & Intense"
            elif avg_valence < 0.4 and avg_energy < 0.4:
                mood = "Sad & Chill"
            elif avg_valence > 0.6 and avg_energy < 0.4:
                mood = "Content & Relaxed"
            else:
                mood = "Balanced"
            
            return {
                'mood': mood,
                'average_valence': avg_valence,
                'average_energy': avg_energy,
                'average_danceability': avg_danceability,
                'danceability_interpretation': "Very danceable" if avg_danceability > 0.7 else 
                                              "Moderately danceable" if avg_danceability > 0.5 else 
                                              "Less danceable"
            }
        except KeyError:
            # Fall back to genre analysis if track data doesn't have audio features
            return analyze_mood_from_genres(spotify_client, time_range)
    except Exception as e:
        print(f"Error in mood analysis: {e}")
        return analyze_mood_from_genres(spotify_client, time_range)

def analyze_mood_from_genres(spotify_client, time_range='medium_term'):
    """Alternative mood analysis based on genres when audio features aren't available"""
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
        'average_valence': 0.5,  # Placeholder
        'average_energy': 0.5,   # Placeholder
        'average_danceability': 0.5,  # Placeholder
        'danceability_interpretation': "Based on genre analysis"
    }