"""Stores owner commands of Bot"""

import json

import discord
from discord.ext import commands

from helpers import json_manager, checks


class Owner(commands.Cog, name="owner"):
    """Owner Commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="shutdown", aliases=["sd", "sleep"])
    @checks.is_owner()
    async def shutdown(self, ctx):
        """Make the bot shutdown"""

        embed = discord.Embed(
            description="Shutting down. Bye! :wave:",
            color=0x42F56C
        )
        await ctx.send(embed=embed)
        await self.bot.close()

    @commands.group(name="blacklist")
    @checks.is_owner()
    async def blacklist(self, ctx):
        """Lets you add or remove a user from not being able to use the bot."""

        if ctx.invoked_subcommand is None:
            with open("blacklist.json", encoding="utf-8") as infile:
                blacklist = json.load(infile)
            embed = discord.Embed(
                title=f"There are currently {len(blacklist['ids'])} blacklisted IDs",
                description=f"{', '.join(str(id) for id in blacklist['ids'])}",
                color=0x0000FF
            )
            await ctx.send(embed=embed)

    @blacklist.command(name="add")
    @checks.is_owner()
    async def blacklist_add(self, ctx, member: discord.Member = None):
        """Lets you add a user from not being able to use the bot."""

        user_id = member.id
        try:
            with open("blacklist.json", encoding="utf-8") as infile:
                blacklist = json.load(infile)
            if user_id in blacklist['ids']:
                embed = discord.Embed(
                    title="Error!",
                    description=f"**{member.name}** is already in the blacklist.",
                    color=0xE02B2B
                )
                await ctx.send(embed=embed)
                return
            json_manager.add_user_to_blacklist(user_id)
            embed = discord.Embed(
                title="User Blacklisted",
                description=f"**{member.name}** has been successfully added to the blacklist",
                color=0x42F56C
            )
            with open("blacklist.json", encoding="utf-8") as infile:
                blacklist = json.load(infile)
            embed.set_footer(
                text=f"There are now {len(blacklist['ids'])} users in the blacklist"
            )
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                title="Error!",
                description=("An unknown error occurred when trying to add "
                             f"**{member.name}** to the blacklist."),
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @blacklist.command(name="remove")
    @checks.is_owner()
    async def blacklist_remove(self, ctx, member: discord.Member = None):
        """Lets you remove a user from not being able to use the bot."""

        user_id = member.id
        try:
            json_manager.remove_user_from_blacklist(user_id)
            embed = discord.Embed(
                title="User removed from blacklist",
                description=(f"**{member.name}** has been successfully "
                             "removed from the blacklist"),
                color=0x42F56C
            )
            with open("blacklist.json", encoding="utf-8") as infile:
                blacklist = json.load(infile)
            embed.set_footer(
                text=f"There are now {len(blacklist['ids'])} users in the blacklist"
            )
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                title="Error!",
                description=f"**{member.name}** is not in the blacklist.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @commands.group(name="status")
    @checks.is_owner()
    async def status(self, ctx):
        """Lets you add or remove a status from a list of statuses"""

        if ctx.invoked_subcommand is None:

            with open("config.json", encoding="utf-8") as infile:
                body = json.load(infile)
            embed = discord.Embed(
                title=f"There are currently {len(body['statuses'])} statuses",
                description=f"{', '.join(str(id) for id in body['statuses'])}",
                color=0x0000FF
            )
            await ctx.send(embed=embed)

    @status.command(name="add")
    @checks.is_owner()
    async def status_add(self, ctx, *, sentence: str):
        """Lets you add a status to the list of statuses"""

        try:
            with open("config.json", encoding="utf-8") as infile:
                body = json.load(infile)
            if sentence in body['statuses']:
                embed = discord.Embed(
                    title="Error!",
                    description=f"**{sentence}** is already in the statuses.",
                    color=0xE02B2B
                )
                await ctx.send(embed=embed)
                return
            json_manager.add_status_to_config(sentence)
            embed = discord.Embed(
                title="Status Added",
                description=f"**{sentence}** has been successfully added to the statuses.",
                color=0x42F56C
            )
            with open("config.json", encoding="utf-8") as infile:
                body = json.load(infile)
            embed.set_footer(
                text=f"There are now {len(body['statuses'])} statuses."
            )
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                title="Error!",
                description=("An unknown error occurred when trying to add "
                             f"**{sentence}** to the statuses."),
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @status.command(name="remove")
    @checks.is_owner()
    async def status_remove(self, ctx, *, sentence: str):
        """Lets you remove a status from the list of statuses"""

        try:
            json_manager.remove_status_from_config(sentence)
            embed = discord.Embed(
                title="Status removed from statuses",
                description=f"**{sentence}** has been successfully removed from the statuses.",
                color=0x42F56C
            )
            with open("config.json", encoding="utf-8") as infile:
                body = json.load(infile)
            embed.set_footer(
                text=f"There are now {len(body['statuses'])} statuses."
            )
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                title="Error!",
                description=f"**{sentence}** is not in the statuses.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @status.command(name="set")
    @checks.is_owner()
    async def status_set(self, ctx, *, sentence: str):
        """Lets you set the status of the bot"""

        try:
            await ctx.bot.change_presence(status=discord.Status.idle,
                                          activity=discord.Game(sentence))
            embed = discord.Embed(
                title="Status set",
                description=f"**{sentence}** has been successfully set to bot.",
                color=0x42F56C
            )
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                title="Error!",
                description=f"**{sentence}** was unable to be set.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Add Owner commands to cogs"""
    await bot.add_cog(Owner(bot))
