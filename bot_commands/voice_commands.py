import discord
from discord.ext import commands
import asyncio
from utils.voice_utils import search_youtube, create_audio_source
from utils.spotify_utils import get_playlist_tracks, search_song
from spotify import PLAYLIST_ID, PLAYLIST_NAME, PLAYLIST_URL

# ----------------------------
# Variables Globales para la Cola
# ----------------------------
queue = []          # Lista de canciones (cada una es un diccionario de Spotify)
is_playing = False  # Indica si se está reproduciendo alguna canción
current_song = None # Canción actual en reproducción

# ----------------------------
# Función Auxiliar para Conectar al Canal de Voz
# ----------------------------
async def ensure_voice(ctx):
    """Verifica y conecta al canal de voz del autor si no está conectado."""
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"✅ Conectado al canal de voz: {channel.name}")
        else:
            await ctx.send("❌ No estás en un canal de voz.")
            return False
    return True

# ----------------------------
# Comando: Reproducción Directa de la Playlist
# ----------------------------
@commands.command(name="play_playlist", help="Reproduce la primera canción de la playlist de Spotify.")
async def play_playlist(ctx):
    # Conectar al canal de voz si es necesario
    if not await ensure_voice(ctx):
        return

    tracks = get_playlist_tracks(PLAYLIST_ID)
    if not tracks:
        await ctx.send("❌ La playlist está vacía.")
        return

    track = tracks[0]['track']
    song_query = f"{track['name']} {track['artists'][0]['name']}"
    await ctx.send(f"🎵 Buscando en YouTube: {song_query}")

    url = search_youtube(song_query)
    if not url:
        await ctx.send("❌ No encontré la canción en YouTube.")
        return

    await ctx.send(f"▶️ Reproduciendo: {song_query}")
    voice_client = ctx.voice_client
    audio_source = create_audio_source(url)
    if not voice_client.is_playing():
        voice_client.play(audio_source, after=lambda e: print(f"Error: {e}") if e else None)
    else:
        await ctx.send("❌ Ya estoy reproduciendo una canción.")

# ----------------------------
# Comando: Agregar Canciones a la Cola y Reproducir
# ----------------------------
@commands.command(name="play", help="Agrega una canción a la cola y comienza a reproducir si no hay nada reproduciéndose.")
async def play(ctx, *, song_name):
    global is_playing
    if not await ensure_voice(ctx):
        return

    track = search_song(song_name)
    if track:
        queue.append(track)
        await ctx.send(f"🎵 **{track['name']}** añadida a la cola de reproducción.")
        if not is_playing:
            await play_next_song(ctx)
    else:
        await ctx.send("❌ No se encontró esa canción en Spotify.")

# ----------------------------
# Comando: Saltar Canción
# ----------------------------
@commands.command(name="skip", help="Salta a la siguiente canción de la cola.")
async def skip(ctx):
    global is_playing
    if queue:
        await play_next_song(ctx)
    else:
        await ctx.send("❌ No hay más canciones en la cola.")

# ----------------------------
# Comando: Pausar Reproducción
# ----------------------------
@commands.command(name="pause", help="Pausa la reproducción actual.")
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ La reproducción ha sido pausada.")
    else:
        await ctx.send("❌ No hay música reproduciéndose.")

# ----------------------------
# Comando: Reanudar Reproducción
# ----------------------------
@commands.command(name="resume", help="Reanuda la reproducción pausada.")
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ La reproducción ha sido reanudada.")
    else:
        await ctx.send("❌ La música no está pausada.")

# ----------------------------
# Comando: Detener Reproducción y Limpiar Cola
# ----------------------------
@commands.command(name="stop", help="Detiene la reproducción y limpia la cola.")
async def stop(ctx):
    global is_playing, queue
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    is_playing = False
    queue.clear()
    await ctx.send("⏹️ La reproducción ha sido detenida y la cola ha sido limpiada.")

# ----------------------------
# Comando: Mostrar la Cola
# ----------------------------
@commands.command(name="queue_list", help="Muestra las canciones en la cola.")
async def queue_list(ctx):
    if queue:
        response = "🎵 **Canciones en la cola:**\n"
        for idx, track in enumerate(queue):
            response += f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}\n"
        await ctx.send(response)
    else:
        await ctx.send("❌ No hay canciones en la cola.")

# ----------------------------
# Comando: Eliminar Canción de la Cola
# ----------------------------
@commands.command(name="remove_from_queue", help="Elimina una canción específica de la cola.")
async def remove_from_queue(ctx, *, song_name):
    global queue
    for idx, track in enumerate(queue):
        if track['name'].lower() == song_name.lower():
            del queue[idx]
            await ctx.send(f"✅ La canción **{track['name']}** ha sido eliminada de la cola.")
            return
    await ctx.send(f"❌ No encontré la canción **{song_name}** en la cola.")

# ----------------------------
# Función: Reproducir la Siguiente Canción
# ----------------------------
async def play_next_song(ctx):
    global is_playing, current_song, queue

    if queue:
        current_song = queue.pop(0)
        is_playing = True
        await ctx.send(f"🎶 Reproduciendo: **{current_song['name']}** - {current_song['artists'][0]['name']}")

        song_query = f"{current_song['name']} {current_song['artists'][0]['name']}"
        url = search_youtube(song_query)
        if not url:
            await ctx.send("❌ No encontré la canción en YouTube.")
            is_playing = False
            return

        voice_client = ctx.voice_client
        audio_source = create_audio_source(url)
        if not voice_client.is_playing():
            def after_playing(error):
                if error:
                    print(f"Error al reproducir: {error}")
                fut = asyncio.run_coroutine_threadsafe(play_next_song(ctx), ctx.bot.loop)
                try:
                    fut.result()
                except Exception as e:
                    print(f"Error en la cola: {e}")
            voice_client.play(audio_source, after=after_playing)
        else:
            await ctx.send("❌ Ya estoy reproduciendo una canción.")
    else:
        is_playing = False
