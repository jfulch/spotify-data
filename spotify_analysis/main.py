# main.py
import pandas as pd
from tabulate import tabulate

# Import your modules
from auth import get_spotify_client
from artist_analysis import get_top_artists, analyze_genre_distribution
from track_analysis import get_top_tracks, analyze_recent_plays
from mood_analysis import analyze_music_mood

def main():
    # Create Spotify client
    print("Authenticating with Spotify...")
    sp = get_spotify_client()
    
    # Get user profile to verify authentication
    user_info = sp.current_user()
    print(f"Logged in as: {user_info['display_name']}\n")
    
    # Show top artists for different time ranges
    time_ranges = {
        'short_term': 'Last 4 Weeks',
        'medium_term': 'Last 6 Months',
        'long_term': 'All Time'
    }
    
    for time_range, label in time_ranges.items():
        print(f"\n===== Top Artists - {label} =====")
        artists = get_top_artists(sp, time_range=time_range)
        df = pd.DataFrame(artists)
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    
    # Show top tracks
    print("\n===== Top Tracks - Last 6 Months =====")
    try:
        tracks = get_top_tracks(sp, time_range='medium_term')
        df = pd.DataFrame(tracks)
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    except Exception as e:
        print(f"Error displaying top tracks: {e}")
    
    # Show mood analysis
    print("\n===== Mood Analysis =====")
    mood = analyze_music_mood(sp)
    print(f"Your music mood: {mood['mood']}")
    print(f"Valence (positivity): {mood['average_valence']:.2f}")
    print(f"Energy: {mood['average_energy']:.2f}")
    print(f"Danceability: {mood['average_danceability']:.2f} - {mood['danceability_interpretation']}")
    
    # Show genre distribution
    print("\n===== Top Genres =====")
    genres = analyze_genre_distribution(sp)
    for genre, count in genres[:10]:
        print(f"{genre}: {count}")
    
    # Show recent plays analysis
    print("\n===== Recent Listening Habits =====")
    recent = analyze_recent_plays(sp)
    print(f"Peak listening hour: {recent['peak_listening_hour']}:00")
    print("\nMost played artists recently:")
    for artist, count in recent['top_recent_artists']:
        print(f"{artist}: {count} plays")

if __name__ == "__main__":
    main()