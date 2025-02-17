import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# Cargar variables de entorno
load_dotenv()

# Configurar los intents necesarios
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Inicializar el bot (sin help_command, éste se configurará en el cog general)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

async def load_cogs():
    # Los nombres de extensión deben incluir el nombre del paquete/folder
    await bot.load_extension("bot_commands.spotify_commands")
    await bot.load_extension("bot_commands.voice_commands")
    await bot.load_extension("bot_commands.general_commands")

async def main():
    await load_cogs()
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
