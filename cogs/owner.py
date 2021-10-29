"""
Stores owner commands of Bot
"""

import json

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Context

# pylint: disable=bare-except, no-self-use, import-error
# Why Pylint why
from helpers import json_manager

with open("config.json", encoding="utf-8") as file:
    config = json.load(file)


class Owner(commands.Cog, name="owner"):
    """Owner Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def is_owner(self, ctx: Context):
        """Checks if Message sender is Owner"""

        if ctx.author.id in config["owners"]:
            return True

        embed = Embed(
            title="Error!",
            description="You don't have the permission to use this command.",
            color=0xE02B2B
        )
        await ctx.send(embed=embed)
        return False

    @commands.command(name="shutdown", aliases=["sd", "sleep"])
    async def shutdown(self, ctx: Context):
        """Make the bot shutdown"""

        if not self.is_owner(ctx):
            return

        embed = Embed(
            description="Shutting down. Bye! :wave:",
            color=0x42F56C
        )
        await ctx.send(embed=embed)
        await self.bot.close()

    @commands.group(name="blacklist")
    async def blacklist(self, ctx: Context):
        """Lets you add or remove a user from not being able to use the bot."""

        if ctx.invoked_subcommand is None:
            if not self.is_owner(ctx):
                return
            with open("blacklist.json", encoding="utf-8") as infile:
                blacklist = json.load(infile)
            embed = Embed(
                title=f"There are currently {len(blacklist['ids'])} blacklisted IDs",
                description=f"{', '.join(str(id) for id in blacklist['ids'])}",
                color=0x0000FF
            )
            await ctx.send(embed=embed)

    @blacklist.command(name="add")
    async def blacklist_add(self, ctx: Context, member: discord.Member = None):
        """Lets you add a user from not being able to use the bot."""

        if not self.is_owner(ctx):
            return

        user_id = member.id
        try:
            with open("blacklist.json", encoding="utf-8") as infile:
                blacklist = json.load(infile)
            if user_id in blacklist['ids']:
                embed = Embed(
                    title="Error!",
                    description=f"**{member.name}** is already in the blacklist.",
                    color=0xE02B2B
                )
                await ctx.send(embed=embed)
                return
            json_manager.add_user_to_blacklist(user_id)
            embed = Embed(
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
            embed = Embed(
                title="Error!",
                description=("An unknown error occurred when trying to add "
                             f"**{member.name}** to the blacklist."),
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @blacklist.command(name="remove")
    async def blacklist_remove(self, ctx: Context, member: discord.Member = None):
        """Lets you remove a user from not being able to use the bot."""

        if not self.is_owner(ctx):
            return

        user_id = member.id
        try:
            json_manager.remove_user_from_blacklist(user_id)
            embed = Embed(
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
            embed = Embed(
                title="Error!",
                description=f"**{member.name}** is not in the blacklist.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @commands.group(name="status")
    async def status(self, ctx: Context):
        """Lets you add or remove a status from a list of statuses"""

        if ctx.invoked_subcommand is None:
            if not self.is_owner(ctx):
                return
            with open("config.json", encoding="utf-8") as infile:
                body = json.load(infile)
            embed = Embed(
                title=f"There are currently {len(body['statuses'])} statuses",
                description=f"{', '.join(str(id) for id in body['statuses'])}",
                color=0x0000FF
            )
            await ctx.send(embed=embed)

    @status.command(name="add")
    async def status_add(self, ctx: Context, *, sentence: str):
        """Lets you add a status to the list of statuses"""

        if not self.is_owner(ctx):
            return

        try:
            with open("config.json", encoding="utf-8") as infile:
                body = json.load(infile)
            if sentence in body['statuses']:
                embed = Embed(
                    title="Error!",
                    description=f"**{sentence}** is already in the statuses.",
                    color=0xE02B2B
                )
                await ctx.send(embed=embed)
                return
            json_manager.add_status_to_config(sentence)
            embed = Embed(
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
            embed = Embed(
                title="Error!",
                description=("An unknown error occurred when trying to add "
                             f"**{sentence}** to the statuses."),
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @status.command(name="remove")
    async def status_remove(self, ctx: Context, *, sentence: str):
        """Lets you remove a status from the list of statuses"""

        if not self.is_owner(ctx):
            return

        try:
            json_manager.remove_status_from_config(sentence)
            embed = Embed(
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
            embed = Embed(
                title="Error!",
                description=f"**{sentence}** is not in the statuses.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)

    @status.command(name="set")
    async def status_set(self, ctx: Context, *, sentence: str):
        """Lets you set the status of the bot"""

        if not self.is_owner(ctx):
            return

        try:
            await ctx.bot.change_presence(status=discord.Status.idle,
                                          activity=discord.Game(sentence))
            embed = Embed(
                title="Status set",
                description=f"**{sentence}** has been successfully set to bot.",
                color=0x42F56C
            )
            await ctx.send(embed=embed)
        except:
            embed = Embed(
                title="Error!",
                description=f"**{sentence}** was unable to be set.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)


def setup(bot: Bot):
    """Add Owner commands to cogs"""
    bot.add_cog(Owner(bot))
