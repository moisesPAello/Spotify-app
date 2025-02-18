import random
import discord
from discord.ext import commands
import asyncio
from utils.voice_utils import search_youtube, create_audio_source
from utils.spotify_utils import get_playlist_tracks, search_song
from spotify import PLAYLIST_ID

class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.queue = []
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
    async def play_playlist_static(self, ctx):
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

    @commands.command(name="skip", help="Salta a la siguiente canción de la cola o a varias si se especifica un número.")
    async def skip(self, ctx, num_songs: int = 1):
        # Verificar que num_songs sea mayor a 0
        if num_songs <= 0:
            await ctx.send("❌ El número de canciones a saltar debe ser mayor que 0.")
            return

        # Verificar que haya una canción en reproducción
        if ctx.voice_client and ctx.voice_client.is_playing():
            self.skipping = True  # Activar la bandera para evitar la ejecución del callback duplicado
            ctx.voice_client.stop()  # Esto disparará el callback 'after_playing'
            await ctx.send("⏭️ Saltando la canción actual...")

            # Si se pide saltar más de 1, quitar canciones adicionales de la cola
            skipped_songs = []
            for _ in range(num_songs - 1):
                if self.queue:
                    skipped_songs.append(self.queue.pop(0))
                else:
                    break
            if skipped_songs:
                song_names = ", ".join([song['name'] for song in skipped_songs])
                await ctx.send(f"⏭️ También se han saltado: {song_names}")

            # Llamar manualmente a reproducir la siguiente canción
            await self.play_next_song(ctx)
            self.skipping = False
        else:
            await ctx.send("❌ No hay canción en reproducción para saltar.")

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

    @commands.command(name="queue", help="Muestra las canciones en la cola.")
    async def queue_list(self, ctx):
        if self.queue:
            response = "🎵 **Canciones en la cola:**\n"
            for idx, track in enumerate(self.queue):
                response += f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}\n"
            await ctx.send(response)
        else:
            await ctx.send("❌ No hay canciones en la cola.")

    @commands.command(name="queue_remove", help="Elimina una canción específica de la cola.")
    async def remove_from_queue(self, ctx, *, song_name):
        for idx, track in enumerate(self.queue):
            if track["name"].lower() == song_name.lower():
                del self.queue[idx]
                await ctx.send(f"✅ La canción **{track['name']}** ha sido eliminada de la cola.")
                return
        await ctx.send(f"❌ No encontré la canción **{song_name}** en la cola.")

    @commands.command(name="clear", help="Limpia la cola de reproducción. Puedes especificar cuántas canciones eliminar a partir de la siguiente.")
    async def clear(self, ctx, count: int = None):
        if not self.queue:
            await ctx.send("❌ La cola de reproducción ya está vacía.")
            return

        if count is None or count >= len(self.queue):
            self.queue.clear()
            await ctx.send("🧹 Toda la cola de reproducción ha sido eliminada.")
        else:
            del self.queue[:count]
            await ctx.send(f"🧹 Se eliminaron las siguientes {count} canciones de la cola.")

    @commands.command(name="shuffle", help="Mezcla aleatoriamente las canciones en la cola de reproducción.")
    async def shuffle(self, ctx):
        if len(self.queue) < 2:
            await ctx.send("❌ No hay suficientes canciones en la cola para mezclar.")
            return

        random.shuffle(self.queue)
        await ctx.send("🔀 La cola de reproducción ha sido mezclada.")

    @commands.command(name="playing", aliases=["np"], help="Muestra la canción que se está reproduciendo actualmente.")
    async def now_playing(self, ctx):
        if self.current_song:
            await ctx.send(f"🎶 Ahora suena: **{self.current_song['name']}** - {self.current_song['artists'][0]['name']}")
        else:
            await ctx.send("❌ No hay ninguna canción reproduciéndose.")

    @commands.command(name="play", help="Agrega una canción a la cola y comienza a reproducir si no hay nada reproduciéndose.")
    async def play_song(self, ctx, *, song_name):
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
                    # Solo llamar a play_next_song si no estamos en skip
                    if not getattr(self, "skipping", False):
                        asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.bot.loop)

                voice_client.play(audio_source, after=after_playing)
        else:
            self.is_playing = False
            await ctx.send("✅ No hay más canciones en la cola para reproducir.")


async def setup(bot):
    await bot.add_cog(VoiceCommands(bot))
