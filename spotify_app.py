import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

print("SPOTIPY_CLIENT_ID:", os.getenv("SPOTIPY_CLIENT_ID"))
print("SPOTIPY_CLIENT_SECRET:", os.getenv("SPOTIPY_CLIENT_SECRET"))
print("SPOTIPY_REDIRECT_URI:", os.getenv("SPOTIPY_REDIRECT_URI"))
print("PLAYLIST_ID:", os.getenv("PLAYLIST_ID"))
print("DISCORD_BOT_TOKEN:", os.getenv("DISCORD_BOT_TOKEN"))

# Configurar los permisos (alcances) para modificar playlists
SPOTIPY_SCOPE = "playlist-modify-public"

# Configurar autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=SPOTIPY_SCOPE
))

# Configurar el bot de Discord con intenciones adicionales
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ID de la playlist donde se agregarán las canciones
PLAYLIST_ID = os.getenv("PLAYLIST_ID")

# Obtener el nombre de la playlist
playlist = sp.playlist(PLAYLIST_ID)
PLAYLIST_NAME = playlist['name']
print(f"🎵 Playlist: {PLAYLIST_NAME}")

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# Comando para agregar una canción a la playlist
@bot.command()
async def addsong(ctx, *, song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        sp.playlist_add_items(PLAYLIST_ID, [track_uri])
        
        await ctx.send(f"✅ **{track['name']}** ha sido añadida a {PLAYLIST_NAME} 🎵")
    else:
        await ctx.send("❌ No encontré esa canción en Spotify.")

# Ejecutar el bot con tu token de Discord
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
