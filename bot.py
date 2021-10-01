"""
------------------------------------------------------------------------------
Copyright © Krypton 2021 - https://github.com/kkrypt0nn
Description:
This is a template to create your own discord bot in python.

Version: 2.8
------------------------------------------------------------------------------
Copyright © Xoti-lab 2021 - https://github.com/Xoti-lab

Version: 1.1
------------------------------------------------------------------------------
"""

import json
import os
import platform
import random
import sys

from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot

# pylint: disable=broad-except

load_dotenv()
TOKEN = os.environ.get("TOKEN")

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json", encoding="utf-8") as file:
        config = json.load(file)


intents = discord.Intents.default()

bot = Bot(command_prefix=config["bot_prefix"], intents=intents)


@bot.event
async def on_ready():
    """The code in this event is executed when the bot is ready"""

    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()


@tasks.loop(minutes=60.0)
async def status_task():
    """Setup the game status task of the bot"""

    with open("config.json", encoding="utf-8") as infile:
        body = json.load(infile)
        status = random.choice(body["statuses"])
        await bot.change_presence(status=discord.Status.idle,
                                  activity=discord.Game(status)
                                  )


# Removes the default help command of discord.py to be able to create our custom help command.
bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


@bot.event
async def on_message(message):
    """The code in this event is executed every time someone sends a message"""

    # Ignores if a command is being executed by a bot or by the bot itself
    if message.author == bot.user or message.author.bot:
        return
    # Ignores if a command is being executed by a blacklisted user
    with open("blacklist.json", encoding="utf-8") as infile:
        blacklist = json.load(infile)
    if message.author.id in blacklist["ids"]:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_completion(ctx):
    """The code in this event is executed every time a command has been *successfully* executed"""

    full_command_name = ctx.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    print(f"Executed {executed_command} command in {ctx.guild.name} (ID: {ctx.message.guild.id})"
          f" by {ctx.message.author} (ID: {ctx.message.author.id})")


@bot.event
async def on_command_error(context, error):
    """The code in this event is executed every time a valid commands catches an error"""

    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="Hey, please slow down!",
            description="You can use this command again in "
                        f"{f'{round(hours)} hours' if round(hours) > 0 else ''} "
                        f"{f'{round(minutes)} minutes' if round(minutes) > 0 else ''} "
                        f"{f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description=f"You are missing the permission `,{error.missing_perms}"
                        "` to execute this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await context.send(embed=embed)
    raise error


# Run the bot with the token
bot.run(TOKEN)
