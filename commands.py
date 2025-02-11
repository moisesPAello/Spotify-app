from discord.ext import commands
from spotify import sp, PLAYLIST_ID, PLAYLIST_NAME, PLAYLIST_URL

@commands.command()
async def addsong(ctx, *, song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        sp.playlist_add_items(PLAYLIST_ID, [track_uri])
        
        await ctx.send(f"✅ [{track['name']}] ha sido añadida a la playlist {PLAYLIST_NAME} 🎵")
    else:
        await ctx.send("❌ No encontré esa canción en Spotify.")

@commands.command()
async def list_songs(ctx):
    playlist_tracks = sp.playlist_tracks(PLAYLIST_ID)
    tracks = playlist_tracks['items']
    
    if tracks:
        response = "🎵 **Canciones en la playlist:**\n"
        for idx, item in enumerate(tracks):
            track = item['track']
            response += f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}\n"
        await ctx.send(response)
    else:
        await ctx.send("❌ La playlist está vacía.")

@commands.command()
async def remove_song(ctx, *, song_name):
    playlist_tracks = sp.playlist_tracks(PLAYLIST_ID)
    tracks = playlist_tracks['items']
    
    for item in tracks:
        track = item['track']
        if track['name'].lower() == song_name.lower():
            sp.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, [track['uri']])
            await ctx.send(f"✅ [{track['name']}] ha sido eliminada de la playlist: {PLAYLIST_NAME} 🎵")
            return
    
    await ctx.send("❌ No encontré esa canción en la playlist.")

@commands.command()
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

@commands.command()
async def playlist_link(ctx):
    await ctx.send(f"🔗 Enlace de la playlist: {PLAYLIST_URL}")

@commands.command()
async def playlist_details(ctx):
    playlist = sp.playlist(PLAYLIST_ID)
    response = f"🎵 **Detalles de la playlist:**\n"
    response += f"Nombre: {playlist['name']}\n"
    response += f"Descripción: {playlist['description']}\n"
    response += f"Enlace: {playlist['external_urls']['spotify']}\n"
    response += f"Número de canciones: {playlist['tracks']['total']}\n"
    await ctx.send(response)