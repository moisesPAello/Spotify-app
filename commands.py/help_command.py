import discord
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f'!{command.qualified_name} {command.signature}'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Comandos: ", color=discord.Color.blue())
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                embed.add_field(name=cog.qualified_name if cog else "🎥🎥🎥", value="\n".join(command_signatures), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), description=command.help or "Sin descripción", color=discord.Color.blue())
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=self.get_command_signature(group), description=group.help or "Sin descripción", color=discord.Color.blue())
        if group.commands:
            for command in group.commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "Sin descripción", inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title=cog.qualified_name, description=cog.description or "Sin descripción", color=discord.Color.blue())
        if cog.get_commands():
            for command in cog.get_commands():
                embed.add_field(name=self.get_command_signature(command), value=command.help or "Sin descripción", inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)