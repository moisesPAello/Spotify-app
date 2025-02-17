import discord
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f'!{command.qualified_name} {command.signature}'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Comandos del bot", color=discord.Color.blue())
        for cog, commands_list in mapping.items():
            filtered = await self.filter_commands(commands_list, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = cog.qualified_name if cog else "Sin categoría"
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=self.get_command_signature(command),
            description=command.help or "Sin descripción",
            color=discord.Color.blue()
        )
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=self.get_command_signature(group),
            description=group.help or "Sin descripción",
            color=discord.Color.blue()
        )
        if group.commands:
            for command in group.commands:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.help or "Sin descripción",
                    inline=False
                )
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=cog.qualified_name,
            description=cog.description or "Sin descripción",
            color=discord.Color.blue()
        )
        if cog.get_commands():
            for command in cog.get_commands():
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.help or "Sin descripción",
                    inline=False
                )
        channel = self.get_destination()
        await channel.send(embed=embed)

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Responde con 'Pong!' y muestra la latencia.")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! 🏓 Latencia: {latency}ms")

    @commands.command(name="info", help="Muestra información sobre el bot.")
    async def info(self, ctx):
        embed = discord.Embed(title="Información del Bot", color=discord.Color.blue())
        embed.add_field(name="Nombre", value=self.bot.user.name, inline=True)
        embed.add_field(name="ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Servidores", value=len(self.bot.guilds), inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))
    bot.help_command = CustomHelpCommand()
