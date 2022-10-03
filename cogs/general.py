"""Stores general commands of Bot"""

import random
from platform import python_version

import discord
from discord.ext import commands


BOT_VERSION = "1.3v"


class General(commands.Cog, name="general"):
    """General Commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="info",
                             aliases=["botinfo"],
                             description="Get info about Bot"
                             )
    async def info(self, ctx):
        """Get some useful (or not) information about the bot."""

        embed = discord.Embed(
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
            value=f"{self.bot.config['bot_prefix']}",
            inline=False
        )
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo",
                             description="Get info about Server"
                             )
    @commands.guild_only()
    async def serverinfo(self, ctx):
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

        embed = discord.Embed(
            title="**Server Name:**",
            description=f"{server}",
            color=0x42F56C
        )
        embed.set_thumbnail(
            url=server.icon.url
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

    @commands.hybrid_command(name="ping",
                             description="Get Bot ping"
                             )
    async def ping(self, ctx):
        """Check if the bot is alive."""

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x42F56C
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="server",
                             aliases=["support", "supportserver"],
                             description="Get support Server"
                             )
    async def server(self, ctx):
        """Get the invite link of the discord server of the bot for some support."""

        server_link = "https://discord.gg/Z4vEvCC8Vf"
        embed = discord.Embed(
            description=f"Join the support server for the bot by clicking [here]({server_link}).",
            color=0xD75BF4
        )
        try:
            await ctx.author.send(embed=embed)
            await ctx.send("I sent you a private message!")
        except discord.Forbidden:
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="poll",
                             description="Generate a poll"
                             )
    @commands.guild_only()
    async def poll(self, ctx, *, title: str):
        """Create a poll where members can vote."""

        embed = discord.Embed(
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

    @commands.hybrid_command(name="8ball",
                             descripton="Ask any question to the bot"
                             )
    async def eight_ball(self, ctx, *, question: str):
        """Ask any question to the bot."""

        answers = ["It is certain.", "It is decidedly so.", "You may rely on it.",
                   "Without a doubt.", "Yes - definitely.", "As I see, yes.", "Most likely.",
                   "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.",
                   "Ask again later.", "Better not tell you now.", "Cannot predict now.",
                   "Concentrate and ask again later.", "Don't count on it.", "My reply is no.",
                   "My sources say no.", "Outlook not so good.", "Very doubtful."]
        embed = discord.Embed(
            title="**My Answer:**",
            description=f"{answers[random.randint(0, len(answers))]}",
            color=0x42F56C
        )
        embed.set_footer(text=f"The question was: {question}")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Add General commands to cogs"""
    await bot.add_cog(General(bot))
