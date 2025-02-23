import random
import discord
import yt_dlp
from discord.ext import commands
import asyncio
from enum import Enum
from typing import Optional, Union, List, Dict, Any
from utils.voice_utils import search_youtube, create_audio_source
from utils.spotify_utils import get_playlist_tracks, search_song, get_playlist_id_from_url
from spotify import PLAYLIST_ID

class LoopMode(Enum):
    OFF = 0
    SONG = 1
    QUEUE = 2

class Track:
    def __init__(self, data: Union[str, Dict[str, Any]]):
        self.url = data if isinstance(data, str) else None
        self.spotify_data = None if isinstance(data, str) else data
        
    @property
    def name(self) -> str:
        if self.spotify_data:
            return f"{self.spotify_data['name']} - {self.spotify_data['artists'][0]['name']}"
        return self.url

    def to_search_query(self) -> str:
        if self.spotify_data:
            return f"{self.spotify_data['name']} {self.spotify_data['artists'][0]['name']}"
        return self.url

class MusicPlayer:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.is_playing = False
        self.queue: List[Track] = []
        self.current_track: Optional[Track] = None
        self.loop_mode = LoopMode.OFF
        self.skipping = False

    async def play_track(self, ctx: commands.Context, track: Track) -> None:
        """Handles the actual playback of a track."""
        if not ctx.voice_client:
            return

        self.is_playing = True
        self.current_track = track

        # Get YouTube URL if needed
        url = track.url
        if not url:
            url = search_youtube(track.to_search_query())
            if not url:
                await ctx.send("❌ No se encontró la canción en YouTube.")
                self.is_playing = False
                await self.play_next(ctx)
                return

        # Create audio source and play
        try:
            audio_source = create_audio_source(url)
            await ctx.send(f"▶️ Reproduciendo: {track.name}")
            
            def after_playing(error):
                if error:
                    print(f"Error al reproducir: {error}")
                if not self.skipping:
                    asyncio.run_coroutine_threadsafe(
                        self._handle_playback_finished(ctx),
                        self.bot.loop
                    )
                self.skipping = False

            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            ctx.voice_client.play(audio_source, after=after_playing)
            
        except Exception as e:
            print(f"Error al reproducir: {e}")
            await ctx.send("❌ Error al reproducir la canción.")
            self.is_playing = False
            await self.play_next(ctx)

    async def _handle_playback_finished(self, ctx: commands.Context) -> None:
        """Handles what happens when a track finishes playing."""
        if self.loop_mode == LoopMode.SONG and self.current_track:
            await self.play_track(ctx, self.current_track)
        elif self.loop_mode == LoopMode.QUEUE and self.current_track:
            self.queue.append(self.current_track)
            await self.play_next(ctx)
        else:
            await self.play_next(ctx)

    async def play_next(self, ctx: commands.Context) -> None:
        """Plays the next track in the queue."""
        if not self.queue:
            self.is_playing = False
            await ctx.send("✅ No hay más canciones en la cola.")
            return

        next_track = self.queue.pop(0)
        await self.play_track(ctx, next_track)

class VoiceCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players: Dict[int, MusicPlayer] = {}

    def get_player(self, guild_id: int) -> MusicPlayer:
        """Gets or creates a MusicPlayer for a guild."""
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer(self.bot)
        return self.players[guild_id]

    async def ensure_voice(self, ctx: commands.Context) -> bool:
        """Ensures the bot is in a voice channel."""
        if ctx.voice_client is None:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                await ctx.send(f"✅ Conectado al canal de voz: {channel.name}")
                return True
            await ctx.send("❌ No estás en un canal de voz.")
            return False
        return True

    @commands.command(name="play", help="Reproduce una canción, URL o playlist.")
    async def play(self, ctx: commands.Context, *, query: str):
        if not await self.ensure_voice(ctx):
            return

        player = self.get_player(ctx.guild.id)
        query = query.strip()

        async def handle_spotify_playlist(playlist_id: str) -> None:
            tracks = get_playlist_tracks(playlist_id)
            if not tracks:
                await ctx.send("❌ No se pudo extraer la playlist de Spotify.")
                return
            for item in tracks:
                player.queue.append(Track(item["track"]))
            await ctx.send(f"🎵 {len(tracks)} canciones añadidas de la playlist de Spotify.")

        async def handle_youtube_playlist(url: str) -> None:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    if 'entries' in info:
                        for entry in info['entries']:
                            player.queue.append(Track(entry['url']))
                        await ctx.send(f"🎵 {len(info['entries'])} canciones añadidas de la playlist de YouTube.")
                except Exception as e:
                    await ctx.send("❌ Error al procesar la playlist de YouTube.")
                    print(f"Error: {e}")

        # Handle different types of input
        if query.startswith("http"):
            if "open.spotify.com/playlist" in query:
                await handle_spotify_playlist(get_playlist_id_from_url(query))
            elif "youtube.com/playlist" in query or "list=" in query:
                await handle_youtube_playlist(query)
            else:
                player.queue.append(Track(query))
                await ctx.send("🎵 URL añadida a la cola.")
        else:
            track = search_song(query)
            if track:
                player.queue.append(Track(track))
                await ctx.send(f"🎵 {track['name']} añadida a la cola.")
            else:
                await ctx.send("❌ No se encontró esa canción en Spotify.")

        if not player.is_playing:
            await player.play_next(ctx)

    @commands.command(name="skip", help="Salta canciones en la cola.")
    async def skip(self, ctx: commands.Context, num_songs: int = 1):
        player = self.get_player(ctx.guild.id)
        if num_songs <= 0:
            await ctx.send("❌ El número debe ser mayor que 0.")
            return

        if ctx.voice_client and ctx.voice_client.is_playing():
            player.skipping = True
            ctx.voice_client.stop()
            for _ in range(num_songs - 1):
                if player.queue:
                    player.queue.pop(0)
            await ctx.send(f"⏭️ Saltando {num_songs} canción(es)...")
        else:
            await ctx.send("❌ No hay canción en reproducción.")

    @commands.command(name="queue", help="Muestra la cola actual.")
    async def queue_list(self, ctx: commands.Context):
        player = self.get_player(ctx.guild.id)
        if not player.queue:
            await ctx.send("❌ La cola está vacía.")
            return

        queue_text = "🎵 **Cola de reproducción:**\n"
        for i, track in enumerate(player.queue, 1):
            queue_text += f"{i}. {track.name}\n"
        await ctx.send(queue_text)

    @commands.command(name="loop", help="Configura el modo de repetición.")
    async def loop(self, ctx: commands.Context, mode: str = None):
        player = self.get_player(ctx.guild.id)
        
        if mode == "song":
            if player.current_track:
                player.loop_mode = LoopMode.SONG
                await ctx.send(f"🔂 Repitiendo: {player.current_track.name}")
            else:
                await ctx.send("❌ No hay canción actual.")
        elif mode == "queue":
            if player.queue:
                player.loop_mode = LoopMode.QUEUE
                await ctx.send("🔁 Cola en bucle.")
            else:
                await ctx.send("❌ Cola vacía.")
        else:
            player.loop_mode = LoopMode.OFF
            await ctx.send("⏹ Repetición desactivada.")

    @commands.command(name="shuffle", help="Mezcla la cola.")
    async def shuffle(self, ctx: commands.Context):
        player = self.get_player(ctx.guild.id)
        if len(player.queue) < 2:
            await ctx.send("❌ No hay suficientes canciones para mezclar.")
            return
        
        random.shuffle(player.queue)
        await ctx.send("🔀 Cola mezclada.")

    @commands.command(name="clear", help="Limpia la cola.")
    async def clear(self, ctx: commands.Context):
        player = self.get_player(ctx.guild.id)
        player.queue.clear()
        await ctx.send("🧹 Cola limpiada.")

    @commands.command(name="leave", help="Desconecta el bot.")
    async def leave(self, ctx: commands.Context):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            if ctx.guild.id in self.players:
                del self.players[ctx.guild.id]
            await ctx.send("👋 Desconectado.")
        else:
            await ctx.send("❌ No estoy en un canal de voz.")

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCommands(bot))