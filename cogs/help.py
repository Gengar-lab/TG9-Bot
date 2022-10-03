"""Stores help command of Bot"""

import discord
from discord.ext import commands


class Help(commands.Cog, name="help"):
    """Help Commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="help",
                             description="Get list of all commands"
                             )
    async def help(self, ctx):
        """List all commands from every Cog the bot has loaded."""

        prefix = self.bot.config["bot_prefix"]
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
            embed.add_field(name=f"{i.capitalize()}",
                            value=f"```{help_text}```", inline=False)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Add Help commands to cogs"""
    await bot.add_cog(Help(bot))
