import yt_dlp
from discord import FFmpegPCMAudio

def search_youtube(song_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
        return info['entries'][0]['url'] if 'entries' in info else None

def create_audio_source(url):
    return FFmpegPCMAudio(url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")