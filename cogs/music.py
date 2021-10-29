"""
Stores music commands of Bot
"""

import itertools
import asyncio
from async_timeout import timeout
from youtube_dl import YoutubeDL

import discord
from discord import Embed, Guild
from discord.ext import commands
from discord.ext.commands import Bot, Context

# pylint: disable=too-many-instance-attributes, protected-access, no-self-use

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


class VoiceChError(Exception):
    """Custom Voice Channel error"""


class YTDLSource:
    """Create YTDL Source for playing music"""

    def __init__(self, source, *, data, requester):
        self.source = source
        self.requester = requester

        self.webpage_url = data.get("webpage_url")
        self.title = data.get("title")

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx: Context, search: str, *, loop):
        """Create source from song name"""

        loop = loop or asyncio.get_event_loop()

        data = ytdl.extract_info(f"ytsearch:{search}", download=False)

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]
            url = data["formats"][0]["url"]
            name = data["title"]

        embed = Embed(title="Added",
                      description=f"Added {name} to the Queue.",
                      color=0x42F56C)
        await ctx.send(embed=embed)
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

        return cls(source=source, data=data, requester=ctx.author)


class MusicPlayer:
    """Music player loop"""

    __slots__ = ("bot", "_guild", "_channel", "_cog",
                 "queue", "next", "current", "now_playing_msg")

    def __init__(self, ctx: Context):
        self.bot: Bot = ctx.bot
        self._guild: Guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.now_playing_msg = None  # Now playing message
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    song: YTDLSource = await self.queue.get()
            except asyncio.TimeoutError:
                embed = Embed(title="Disconnected",
                              description="Bot Disconnected due to Emptiness feeling",
                              color=0xE02B2B)
                await self._channel.send(embed=embed)
                return self.destroy(self._guild)

            self.current = song

            self._guild.voice_client.play(song.source,
                                          after=lambda _: self.bot.loop.call_soon_threadsafe(
                                              self.next.set)
                                          )
            np_text = (f"**Now Playing:** `{song.title}` requested by "
                       f"`{song.requester}`\n{song.webpage_url}")
            self.now_playing_msg = await self._channel.send(np_text)
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            song.source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.now_playing_msg.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild: Guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog, name="music"):
    """Music Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild: Guild):
        """Cleanup player of guild where bot has stopped playing music"""

        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx: Context):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: Context, *, url: str):
        """Play Music"""

        try:
            await self.join(ctx)
            player = self.get_player(ctx)

            source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop)

            await player.queue.put(source)

        except VoiceChError:
            return

    async def join(self, ctx: Context):
        """Join Music Channel"""

        if ctx.author.voice is None:
            embed = Embed(description="Join a voice channel first!",
                          color=0xE02B2B)
            await ctx.send(embed=embed)
            raise VoiceChError
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command(name="pause", aliases=["stop"])
    async def pause(self, ctx: Context):
        """Pause Music"""

        if ctx.voice_client.is_paused():
            return
        ctx.voice_client.pause()
        embed = Embed(description="Song paused",
                      colour=0xF59E42)
        await ctx.send(embed=embed)

    @commands.command(name="resume")
    async def resume(self, ctx: Context):
        """Resume Music"""

        if ctx.voice_client.is_playing():
            return
        ctx.voice_client.resume()
        embed = Embed(description="Song resumed",
                      colour=0xF59E42)
        await ctx.send(embed=embed)

    @commands.command(name="disconnect", aliases=["leave", "dc"])
    async def disconnect(self, ctx: Context):
        """Disconnect from voice channel"""

        vc_client = ctx.voice_client
        if not vc_client or not vc_client.is_connected():
            embed = Embed(description="Bot already disconnected",
                          color=0x42F56C)
            return await ctx.send(embed=embed)

        await ctx.voice_client.disconnect()
        embed = Embed(description="Bot disconnected",
                      color=0x42F56C)
        await self.cleanup(ctx.guild)
        await ctx.send(embed=embed)

    @commands.command(name="queue", aliases=["q", "playlist"])
    async def queue_info(self, ctx: Context):
        """Diaplays Song Queue"""

        vc_client = ctx.voice_client

        if not vc_client or not vc_client.is_connected():
            return await ctx.send("I am not currently connected to voice!")

        player = self.get_player(ctx)
        if player.queue.empty():
            embed = Embed(title="Empty Queue",
                          description="There are currently no more queued songs.",
                          color=0xFF8C00)
            return await ctx.send(embed=embed)

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = "\n".join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = Embed(
            title=f"Upcoming - Next {len(upcoming)}", description=fmt, color=0xFF8C00)

        await ctx.send(embed=embed)

    @commands.command(name="playing", aliases=["np", "current", "now_playing"])
    async def now_playing(self, ctx: Context):
        """Shows current playing song"""

        vc_client = ctx.voice_client

        if not vc_client or not vc_client.is_connected():
            return await ctx.send("I am not currently connected to voice!")

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send("I am not currently playing anything!")

        try:
            # Remove our previous now_playing message.
            await player.now_playing_msg.delete()
        except discord.HTTPException:
            pass

        player.now_playing_msg = await ctx.send(f"**Now Playing:** `{player.current.title}` "
                                                f"requested by `{player.current.requester}`"
                                                f"\n{player.current.webpage_url}")


def setup(bot: Bot):
    """Add Music commands to cogs"""
    bot.add_cog(Music(bot))
