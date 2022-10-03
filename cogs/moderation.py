"""Stores moderation commands of Bot"""

import discord
from discord.ext import commands


class Moderation(commands.Cog, name="moderation"):
    """Moderation Commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="say",
                             aliases=["echo"],
                             description="The bot will say anything you want"
                             )
    @commands.guild_only()
    async def say(self, ctx, *, sentence: str):
        """The bot will say anything you want."""

        await ctx.send(sentence)

    @commands.hybrid_command(name="embed",
                             description="The bot will say anything you want in embeds"
                             )
    @commands.guild_only()
    async def embed(self, ctx, *, sentence: str):
        """The bot will say anything you want in embeds."""

        embed = discord.Embed(
            description=sentence,
            color=0x42F56C
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="warn",
                             description="Warn a user in his private messages"
                             )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Not specified"):
        """Warn a user in his private messages."""

        embed = discord.Embed(
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

    @commands.hybrid_command(name='kick',
                             pass_context=True,
                             description="Kick a user out of the server"
                             )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Not specified"):
        """Kick a user out of the server."""

        if member.guild_permissions.administrator:
            embed = discord.Embed(
                title="Error!",
                description="User has Admin permissions.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)
        else:
            try:
                await member.kick(reason=reason)
                embed = discord.Embed(
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
                embed = discord.Embed(
                    title="Error!",
                    description=("An error occurred while trying to kick the user. "
                                 "Make sure my role is above the role of the user "
                                 "you want to kick."),
                    color=0xE02B2B
                )
                await ctx.channel.send(embed=embed)

    @commands.hybrid_command(name="ban",
                             description="Ban a user from the server"
                             )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Not specified"):
        """Ban a user from the server."""

        try:
            if member.guild_permissions.administrator:
                embed = discord.Embed(
                    title="Error!",
                    description="User has Admin permissions.",
                    color=0xE02B2B
                )
                await ctx.send(embed=embed)
            else:
                await member.ban(reason=reason)
                embed = discord.Embed(
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
            embed = discord.Embed(
                title="Error!",
                description=("An error occurred while trying to ban the user. "
                             "Make sure my role is above the role of the user you want to ban."),
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="nick",
                             description="Change the nickname of a user on a server"
                             )
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nickname: str = None):
        """Change the nickname of a user on a server."""

        try:
            await member.edit(nick=nickname)
            embed = discord.Embed(
                title="Changed Nickname!",
                description=f"**{member}'s** new nickname is **{nickname}**!",
                color=0x42F56C
            )
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                title="Error!",
                description=("An error occurred while trying to change the nickname of the user. "
                             "Make sure my role is above the role of the user "
                             "you want to change the nickname."),
                color=0xE02B2B
            )
            await ctx.channel.send(embed=embed)

    @commands.hybrid_command(name="purge",
                             description="Delete a number of messages"
                             )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def purge(self, ctx, amount):
        """Delete a number of messages."""

        try:
            amount = int(amount)
        except ValueError:
            embed = discord.Embed(
                title="Error!",
                description=f"`{amount}` is not a valid number.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)
            return
        if amount < 1:
            embed = discord.Embed(
                title="Error!",
                description=f"`{amount}` is not a valid number.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)
            return
        purged_messages = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title="Chat Cleared!",
            description=(f"**{ctx.author}** cleared "
                         f"**{len(purged_messages)}** messages!"),
            color=0x42F56C
        )
        await ctx.send(embed=embed, delete_after=5)


async def setup(bot: commands.Bot):
    """Add Moderation commands to cogs"""
    await bot.add_cog(Moderation(bot))
