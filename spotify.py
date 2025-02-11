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

# Obtener el nombre y el enlace de la playlist desde las variables de entorno
PLAYLIST_NAME = os.getenv("PLAYLIST_NAME")
PLAYLIST_URL = os.getenv("PLAYLIST_URL")
print(f"🎵 Playlist: {PLAYLIST_NAME}")