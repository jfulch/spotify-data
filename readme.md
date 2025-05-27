# Spotify Music Analysis Dashboard
A personalized web application that provides in-depth analysis of your Spotify listening habits, showcasing your musical taste profile and listening patterns.

Check out the live deployed version here: https://jfulch-spotify-data.up.railway.app/

## Overview
This application connects to your Spotify account and analyzes your listening history to generate insights about your music preferences. It visualizes your top artists, tracks, genres, and provides detailed analysis of your musical "DNA" through audio feature analysis.

## Features

### The Basics
- Top Artists: View your most listened artists over different time periods (4 weeks, 6 months, all-time)
- Top Tracks: Discover your most played songs with popularity metrics
- Genre Analysis: See your most common music genres
- Recent Plays: Check your recently played artists and tracks

### Music DNA
- Mood Analysis: Get insights about the emotional characteristics of your music
- Audio Features Radar: Visualize the musical attributes that define your taste (energy, danceability, etc.)
- Uniqueness Score: See how mainstream or underground your music taste is
- Listening Schedule: Discover your music listening patterns throughout the day

## Project Structure
```
spotify-data/
│
├── app.py                  # Main Flask application
├── spotify_analysis/       # Analysis modules
│   ├── __init__.py
│   ├── artist_analysis.py
│   ├── audio_analysis.py
│   └── recent_plays.py
│
├── static/
│   ├── css/                # CSS files
│   └── img/                # Images and icons
│
├── templates/              # HTML templates
│   ├── layout.html
│   ├── index.html
│   ├── basics.html
│   └── music_dna.html
│
└── requirements.txt        # Python dependencies
```

## Technologies Used
- Backend: Flask, Spotipy (Python Spotify API wrapper)
- Frontend: HTML, CSS, JavaScript
- Data Visualization: Chart.js
- Authentication: OAuth 2.0 (via Spotify API)

## Future Improvements
- Add social sharing functionality
- Implement playlist recommendations based on analysis
- Create time-based analysis to show how your music taste evolves
- Develop comparison feature to compare your taste with friends
- Add more detailed genre breakdown and music discovery tools