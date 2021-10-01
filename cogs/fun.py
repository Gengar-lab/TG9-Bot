"""
Stores fun commands of Bot
"""

import asyncio
import random

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import BucketType

# pylint: disable=no-member


class Fun(commands.Cog, name="fun"):
    """Fun Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dailyfact")
    @commands.cooldown(1, 86400, BucketType.user)
    async def dailyfact(self, context):
        """Get a daily fact, command can only be ran once every day per user."""

        # This will prevent your bot from stopping everything when doing a web request
        async with aiohttp.ClientSession() as session:
            web_link = "https://uselessfacts.jsph.pl/random.json?language=en"
            async with session.get(web_link) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(
                        description=data["text"],
                        color=0xD75BF4
                    )
                    await context.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B
                    )
                    await context.send(embed=embed)
                    # We need to reset the cool down since the user didn't got his daily fact.
                    self.dailyfact.reset_cooldown(context)

    @commands.command(name="rps")
    async def rock_paper_scissors(self, context):
        """Play Rock, Paper, Scissors"""

        reactions = {
            "🪨": 0,
            "🧻": 1,
            "✂": 2
        }
        embed = discord.Embed(
            title="Please choose",
            color=0xF59E42
        )
        embed.set_author(name=context.author.display_name,
                         icon_url=context.author.avatar_url)
        choose_message = await context.send(embed=embed)
        for emoji in reactions:
            await choose_message.add_reaction(emoji)

        def check(reaction, user):
            return user == context.message.author and str(reaction) in reactions

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)
            if not user:
                return

            user_choice_emote = reaction.emoji
            user_choice_index = reactions[user_choice_emote]

            bot_choice_emote = random.choice(list(reactions.keys()))
            bot_choice_index = reactions[bot_choice_emote]

            result_embed = discord.Embed(color=0x42F56C)
            result_embed.set_author(
                name=context.author.display_name, icon_url=context.author.avatar_url)
            await choose_message.clear_reactions()

            if user_choice_index == bot_choice_index:
                result_embed.description = ("**That's a draw!**\n"
                                            "You've chosen {user_choice_emote} "
                                            "and I've chosen {bot_choice_emote}.")
                result_embed.colour = 0xF59E42
            elif user_choice_index == 0 and bot_choice_index == 2:
                result_embed.description = ("**You won!**\n"
                                            "You've chosen {user_choice_emote} "
                                            "and I've chosen {bot_choice_emote}.")
                result_embed.colour = 0x42F56C
            elif user_choice_index == 1 and bot_choice_index == 0:
                result_embed.description = ("**You won!**\n"
                                            "You've chosen {user_choice_emote} "
                                            "and I've chosen {bot_choice_emote}.")
                result_embed.colour = 0x42F56C
            elif user_choice_index == 2 and bot_choice_index == 1:
                result_embed.description = ("**You won!**\n"
                                            "You've chosen {user_choice_emote} "
                                            "and I've chosen {bot_choice_emote}.")
                result_embed.colour = 0x42F56C
            else:
                result_embed.description = ("**I won!**\n"
                                            "You've chosen {user_choice_emote} "
                                            "and I've chosen {bot_choice_emote}.")
                result_embed.colour = 0xE02B2B
                await choose_message.add_reaction("🇱")
            await choose_message.edit(embed=result_embed)
        except asyncio.exceptions.TimeoutError:
            await choose_message.clear_reactions()
            timeout_embed = discord.Embed(title="Too late", color=0xE02B2B)
            timeout_embed.set_author(
                name=context.author.display_name, icon_url=context.author.avatar_url)
            await choose_message.edit(embed=timeout_embed)


def setup(bot):
    """Add Fun commands to cogs"""
    bot.add_cog(Fun(bot))
