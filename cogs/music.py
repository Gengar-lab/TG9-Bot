"""
Stores music commands of Bot
"""

import json
import itertools
import os
import sys

import asyncio
import discord
from discord.ext import commands
from async_timeout import timeout
from youtube_dl import YoutubeDL

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}
YDL_OPTIONS = {
    "format": "bestaudio",
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
}

ytdl = YoutubeDL(YDL_OPTIONS)

if not os.path.isfile("config.json"):
    sys.exit('"config.json" not found! Please add it and try again.')
else:
    with open("config.json", encoding="utf-8") as file:
        config = json.load(file)


class VoiceChError(Exception):
    """Custom Voice Channel error"""


class YTDLSource:

    def __init__(self, source, *, data, requester):
        self.source = source
        self.requester = requester

        self.webpage_url = data.get("webpage_url")
        self.title = data.get("title")

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, context, search: str, *, loop):
        loop = loop or asyncio.get_event_loop()

        data = ytdl.extract_info(f"ytsearch:{search}", download=False)

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]
            url = data["formats"][0]["url"]
            name = data["title"]

        embed = discord.Embed(title="Added",
                              description=f"Added {name} to the Queue.",
                              color=0x42F56C)
        await context.send(embed=embed)
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

        return cls(source=source, data=data, requester=context.author)


class MusicPlayer:

    __slots__ = ("bot", "_guild", "_channel", "_cog",
                 "queue", "next", "current", "np")

    def __init__(self, context):
        self.bot = context.bot
        self._guild = context.guild
        self._channel = context.channel
        self._cog = context.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.current = None

        context.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                embed=discord.Embed(title="Disconnected",
                description="Bot Disconnected due to Emptiness feeling",
                color=0xE02B2B)
                await self._channel.send(embed=embed)
                return self.destroy(self._guild)

            self.current = source

            self._guild.voice_client.play(source.source,
                                          after=lambda _: self.bot.loop.call_soon_threadsafe(
                                              self.next.set)
                                          )
            self.np = await self._channel.send(f"**Now Playing:** `{source.title}` requested by "
                                               f"`{source.requester}`\n{source.webpage_url}")
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog, name="music"):
    """Music Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, context):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[context.guild.id]
        except KeyError:
            player = MusicPlayer(context)
            self.players[context.guild.id] = player

        return player

    @commands.command(name="play", aliases=["p"])
    async def play(self, context, *, url):
        """Play Music"""

        try:
            await self.join(context)
            player = self.get_player(context)

            source = await YTDLSource.create_source(context, url, loop=self.bot.loop)

            await player.queue.put(source)

        except VoiceChError:
            return

    async def join(self, context):
        """Join Music Channel"""

        if context.author.voice is None:
            embed = discord.Embed(description="Join a voice channel first!",
                                  color=0xE02B2B)
            await context.send(embed=embed)
            raise VoiceChError
        voice_channel = context.author.voice.channel
        if context.voice_client is None:
            await voice_channel.connect()
        else:
            await context.voice_client.move_to(voice_channel)

    @commands.command(name="pause", aliases=["stop"])
    async def pause(self, context):
        """Pause Music"""

        if context.voice_client.is_paused():
            return
        context.voice_client.pause()
        embed = discord.Embed(description="Song paused",
                              colour=0xF59E42)
        await context.send(embed=embed)

    @commands.command(name="resume")
    async def resume(self, context):
        """Resume Music"""

        if context.voice_client.is_playing():
            return
        context.voice_client.resume()
        embed = discord.Embed(description="Song resumed",
                              colour=0xF59E42)
        await context.send(embed=embed)

    @commands.command(name="disconnect", aliases=["leave", "dc"])
    async def disconnect(self, context):
        """Disconnect from voice channel"""

        vc = context.voice_client
        if not vc or not vc.is_connected():
            embed = discord.Embed(description="Bot already disconnected",
                                  color=0x42F56C)
            return await context.send(embed=embed)

        await context.voice_client.disconnect()
        embed = discord.Embed(description="Bot disconnected",
                              color=0x42F56C)
        await self.cleanup(context.guild)
        await context.send(embed=embed)

    @commands.command(name="queue", aliases=["q", "playlist"])
    async def queue_info(self, context):
        """Diaplays Song Queue"""

        vc = context.voice_client

        if not vc or not vc.is_connected():
            return await context.send("I am not currently connected to voice!", delete_after=20)

        player = self.get_player(context)
        if player.queue.empty():
            embed = discord.Embed(title="Empty Queue",
            description = "There are currently no more queued songs.",
            color=0xFF8C00)
            return await context.send(embed=embed)

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = "\n".join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(
            title=f"Upcoming - Next {len(upcoming)}", description=fmt, color=0xFF8C00)

        await context.send(embed=embed)

    @commands.command(name="playing", aliases=["np", "current", "now_playing"])
    async def now_playing(self, context):
        """Shows current playing song"""

        vc = context.voice_client

        if not vc or not vc.is_connected():
            return await context.send("I am not currently connected to voice!", delete_after=20)

        player = self.get_player(context)
        if not player.current:
            return await context.send("I am not currently playing anything!")

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await context.send(f"**Now Playing:** `{player.current.title}` "
                                       f"requested by `{player.current.requester}`"
                                       f"\n{player.current.webpage_url}")


def setup(bot):
    """Add Music commands to cogs"""
    bot.add_cog(Music(bot))
