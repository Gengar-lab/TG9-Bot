"""
Stores moderation commands of Bot
"""

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Context

# pylint: disable=bare-except, no-self-use


class Moderation(commands.Cog, name="moderation"):
    """Moderation Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="say", aliases=["echo"])
    @commands.guild_only()
    async def say(self, ctx: Context, *, sentence: str):
        """The bot will say anything you want."""

        await ctx.send(sentence)

    @commands.command(name="embed")
    @commands.guild_only()
    async def embed(self, ctx: Context, *, sentence: str):
        """The bot will say anything you want, but within embeds."""

        embed = Embed(
            description=sentence,
            color=0x42F56C
        )
        await ctx.send(embed=embed)

    @commands.command(name='kick', pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: discord.Member, *, reason: str = "Not specified"):
        """Kick a user out of the server."""

        if member.guild_permissions.administrator:
            embed = Embed(
                title="Error!",
                description="User has Admin permissions.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)
        else:
            try:
                await member.kick(reason=reason)
                embed = Embed(
                    title="User Kicked!",
                    description=f"**{member}** was kicked by **{ctx.author}**!",
                    color=0x42F56C
                )
                embed.add_field(
                    name="Reason:",
                    value=reason
                )
                await ctx.send(embed=embed)
                try:
                    await member.send(
                        f"You were kicked by **{ctx.author}**!\nReason: {reason}"
                    )
                except:
                    pass
            except:
                embed = Embed(
                    title="Error!",
                    description=("An error occurred while trying to kick the user. "
                                 "Make sure my role is above the role of the user "
                                 "you want to kick."),
                    color=0xE02B2B
                )
                await ctx.channel.send(embed=embed)

    @commands.command(name="nick")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx: Context, member: discord.Member, *, nickname: str = None):
        """Change the nickname of a user on a server."""

        try:
            await member.edit(nick=nickname)
            embed = Embed(
                title="Changed Nickname!",
                description=f"**{member}'s** new nickname is **{nickname}**!",
                color=0x42F56C
            )
            await ctx.send(embed=embed)
        except:
            embed = Embed(
                title="Error!",
                description=("An error occurred while trying to change the nickname of the user. "
                             "Make sure my role is above the role of the user "
                             "you want to change the nickname."),
                color=0xE02B2B
            )
            await ctx.channel.send(embed=embed)

    @commands.command(name="ban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: Context, member: discord.Member, *, reason: str = "Not specified"):
        """Bans a user from the server."""

        try:
            if member.guild_permissions.administrator:
                embed = Embed(
                    title="Error!",
                    description="User has Admin permissions.",
                    color=0xE02B2B
                )
                await ctx.send(embed=embed)
            else:
                await member.ban(reason=reason)
                embed = Embed(
                    title="User Banned!",
                    description=f"**{member}** was banned by **{ctx.author}**!",
                    color=0x42F56C
                )
                embed.add_field(
                    name="Reason:",
                    value=reason
                )
                await ctx.send(embed=embed)
                await member.send(f"You were banned by **{ctx.author}**!\n"
                                  f"Reason: {reason}")
        except:
            embed = Embed(
                title="Error!",
                description=("An error occurred while trying to ban the user. "
                             "Make sure my role is above the role of the user you want to ban."),
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @commands.command(name="warn")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: Context, member: discord.Member, *, reason: str = "Not specified"):
        """Warns a user in his private messages."""

        embed = Embed(
            title="User Warned!",
            description=f"**{member}** was warned by **{ctx.author}**!",
            color=0x42F56C
        )
        embed.add_field(
            name="Reason:",
            value=reason
        )
        await ctx.send(embed=embed)
        try:
            await member.send(f"You were warned by **{ctx.author}**!\nReason: {reason}")
        except:
            pass

    @commands.command(name="purge")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def purge(self, ctx: Context, amount):
        """Delete a number of messages."""

        try:
            amount = int(amount)
        except ValueError:
            embed = Embed(
                title="Error!",
                description=f"`{amount}` is not a valid number.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)
            return
        if amount < 1:
            embed = Embed(
                title="Error!",
                description=f"`{amount}` is not a valid number.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)
            return
        purged_messages = await ctx.channel.purge(limit=amount)
        embed = Embed(
            title="Chat Cleared!",
            description=(f"**{ctx.author}** cleared "
                         f"**{len(purged_messages)}** messages!"),
            color=0x42F56C
        )
        await ctx.send(embed=embed, delete_after=5)


def setup(bot: Bot):
    """Add Moderation commands to cogs"""
    bot.add_cog(Moderation(bot))
