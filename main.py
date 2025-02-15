import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from commands import spotify_commands, voice_commands

# Cargar el archivo .env
load_dotenv()

# Configurar el bot de Discord
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# Registrar comandos
bot.add_command(spotify_commands.addsong)
bot.add_command(spotify_commands.list_songs)
bot.add_command(spotify_commands.remove_song)
bot.add_command(spotify_commands.search_song)
bot.add_command(spotify_commands.playlist_link)
bot.add_command(spotify_commands.playlist_details)
bot.add_command(voice_commands.play_playlist)

# Ejecutar el bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))