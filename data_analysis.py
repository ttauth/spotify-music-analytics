import sqlite3
import pandas as pd

conn = sqlite3.connect('spotify_data.db')
cursor = conn.cursor()

# Genre Analysis
def analyze_genres():
    query = '''
    SELECT genre, count
    FROM top_genres
    ORDER BY count DESC
    '''
    top_genres_df = pd.read_sql(query, conn)
    print("Top Genres:")
    print(top_genres_df)

# Listening Patterns
def analyze_listening_patterns():
    query = '''
    SELECT strftime('%H', played_at) as hour, COUNT(*) as play_count
    FROM listening_history
    GROUP BY hour
    ORDER BY hour
    '''
    hourly_patterns_df = pd.read_sql(query, conn)
    print("Listening Patterns by Hour:")
    print(hourly_patterns_df)

    query = '''
    SELECT strftime('%w', played_at) as day, COUNT(*) as play_count
    FROM listening_history
    GROUP BY day
    ORDER BY day
    '''
    daily_patterns_df = pd.read_sql(query, conn)
    daily_patterns_df['day'] = daily_patterns_df['day'].replace({
        '0': 'Sunday',
        '1': 'Monday',
        '2': 'Tuesday',
        '3': 'Wednesday',
        '4': 'Thursday',
        '5': 'Friday',
        '6': 'Saturday'
    })
    print("Listening Patterns by Day:")
    print(daily_patterns_df)

# Artist and Track Popularity Over Time
def analyze_popularity_over_time():
    query = '''
    SELECT played_at, track_name, artist_name
    FROM listening_history
    ORDER BY played_at
    '''
    popularity_df = pd.read_sql(query, conn)
    popularity_df['played_at'] = pd.to_datetime(popularity_df['played_at'])
    popularity_df['date'] = popularity_df['played_at'].dt.date
    popularity_df = popularity_df.groupby(['date', 'artist_name', 'track_name']).size().reset_index(name='play_count')
    print("Artist and Track Popularity Over Time:")
    print(popularity_df)

# Perform Analyses
analyze_genres()
analyze_listening_patterns()
analyze_popularity_over_time()

conn.close()
