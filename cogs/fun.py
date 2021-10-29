"""
Stores fun commands of Bot
"""

import random
import asyncio
import aiohttp

from discord import Embed
from discord.ext import commands
from discord.ext.commands import BucketType, Bot, Context

# pylint: disable=no-member, too-many-boolean-expressions


class Fun(commands.Cog, name="fun"):
    """Fun Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="dailyfact")
    @commands.cooldown(1, 86400, BucketType.user)
    async def dailyfact(self, ctx: Context):
        """Get a daily fact, command can only be ran once every day per user."""

        # This will prevent your bot from stopping everything when doing a web request
        async with aiohttp.ClientSession() as session:
            web_link = "https://uselessfacts.jsph.pl/random.json?language=en"
            async with session.get(web_link) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = Embed(
                        description=data["text"],
                        color=0xD75BF4
                    )
                    await ctx.send(embed=embed)
                else:
                    embed = Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B
                    )
                    await ctx.send(embed=embed)
                    # We need to reset the cool down since the user didn't got his daily fact.
                    self.dailyfact.reset_cooldown(ctx)

    @commands.command(name="rps")
    async def rock_paper_scissors(self, ctx: Context):
        """Play Rock, Paper, Scissors"""

        reactions = {
            "🪨": 0,
            "🧻": 1,
            "✂": 2
        }
        embed = Embed(
            title="Please choose",
            color=0xF59E42
        )
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
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

            result_embed = Embed(color=0x42F56C)
            result_embed.set_author(name=ctx.author.display_name,
                                    icon_url=ctx.author.avatar_url)
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
            timeout_embed = Embed(title="Too late",
                                  color=0xE02B2B
                                  )
            timeout_embed.set_author(name=ctx.author.display_name,
                                     icon_url=ctx.author.avatar_url)
            await choose_message.edit(embed=timeout_embed)


def setup(bot: Bot):
    """Add Fun commands to cogs"""
    bot.add_cog(Fun(bot))
