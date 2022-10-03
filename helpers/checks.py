"""Contains command checks"""

import json

from discord.ext import commands

from helpers.exceptions import UserNotOwner


def is_owner():
    """Checks if User is Owner"""

    async def predicate(ctx: commands.Context):
        with open("config.json", encoding="utf-8") as file:
            config = json.load(file)
            if ctx.author.id not in config["owners"]:
                raise UserNotOwner
        return True

    return commands.check(predicate)
