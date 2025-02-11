import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Configurar autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-modify-public"
))

# ID de la playlist donde se agregarán las canciones
PLAYLIST_ID = os.getenv("PLAYLIST_ID")

# Obtener el nombre y el enlace de la playlist
playlist = sp.playlist(PLAYLIST_ID)
PLAYLIST_NAME = playlist['name']
PLAYLIST_URL = playlist['external_urls']['spotify']
print(f"🎵 Playlist: {PLAYLIST_NAME}")