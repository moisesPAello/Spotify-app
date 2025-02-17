import discord
from discord.ext import commands
import asyncio
from utils.voice_utils import search_youtube, create_audio_source
from utils.spotify_utils import get_playlist_tracks, search_song
from spotify import PLAYLIST_ID

class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []          # Cola de canciones (cada canción es un diccionario de Spotify)
        self.is_playing = False  # Indica si se está reproduciendo algo
        self.current_song = None

    async def ensure_voice(self, ctx):
        """Verifica y conecta al canal de voz del usuario si es necesario."""
        if ctx.voice_client is None:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                await ctx.send(f"✅ Conectado al canal de voz: {channel.name}")
            else:
                await ctx.send("❌ No estás en un canal de voz.")
                return False
        return True

    @commands.command(name="play_playlist", aliases=["pp"], help="Reproduce toda la playlist de Spotify.")
    async def play_playlist(self, ctx):
        if not await self.ensure_voice(ctx):
            return

        tracks = get_playlist_tracks(PLAYLIST_ID)
        if not tracks:
            await ctx.send("❌ La playlist está vacía.")
            return

        # Agregar todas las canciones a la cola
        for item in tracks:
            self.queue.append(item["track"])
        await ctx.send(f"🎵 **{len(tracks)}** canciones añadidas a la cola de reproducción.")

        if not self.is_playing:
            await self.play_next_song(ctx)

    @commands.command(name="play", help="Agrega una canción a la cola y comienza a reproducir si no hay nada reproduciéndose.")
    async def play(self, ctx, *, song_name):
        if not await self.ensure_voice(ctx):
            return

        track = search_song(song_name)
        if track:
            self.queue.append(track)
            await ctx.send(f"🎵 **{track['name']}** añadida a la cola de reproducción.")
            if not self.is_playing:
                await self.play_next_song(ctx)
        else:
            await ctx.send("❌ No se encontró esa canción en Spotify.")

    @commands.command(name="skip", help="Salta a la siguiente canción de la cola.")
    async def skip(self, ctx):
        if self.queue:
            await self.play_next_song(ctx)
        else:
            await ctx.send("❌ No hay más canciones en la cola.")

    @commands.command(name="pause", help="Pausa la reproducción actual.")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ La reproducción ha sido pausada.")
        else:
            await ctx.send("❌ No hay música reproduciéndose.")

    @commands.command(name="resume", help="Reanuda la reproducción pausada.")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ La reproducción ha sido reanudada.")
        else:
            await ctx.send("❌ La música no está pausada.")

    @commands.command(name="stop", help="Detiene la reproducción y limpia la cola.")
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        self.is_playing = False
        self.queue.clear()
        await ctx.send("⏹️ La reproducción ha sido detenida y la cola ha sido limpiada.")

    @commands.command(name="queue_list", help="Muestra las canciones en la cola.")
    async def queue_list(self, ctx):
        if self.queue:
            response = "🎵 **Canciones en la cola:**\n"
            for idx, track in enumerate(self.queue):
                response += f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}\n"
            await ctx.send(response)
        else:
            await ctx.send("❌ No hay canciones en la cola.")

    @commands.command(name="remove_from_queue", help="Elimina una canción específica de la cola.")
    async def remove_from_queue(self, ctx, *, song_name):
        for idx, track in enumerate(self.queue):
            if track["name"].lower() == song_name.lower():
                del self.queue[idx]
                await ctx.send(f"✅ La canción **{track['name']}** ha sido eliminada de la cola.")
                return
        await ctx.send(f"❌ No encontré la canción **{song_name}** en la cola.")

    async def play_next_song(self, ctx):
        if self.queue:
            self.current_song = self.queue.pop(0)
            self.is_playing = True
            await ctx.send(f"🎶 Reproduciendo: **{self.current_song['name']}** - {self.current_song['artists'][0]['name']}")

            song_query = f"{self.current_song['name']} {self.current_song['artists'][0]['name']}"
            url = search_youtube(song_query)
            if not url:
                await ctx.send("❌ No encontré la canción en YouTube.")
                self.is_playing = False
                return

            voice_client = ctx.voice_client
            audio_source = create_audio_source(url)
            if not voice_client.is_playing():
                def after_playing(error):
                    if error:
                        print(f"Error al reproducir: {error}")
                    fut = asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.bot.loop)
                    try:
                        fut.result()
                    except Exception as e:
                        print(f"Error en la cola: {e}")

                voice_client.play(audio_source, after=after_playing)
            else:
                await ctx.send("❌ Ya estoy reproduciendo una canción.")
        else:
            self.is_playing = False

async def setup(bot):
    await bot.add_cog(VoiceCommands(bot))
