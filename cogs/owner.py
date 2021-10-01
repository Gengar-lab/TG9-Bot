"""
Stores owner commands of Bot
"""

import json

import discord
from discord.ext import commands

# pylint: disable=bare-except, import-error
# Why Pylint why
from helpers import json_manager

with open("config.json", encoding="utf-8") as file:
    config = json.load(file)


class Owner(commands.Cog, name="owner"):
    """Owner Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shutdown", aliases=["sd", "sleep"])
    async def shutdown(self, context):
        """Make the bot shutdown"""

        if context.message.author.id in config["owners"]:
            embed = discord.Embed(
                description="Shutting down. Bye! :wave:",
                color=0x42F56C
            )
            await context.send(embed=embed)
            await self.bot.close()
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.command(name="say", aliases=["echo"])
    async def say(self, context, *, args):
        """The bot will say anything you want."""

        if context.message.author.id in config["owners"]:
            await context.send(args)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.command(name="embed")
    async def embed(self, context, *, args):
        """The bot will say anything you want, but within embeds."""

        if context.message.author.id in config["owners"]:
            embed = discord.Embed(
                description=args,
                color=0x42F56C
            )
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.group(name="blacklist")
    async def blacklist(self, context):
        """Lets you add or remove a user from not being able to use the bot."""

        if context.invoked_subcommand is None:
            with open("blacklist.json", encoding="utf-8") as infile:
                blacklist = json.load(infile)
            embed = discord.Embed(
                title=f"There are currently {len(blacklist['ids'])} blacklisted IDs",
                description=f"{', '.join(str(id) for id in blacklist['ids'])}",
                color=0x0000FF
            )
            await context.send(embed=embed)

    @blacklist.command(name="add")
    async def blacklist_add(self, context, member: discord.Member = None):
        """Lets you add a user from not being able to use the bot."""

        if context.message.author.id in config["owners"]:
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
                    await context.send(embed=embed)
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
                await context.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=("An unknown error occurred when trying to add "
                                 f"**{member.name}** to the blacklist."),
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @blacklist.command(name="remove")
    async def blacklist_remove(self, context, member: discord.Member = None):
        """Lets you remove a user from not being able to use the bot."""

        if context.message.author.id in config["owners"]:
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
                await context.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=f"**{member.name}** is not in the blacklist.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.group(name="status")
    async def status(self, context):
        """Lets you add or remove a status from a list of statuses"""

        if context.invoked_subcommand is None:
            with open("config.json", encoding="utf-8") as infile:
                body = json.load(infile)
            embed = discord.Embed(
                title=f"There are currently {len(body['statuses'])} statuses",
                description=f"{', '.join(str(id) for id in body['statuses'])}",
                color=0x0000FF
            )
            await context.send(embed=embed)

    @status.command(name="add")
    async def status_add(self, context, *, args):
        """Lets you add a status to the list of statuses"""

        if context.message.author.id in config["owners"]:
            try:
                with open("config.json", encoding="utf-8") as infile:
                    body = json.load(infile)
                if args in body['statuses']:
                    embed = discord.Embed(
                        title="Error!",
                        description=f"**{args}** is already in the statuses.",
                        color=0xE02B2B
                    )
                    await context.send(embed=embed)
                    return
                json_manager.add_status_to_config(args)
                embed = discord.Embed(
                    title="Status Added",
                    description=f"**{args}** has been successfully added to the statuses.",
                    color=0x42F56C
                )
                with open("config.json", encoding="utf-8") as infile:
                    body = json.load(infile)
                embed.set_footer(
                    text=f"There are now {len(body['statuses'])} statuses."
                )
                await context.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=("An unknown error occurred when trying to add "
                                 f"**{args}** to the statuses."),
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @status.command(name="remove")
    async def status_remove(self, context, *, args):
        """Lets you remove a status from the list of statuses"""

        if context.message.author.id in config["owners"]:
            try:
                json_manager.remove_status_from_config(args)
                embed = discord.Embed(
                    title="Status removed from statuses",
                    description=f"**{args}** has been successfully removed from the statuses.",
                    color=0x42F56C
                )
                with open("config.json", encoding="utf-8") as infile:
                    body = json.load(infile)
                embed.set_footer(
                    text=f"There are now {len(body['statuses'])} statuses."
                )
                await context.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=f"**{args}** is not in the statuses.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @status.command(name="set")
    async def status_set(self, context, *, args):
        """Lets you set the status of the bot"""

        if context.message.author.id in config["owners"]:
            try:
                await context.bot.change_presence(status=discord.Status.idle,
                                                  activity=discord.Game(args))
                embed = discord.Embed(
                    title="Status set",
                    description=f"**{args}** has been successfully set to bot.",
                    color=0x42F56C
                )
                await context.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=f"**{args}** was unable to be set.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)


def setup(bot):
    """Add Owner commands to cogs"""
    bot.add_cog(Owner(bot))
