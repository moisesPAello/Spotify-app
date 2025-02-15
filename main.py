import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from bot_commands import spotify_commands, voice_commands, general_commands

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
bot.add_command(voice_commands.play)
bot.add_command(voice_commands.skip)
bot.add_command(voice_commands.pause)
bot.add_command(voice_commands.stop)
bot.add_command(voice_commands.queue_list)
bot.add_command(voice_commands.remove_from_queue)

# Registrar el comando de ayuda personalizado
general_commands.setup(bot)

# Ejecutar el bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))