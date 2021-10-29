"""
Stores general commands of Bot
"""

import json
from platform import python_version
import random

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Context

# pylint: disable=no-self-use

BOT_VERSION = "1.2v"

with open("config.json", encoding="utf-8") as file:
    config = json.load(file)


class General(commands.Cog, name="general"):
    """General Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="info", aliases=["botinfo"])
    async def info(self, ctx: Context):
        """Get some useful (or not) information about the bot."""

        embed = Embed(
            description="Made by Gengar",
            color=0x42F56C
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="TheGriffin999",
            inline=True
        )
        embed.add_field(
            name="Bot Version:",
            value=BOT_VERSION,
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{python_version()}",
            inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"{config['bot_prefix']}",
            inline=False
        )
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    @commands.guild_only()
    async def serverinfo(self, ctx: Context):
        """Get some useful (or not) information about the server."""

        server = ctx.message.guild
        roles = [x.name for x in server.roles]
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = Embed(
            title="**Server Name:**",
            description=f"{server}",
            color=0x42F56C
        )
        embed.set_thumbnail(
            url=server.icon_url
        )
        embed.add_field(
            name="Owner",
            value=f"{server.owner}\n{server.owner.id}"
        )
        embed.add_field(
            name="Server ID",
            value=server.id
        )
        embed.add_field(
            name="Member Count",
            value=server.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{channels}"
        )
        embed.add_field(
            name=f"Roles ({role_length})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {time}"
        )
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx: Context):
        """Check if the bot is alive."""

        embed = Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x42F56C
        )
        await ctx.send(embed=embed)

    @commands.command(name="server", aliases=["support", "supportserver"])
    async def server(self, ctx: Context):
        """Get the invite link of the discord server of the bot for some support."""

        server_link = "https://discord.gg/Z4vEvCC8Vf"
        embed = Embed(
            description=f"Join the support server for the bot by clicking [here]({server_link}).",
            color=0xD75BF4
        )
        try:
            await ctx.author.send(embed=embed)
            await ctx.send("I sent you a private message!")
        except discord.Forbidden:
            await ctx.send(embed=embed)

    @commands.command(name="poll")
    @commands.guild_only()
    async def poll(self, ctx: Context, *, title: str):
        """Create a poll where members can vote."""

        embed = Embed(
            title="A new poll has been created!",
            description=f"{title}",
            color=0x42F56C
        )
        embed.set_footer(
            text=f"Poll created by: {ctx.author} • React to vote!")
        embed_message = await ctx.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

    @commands.command(name="8ball")
    async def eight_ball(self, ctx: Context, *, question: str):
        """Ask any question to the bot."""

        answers = ["It is certain.", "It is decidedly so.", "You may rely on it.",
                   "Without a doubt.", "Yes - definitely.", "As I see, yes.", "Most likely.",
                   "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.",
                   "Ask again later.", "Better not tell you now.", "Cannot predict now.",
                   "Concentrate and ask again later.", "Don't count on it.", "My reply is no.",
                   "My sources say no.", "Outlook not so good.", "Very doubtful."]
        embed = Embed(
            title="**My Answer:**",
            description=f"{answers[random.randint(0, len(answers))]}",
            color=0x42F56C
        )
        embed.set_footer(text=f"The question was: {question}")
        await ctx.send(embed=embed)


def setup(bot: Bot):
    """Add General commands to cogs"""
    bot.add_cog(General(bot))
