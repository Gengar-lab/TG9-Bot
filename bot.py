"""
------------------------------------------------------------------------------
Copyright © Gengar-lab 2021 - https://github.com/Gengar-lab

Version: 1.3v
------------------------------------------------------------------------------
"""

import json
import os
import platform
import random

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from helpers import exceptions

# Get configuration
with open("config.json", encoding="utf-8") as file:
    config = json.load(file)

# Get token of bot
load_dotenv()
TOKEN = os.environ.get("TOKEN")

# Set intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config["bot_prefix"]), intents=intents)

# Remove the default help command of discord.py
bot.remove_command("help")
bot.config = config


@bot.event
async def on_ready():
    """This is executed when the bot is ready"""

    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()


@bot.event
async def setup_hook():
    """Load our modules when the bot is run"""

    for infile in os.listdir("./cogs"):
        if infile.endswith(".py"):
            extension = infile[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:  # If module fails to load, let us know the error
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")
    # await bot.tree.sync()


@tasks.loop(minutes=60.0)  # Change status after 60 minutes
async def status_task():
    """Setup the game status task of the bot"""

    with open("config.json", encoding="utf-8") as infile:
        body = json.load(infile)
        status = random.choice(body["statuses"])
        await bot.change_presence(status=discord.Status.idle,
                                  activity=discord.Game(status))


@bot.event
async def on_message(message: discord.Message):
    """This is executed every time when someone sends a message"""

    # Ignore if a command is being executed by a bot or by the bot itself
    if message.author == bot.user or message.author.bot:
        return
    # Ignore if a command is being executed by a blacklisted user
    with open("blacklist.json", encoding="utf-8") as infile:
        blacklist = json.load(infile)
    if message.author.id in blacklist["ids"]:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_completion(ctx: commands.Context):
    """This is executed every time a command has been successfully executed"""

    full_command_name = ctx.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    print(f"Executed {executed_command} command in {ctx.guild.name} (ID: {ctx.message.guild.id})"
          f" by {ctx.message.author} (ID: {ctx.message.author.id})")


@bot.event
async def on_command_error(ctx: commands.Context, error):
    """This is executed every time a valid command catches an error"""

    if isinstance(error, commands.MissingRequiredArgument):
        args = ""
        args = [args.join(i) for i in str(error).split("_")]
        embed = discord.Embed(
            title="Error!",
            description=args.strip().capitalize(),
            color=0xE02B2B
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description=f"You are missing the permission `,{error.missing_perms}"
                        "` to execute this command!",
            color=0xE02B2B
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        err = str(error.args).split(',')[0]
        print(f"Unknown command {err} in {ctx.guild.name} (ID: {ctx.message.guild.id})"
              f" by {ctx.message.author} (ID: {ctx.message.author.id})")

    elif isinstance(error, commands.CommandOnCooldown):
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
        await ctx.send(embed=embed)
    elif isinstance(error, exceptions.UserNotOwner):
        embed = discord.Embed(
            title="Error!",
            description="You don't have the permission to use this command.",
            color=0xE02B2B
        )
        await ctx.send(embed=embed)
    elif isinstance(error, exceptions.VoiceChError):
        print(error.description)
    else:
        raise error

if __name__ == "__main__":
    bot.run(TOKEN)  # Run the bot with the token
