"""
Stores help command of Bot
"""

import json

import discord
from discord.ext import commands

with open("config.json", encoding="utf-8") as file:
    config = json.load(file)


class Help(commands.Cog, name="help"):
    """Help Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, context):
        """List all commands from every Cog the bot has loaded."""

        prefix = config["bot_prefix"]
        if not isinstance(prefix, str):
            prefix = prefix[0]
        embed = discord.Embed(
            title="Help", description="List of available commands:",
            color=0x42F56C
        )
        for i in ["help", "general", "music", "fun", "moderation"]:
            cog = self.bot.get_cog(i.lower())
            bot_commands = cog.get_commands()
            command_list = [command.name for command in bot_commands]
            command_description = [command.help for command in bot_commands]
            help_text = "\n".join(
                        f"{prefix}{n} - {h}" for n, h in zip(command_list, command_description))
            embed.add_field(name=i.capitalize(),
                            value=f"```{help_text}```", inline=False)
        await context.send(embed=embed)


def setup(bot):
    """Add Help commands to cogs"""
    bot.add_cog(Help(bot))
