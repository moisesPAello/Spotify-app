from spotify import sp  # Importa el sp configurado con SpotifyOAuth

# Función para buscar una canción en Spotify
def search_song(query):
    results = sp.search(q=query, limit=1, type='track')
    tracks = results.get('tracks', {}).get('items', [])
    return tracks[0] if tracks else None

# Función para obtener las canciones de una playlist de Spotify
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    return results.get('items', [])

# Función para agregar una canción a una playlist de Spotify
def add_song_to_playlist(playlist_id, track_uri):
    sp.playlist_add_items(playlist_id, [track_uri])

# Función para eliminar una canción de una playlist de Spotify
def remove_song_from_playlist(playlist_id, track_uri):
    sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])

# Función para obtener detalles de una playlist de Spotify
def get_playlist_details(playlist_id):
    return sp.playlist(playlist_id)

# Función para extraer el ID de una playlist desde su URL
def get_playlist_id_from_url(url):
    return url.split('/')[-1].split('?')[0]
