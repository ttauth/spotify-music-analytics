import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('spotify_data.db')

# Export top_tracks table to CSV
top_tracks_df = pd.read_sql_query("SELECT * FROM top_tracks", conn)
top_tracks_df.to_csv('top_tracks.csv', index=False)

# Export top_genres table to CSV
top_genres_df = pd.read_sql_query("SELECT * FROM top_genres", conn)
top_genres_df.to_csv('top_genres.csv', index=False)

# Export listening_history table to CSV
listening_history_df = pd.read_sql_query("SELECT * FROM listening_history", conn)
listening_history_df.to_csv('listening_history.csv', index=False)

# Close the connection
conn.close()
