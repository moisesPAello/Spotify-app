from spotify import sp

def search_song(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    return results['tracks']['items'][0] if results['tracks']['items'] else None

def get_playlist_tracks(playlist_id):
    return sp.playlist_tracks(playlist_id)['items']

def add_song_to_playlist(playlist_id, track_uri):
    sp.playlist_add_items(playlist_id, [track_uri])

def remove_song_from_playlist(playlist_id, track_uri):
    sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])

def get_playlist_details(playlist_id):
    return sp.playlist(playlist_id)