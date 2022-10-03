"""Contains Music Player"""

import asyncio
from async_timeout import timeout

import discord
from discord.ext import commands
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
    async def create_source(cls, ctx, search: str, *, loop):
        """Create source from song name"""

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
        await ctx.send(embed=embed)
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

        return cls(source=source, data=data, requester=ctx.author)


class MusicPlayer:
    """Music player loop"""

    __slots__ = ("bot", "_guild", "_channel", "_cog",
                 "queue", "next", "current", "now_playing_msg")

    def __init__(self, ctx):
        self.bot: commands.Bot = ctx.bot
        self._guild: discord.Guild = ctx.guild
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
                embed = discord.Embed(title="Disconnected",
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

    def destroy(self, guild: discord.Guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))
