import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# Configurar autenticación con Spotify usando SpotifyOAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-modify-public"  # O "playlist-modify-private" según corresponda
))

# ID, nombre y URL de la playlist se toman de las variables de entorno
PLAYLIST_ID = os.getenv("PLAYLIST_ID")
PLAYLIST_NAME = os.getenv("PLAYLIST_NAME")
PLAYLIST_URL = os.getenv("PLAYLIST_URL")

print(f"🎵 Playlist: {PLAYLIST_NAME}")
