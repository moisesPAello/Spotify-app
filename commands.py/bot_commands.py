import yt_dlp
from discord import FFmpegPCMAudio
from discord.ext import commands
from spotify import sp, PLAYLIST_ID, PLAYLIST_NAME, PLAYLIST_URL

# Función auxiliar para obtener las canciones de la playlist
def get_playlist_tracks():
    playlist_tracks = sp.playlist_tracks(PLAYLIST_ID)
    return playlist_tracks['items'] if playlist_tracks else []

# Función auxiliar para buscar y obtener URL de la canción en YouTube
def search_song_on_youtube(song_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
        if 'entries' in info and info['entries']:
            return info['entries'][0]['url']
    return None

# Comando para reproducir la playlist
@commands.command(help="Reproduce la primera canción de la playlist de Spotify.")
async def play_playlist(ctx):
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"✅ Conectado al canal de voz: {channel.name}")
        else:
            await ctx.send("❌ No estás en un canal de voz.")
            return

    # Obtener y reproducir la primera canción de la playlist
    tracks = get_playlist_tracks()
    if not tracks:
        await ctx.send("❌ La playlist está vacía.")
        return

    track = tracks[0]['track']
    song_name = f"{track['name']} {track['artists'][0]['name']}"
    await ctx.send(f"🎵 Buscando en YouTube: {song_name}")

    video_url = search_song_on_youtube(song_name)
    if not video_url:
        await ctx.send("❌ No encontré la canción en YouTube.")
        return

    await ctx.send(f"▶️ Reproduciendo: {song_name}")

    # Reproducir el audio en Discord
    voice_client = ctx.voice_client
    audio_source = FFmpegPCMAudio(video_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
    
    if not voice_client.is_playing():
        voice_client.play(audio_source, after=lambda e: print(f"Error: {e}") if e else None)
    else:
        await ctx.send("❌ Ya estoy reproduciendo una canción.")

# Comando para añadir canción a la playlist
@commands.command(help="Añade una canción a la playlist de Spotify.")
async def addsong(ctx, *, song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        sp.playlist_add_items(PLAYLIST_ID, [track_uri])
        await ctx.send(f"✅ [{track['name']}] ha sido añadida a la playlist {PLAYLIST_NAME} 🎵")
    else:
        await ctx.send("❌ No encontré esa canción en Spotify.")

# Comando para listar las canciones de la playlist
@commands.command(help="Lista las canciones de la playlist de Spotify.")
async def list_songs(ctx):
    tracks = get_playlist_tracks()
    if tracks:
        response = "🎵 **Canciones en la playlist:**\n"
        for idx, item in enumerate(tracks):
            track = item['track']
            response += f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}\n"
        await ctx.send(response)
    else:
        await ctx.send("❌ La playlist está vacía.")

# Comando para eliminar una canción de la playlist
@commands.command(help="Elimina una canción de la playlist de Spotify.")
async def remove_song(ctx, *, song_name):
    tracks = get_playlist_tracks()
    for item in tracks:
        track = item['track']
        if track['name'].lower() == song_name.lower():
            sp.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, [track['uri']])
            await ctx.send(f"✅ [{track['name']}] ha sido eliminada de la playlist: {PLAYLIST_NAME} 🎵")
            return
    await ctx.send("❌ No encontré esa canción en la playlist.")

# Comando para buscar detalles de una canción
@commands.command(help="Busca detalles de una canción en Spotify.")
async def search_song(ctx, *, song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        response = f"🎵 **Resultado de búsqueda:**\n"
        response += f"Nombre: {track['name']}\n"
        response += f"Artista: {track['artists'][0]['name']}\n"
        response += f"Álbum: {track['album']['name']}\n"
        response += f"URI: {track['uri']}\n"
        await ctx.send(response)
    else:
        await ctx.send("❌ No encontré esa canción en Spotify.")

# Comando para obtener el enlace de la playlist
@commands.command(help="Obtiene el enlace de la playlist de Spotify.")
async def playlist_link(ctx):
    await ctx.send(f"🔗 Enlace de la playlist: {PLAYLIST_URL}")

# Comando para obtener detalles de la playlist
@commands.command(help="Obtiene detalles de la playlist de Spotify.")
async def playlist_details(ctx):
    playlist = sp.playlist(PLAYLIST_ID)
    response = f"🎵 **Detalles de la playlist:**\n"
    response += f"Nombre: {playlist['name']}\n"
    response += f"Descripción: {playlist['description']}\n"
    response += f"Enlace: {playlist['external_urls']['spotify']}\n"
    response += f"Número de canciones: {playlist['tracks']['total']}\n"
    await ctx.send(response)
