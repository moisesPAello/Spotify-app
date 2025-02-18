import random
import discord
from discord.ext import commands
import asyncio
from utils.voice_utils import search_youtube, create_audio_source
from utils.spotify_utils import get_playlist_tracks, search_song
from spotify import PLAYLIST_ID
from enum import Enum

class LoopMode(Enum):
    OFF = 0
    SONG = 1
    QUEUE = 2

class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.queue = []           # Cola de canciones
        self.current_song = None  # Canción actualmente reproduciéndose
        self.prev_song = None     # Última canción reproducida (para loop de canción)
        self.loop_mode = LoopMode.OFF
        self.skipping = False     # Bandera para evitar callbacks duplicados

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

    @commands.command(name="leave", help="Desconecta al bot del canal de voz.")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Me he desconectado del canal de voz.")
        else:
            await ctx.send("❌ No estoy en un canal de voz.")

    @commands.command(name="play_playlist", aliases=["pp"], help="Reproduce toda la playlist de Spotify agregándola a la cola.")
    async def play_playlist_static(self, ctx):
        if not await self.ensure_voice(ctx):
            return

        tracks = get_playlist_tracks(PLAYLIST_ID)
        if not tracks:
            await ctx.send("❌ La playlist está vacía.")
            return

        for item in tracks:
            self.queue.append(item["track"])
        await ctx.send(f"🎵 **{len(tracks)}** canciones añadidas a la cola de reproducción.")

        if not self.is_playing:
            await self.play_next_song(ctx)

    @commands.command(name="play", help="Busca y añade una canción a la cola, y la reproduce si no hay nada en reproducción.")
    async def play(self, ctx, *, song_name):
        if not await self.ensure_voice(ctx):
            return

        track = search_song(song_name)
        if track:
            self.queue.append(track)
            await ctx.send(f"🎵 **{track['name']}** añadida a la cola. ({len(self.queue)} en total)")
            if not self.is_playing:
                await self.play_next_song(ctx)
        else:
            await ctx.send("❌ No se encontró esa canción en Spotify.")

    async def _play_track(self, ctx, track, loop: bool = False):
        """Función interna para reproducir un track.
        Si loop es True, se repetirá indefinidamente."""
        if ctx.voice_client is None:
            await ctx.send("❌ No estoy en un canal de voz.")
            return

        self.is_playing = True
        self.current_song = track
        await ctx.send(f"🎶 Reproduciendo: **{track['name']}** - {track['artists'][0]['name']}")

        song_query = f"{track['name']} {track['artists'][0]['name']}"
        url = search_youtube(song_query)

        if not url:
            await ctx.send("❌ No se encontró la canción en YouTube.")
            self.is_playing = False
            await self.play_next_song(ctx)
            return

        voice_client = ctx.voice_client

        # 🔹 Manejo de errores en la creación del audio
        try:
            audio_source = create_audio_source(url)
        except Exception as e:
            await ctx.send("❌ Error al procesar el audio.")
            print(f"Error al crear el audio: {e}")
            self.is_playing = False
            await self.play_next_song(ctx)
            return

        def after_playing(error):
            if error:
                print(f"Error al reproducir: {error}")

            if not self.skipping:
                # Consulta el modo de loop actual para decidir si se repite la canción
                if self.loop_mode == LoopMode.SONG and self.current_song == track:
                    self.bot.loop.create_task(self._play_track(ctx, track, loop=True))
                else:
                    self.prev_song = track
                    self.bot.loop.create_task(self.play_next_song(ctx))
            self.skipping = False

        # 🔹 Asegurar que no haya reproducción en curso antes de iniciar
        if voice_client.is_playing():
            voice_client.stop()
            await asyncio.sleep(0.5)  # Espera breve para evitar errores

        voice_client.play(audio_source, after=after_playing)

    async def play_next_song(self, ctx):
        """Reproduce la siguiente canción en la cola o maneja el loop de cola."""
        if self.loop_mode == LoopMode.SONG and self.current_song:
            # Si el loop de canción está activado, vuelve a reproducir la canción actual.
            await self._play_track(ctx, self.current_song, loop=True)
        elif self.queue:
            next_song = self.queue.pop(0)
            await self._play_track(ctx, next_song)
            
            # Si el loop de cola está activado, reinserta la canción al final de la cola.
            if self.loop_mode == LoopMode.QUEUE:
                self.queue.append(next_song)
        else:
            # Si la cola está vacía
            if self.loop_mode == LoopMode.QUEUE:
                await ctx.send("🔁 Loop de cola activado, pero la cola está vacía.")
            else:
                self.is_playing = False
                await ctx.send("✅ No hay más canciones en la cola.")

    @commands.command(name="skip", help="Salta a la siguiente canción de la cola o a varias si se especifica un número.")
    async def skip(self, ctx, num_songs: int = 1):
        if num_songs <= 0:
            await ctx.send("❌ El número de canciones a saltar debe ser mayor que 0.")
            return

        if ctx.voice_client and ctx.voice_client.is_playing():
            self.skipping = True
            ctx.voice_client.stop()  # Detiene la canción actual y dispara el callback
            await ctx.send("⏭️ Saltando la canción actual...")
            # Quita canciones adicionales de la cola según el número solicitado (menos la actual ya detenida)
            skipped_songs = []
            for _ in range(num_songs - 1):
                if self.queue:
                    skipped_songs.append(self.queue.pop(0))
                else:
                    break
            if skipped_songs:
                names = ", ".join([song['name'] for song in skipped_songs])
                await ctx.send(f"⏭️ También se saltaron: {names}")
            await self.play_next_song(ctx)
            self.skipping = False
        else:
            await ctx.send("❌ No hay canción en reproducción para saltar.")

    @commands.command(name="loop", help="Configura el loop: 'song' para repetir la canción actual, 'queue' para repetir la cola, 'off' para desactivar.")
    async def loop(self, ctx, mode: str = None):
        mode = mode.lower() if mode else None

        if mode == "song":
            if self.current_song:
                self.loop_mode = LoopMode.SONG
                await ctx.send(f"🔂 Loop activado para la canción: **{self.current_song['name']}** - {self.current_song['artists'][0]['name']}")
            else:
                await ctx.send("❌ No hay canción actual para poner en loop.")

        elif mode == "queue":
            if self.queue:
                self.loop_mode = LoopMode.QUEUE
                await ctx.send("🔁 Loop de cola activado.")
            else:
                await ctx.send("❌ No hay canciones en la cola para poner en loop.")

        elif mode == "off":
            self.loop_mode = LoopMode.OFF
            await ctx.send("⏹ Loop desactivado.")

        else:
            # Toggle: Si no se especifica, alterna entre activado y desactivado
            if self.loop_mode == LoopMode.OFF:
                if self.current_song:
                    self.loop_mode = LoopMode.SONG
                    await ctx.send(f"🔂 Loop activado para la canción: **{self.current_song['name']}** - {self.current_song['artists'][0]['name']}")
                else:
                    await ctx.send("❌ No hay canción actual para poner en loop.")
            else:
                self.loop_mode = LoopMode.OFF
                await ctx.send("⏹ Loop desactivado.")

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
            if song_name.lower() in track["name"].lower():
                del self.queue[idx]
                await ctx.send(f"✅ La canción **{track['name']}** ha sido eliminada de la cola.")
                return
        await ctx.send(f"❌ No encontré la canción **{song_name}** en la cola.")

    @commands.command(name="clear", help="Limpia la cola de reproducción. Si se especifica un número, elimina esa cantidad de canciones a partir de la siguiente.")
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

async def setup(bot):
    await bot.add_cog(VoiceCommands(bot))
