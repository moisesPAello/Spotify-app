import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from spotify import sp, PLAYLIST_ID, PLAYLIST_NAME
import commands as bot_commands

# Cargar el archivo .env
load_dotenv()

# Configurar el bot de Discord con intenciones adicionales
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# Registrar comandos
bot.add_command(bot_commands.addsong)
bot.add_command(bot_commands.list_songs)
bot.add_command(bot_commands.remove_song)
bot.add_command(bot_commands.search_song)
bot.add_command(bot_commands.playlist_link)
bot.add_command(bot_commands.playlist_details)

# Ejecutar el bot con tu token de Discord
bot.run(os.getenv("DISCORD_BOT_TOKEN"))