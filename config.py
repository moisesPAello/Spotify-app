import os
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

# Verificar que las variables de entorno estén configuradas correctamente
print("SPOTIPY_CLIENT_ID:", os.getenv("SPOTIPY_CLIENT_ID"))
print("SPOTIPY_CLIENT_SECRET:", os.getenv("SPOTIPY_CLIENT_SECRET"))
print("SPOTIPY_REDIRECT_URI:", os.getenv("SPOTIPY_REDIRECT_URI"))
print("PLAYLIST_ID:", os.getenv("PLAYLIST_ID"))
print("DISCORD_BOT_TOKEN:", os.getenv("DISCORD_BOT_TOKEN"))