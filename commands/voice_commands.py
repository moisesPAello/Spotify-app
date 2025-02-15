from discord.ext import commands
from utils.voice_utils import search_youtube, create_audio_source
from utils.spotify_utils import get_playlist_tracks
from spotify import PLAYLIST_ID

@commands.command()
async def play_playlist(ctx):
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"✅ Conectado al canal de voz: {channel.name}")
        else:
            await ctx.send("❌ No estás en un canal de voz.")
            return

    tracks = get_playlist_tracks(PLAYLIST_ID)
    if not tracks:
        await ctx.send("❌ La playlist está vacía.")
        return

    track = tracks[0]['track']
    song_name = f"{track['name']} {track['artists'][0]['name']}"
    await ctx.send(f"🎵 Buscando en YouTube: {song_name}")

    url = search_youtube(song_name)
    if not url:
        await ctx.send("❌ No encontré la canción en YouTube.")
        return

    await ctx.send(f"▶️ Reproduciendo: {song_name}")

    voice_client = ctx.voice_client
    audio_source = create_audio_source(url)
    if not voice_client.is_playing():
        voice_client.play(audio_source, after=lambda e: print(f"Error: {e}") if e else None)
    else:
        await ctx.send("❌ Ya estoy reproduciendo una canción.")