"""Stores fun commands of Bot"""

import json
import random
import asyncio
import aiohttp

import discord
from discord.ext import commands

with open("config.json", encoding="utf-8") as file:
    config = json.load(file)


class Fun(commands.Cog, name="fun"):
    """Fun Commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="dailyfact",
                             description="Sends a fact"
                             )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def dailyfact(self, ctx):
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
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B
                    )
                    await ctx.send(embed=embed)
                    # We need to reset the cool down since the user didn't got his daily fact.
                    self.dailyfact.reset_cooldown(ctx)

    @commands.hybrid_command(name="rps",
                             description="Play Rock, Paper, Scissors"
                             )
    async def rock_paper_scissors(self, ctx):
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
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.display_avatar.url)
        choose_message = await ctx.send(embed=embed)
        for emoji in reactions:
            await choose_message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction) in reactions

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)
            if not user:
                return

            user_choice_emote = reaction.emoji
            user_choice_index = reactions[user_choice_emote]

            bot_choice_emote = random.choice(list(reactions.keys()))
            bot_choice_index = reactions[bot_choice_emote]

            result_embed = discord.Embed(color=0x42F56C)
            result_embed.set_author(name=ctx.author.display_name,
                                    icon_url=ctx.author.display_avatar.url)
            await choose_message.clear_reactions()

            if user_choice_index == bot_choice_index:
                result_embed.description = ("**That's a draw!**"
                                            f"\nYou've chosen {user_choice_emote}"
                                            f" and I've chosen {bot_choice_emote}.")
                result_embed.colour = 0xF59E42
            elif ((user_choice_index == 0 and bot_choice_index == 2) or
                  (user_choice_index == 1 and bot_choice_index == 0) or
                  (user_choice_index == 2 and bot_choice_index == 1)):
                result_embed.description = ("**You won!**"
                                            f"\nYou've chosen {user_choice_emote}"
                                            f" and I've chosen {bot_choice_emote}.")
                result_embed.colour = 0x42F56C
            else:
                result_embed.description = ("**I won!**"
                                            f"\nYou've chosen {user_choice_emote}"
                                            f" and I've chosen {bot_choice_emote}.")
                result_embed.colour = 0xE02B2B
                await choose_message.add_reaction("🇱")

            await choose_message.edit(embed=result_embed)
        except asyncio.exceptions.TimeoutError:
            await choose_message.clear_reactions()
            timeout_embed = discord.Embed(title="Too late",
                                          color=0xE02B2B
                                          )
            timeout_embed.set_author(name=ctx.author.display_name,
                                     icon_url=ctx.author.display_avatar.url)
            await choose_message.edit(embed=timeout_embed)


async def setup(bot: commands.Bot):
    """Add Fun commands to cogs"""
    await bot.add_cog(Fun(bot))
