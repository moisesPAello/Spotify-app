from discord.ext import commands
from utils.spotify_utils import (
    search_song,
    get_playlist_tracks,
    add_song_to_playlist,
    remove_song_from_playlist,
    get_playlist_details,
)
from spotify import PLAYLIST_ID, PLAYLIST_NAME, PLAYLIST_URL

class SpotifyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["add_spotify"], help="Añade una canción a la playlist de Spotify.")
    async def add_playlist(self, ctx, *, song_name):
        track = search_song(song_name)
        if track:
            add_song_to_playlist(PLAYLIST_ID, track["uri"])
            await ctx.send(f"✅ [{track['name']}] ha sido añadida a la playlist {PLAYLIST_NAME} 🎵")
        else:
            await ctx.send("❌ No encontré esa canción en Spotify.")

    @commands.command(aliases=["list_spotify"], help="Muestra todas las canciones en la playlist de Spotify.")
    async def list_playlist(self, ctx):
        tracks = get_playlist_tracks(PLAYLIST_ID)
        if tracks:
            response = "🎵 **Canciones en la playlist:**\n"
            for idx, item in enumerate(tracks):
                track = item["track"]
                response += f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}\n"
            await ctx.send(response)
        else:
            await ctx.send("❌ La playlist está vacía.")

    @commands.command(aliases=["remove_spotify"], help="Elimina una canción de la playlist de Spotify.")
    async def remove_playlist(self, ctx, *, song_name):
        tracks = get_playlist_tracks(PLAYLIST_ID)
        for item in tracks:
            track = item["track"]
            if track["name"].lower() == song_name.lower():
                remove_song_from_playlist(PLAYLIST_ID, track["uri"])
                await ctx.send(f"✅ [{track['name']}] ha sido eliminada de la playlist: {PLAYLIST_NAME} 🎵")
                return
        await ctx.send("❌ No encontré esa canción en la playlist.")

    @commands.command(aliases=["search_spotify"], help="Busca una canción en Spotify y muestra detalles.")
    async def search(self, ctx, *, song_name):
        track = search_song(song_name)
        if track:
            response = (
                f"🎵 **Resultado de búsqueda:**\n"
                f"Nombre: {track['name']}\n"
                f"Artista: {track['artists'][0]['name']}\n"
                f"Álbum: {track['album']['name']}\n"
                f"URI: {track['uri']}\n"
            )
            await ctx.send(response)
        else:
            await ctx.send("❌ No encontré esa canción en Spotify.")

    @commands.command(aliases=["link_spotify"], help="Muestra el enlace de la playlist de Spotify.")
    async def link_playlist(self, ctx):
        await ctx.send(f"🔗 Enlace de la playlist: {PLAYLIST_URL}")

    @commands.command(aliases=["details_spotify"], help="Muestra detalles de la playlist de Spotify.")
    async def details_playlist(self, ctx):
        playlist = get_playlist_details(PLAYLIST_ID)
        response = (
            f"🎵 **Detalles de la playlist:**\n"
            f"Nombre: {playlist['name']}\n"
            f"Descripción: {playlist['description']}\n"
            f"Enlace: {playlist['external_urls']['spotify']}\n"
            f"Número de canciones: {playlist['tracks']['total']}\n"
        )
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(SpotifyCommands(bot))
