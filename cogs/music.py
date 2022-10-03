"""Stores music commands of Bot"""

import itertools

import discord
from discord.ext import commands

from helpers.music_player import MusicPlayer, YTDLSource
from helpers.exceptions import VoiceChError

class Music(commands.Cog, name="music"):
    """Music Commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild: discord.Guild):
        """Cleanup player of guild where bot has stopped playing music"""

        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""

        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    async def join(self, ctx):
        """Join Music Channel"""

        if ctx.author.voice is None:
            embed = discord.Embed(description="Join a voice channel first!",
                                  color=0xE02B2B)
            await ctx.send(embed=embed)
            raise VoiceChError
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.hybrid_command(name="play",
                             aliases=["p"],
                             description="Play Music"
                             )
    @commands.guild_only()
    async def play(self, ctx, *, url: str):
        """Play Music"""

        try:
            await self.join(ctx)
            player = self.get_player(ctx)

            source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop)

            await player.queue.put(source)

        except VoiceChError:
            return

    @commands.hybrid_command(name="pause",
                             aliases=["stop"],
                             description="Pause Music"
                             )
    @commands.guild_only()
    async def pause(self, ctx):
        """Pause Music"""

        if ctx.voice_client.is_paused():
            return
        ctx.voice_client.pause()
        embed = discord.Embed(description="Song paused",
                              colour=0xF59E42)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="resume",
                             description="Resume Music"
                             )
    @commands.guild_only()
    async def resume(self, ctx):
        """Resume Music"""

        if ctx.voice_client.is_playing():
            return
        ctx.voice_client.resume()
        embed = discord.Embed(description="Song resumed",
                              colour=0xF59E42)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="disconnect",
                             aliases=["leave", "dc"],
                             description="Disconnect bot from voice channel"
                             )
    @commands.guild_only()
    async def disconnect(self, ctx):
        """Disconnect bot from voice channel"""

        vc_client = ctx.voice_client
        if not vc_client or not vc_client.is_connected():
            embed = discord.Embed(description="Bot already disconnected",
                                  color=0x42F56C)
            return await ctx.send(embed=embed)

        await ctx.voice_client.disconnect()
        embed = discord.Embed(description="Bot disconnected",
                              color=0x42F56C)
        await self.cleanup(ctx.guild)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="queue",
                             aliases=["q", "playlist"],
                             description="Displays Song Queue"
                             )
    @commands.guild_only()
    async def queue_info(self, ctx):
        """Displays Song Queue"""

        vc_client = ctx.voice_client

        if not vc_client or not vc_client.is_connected():
            return await ctx.send("I am not currently connected to voice!")

        player = self.get_player(ctx)
        if player.queue.empty():
            embed = discord.Embed(title="Empty Queue",
                                  description="There are currently no more queued songs.",
                                  color=0xFF8C00)
            return await ctx.send(embed=embed)

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = "\n".join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(
            title=f"Upcoming - Next {len(upcoming)}", description=fmt, color=0xFF8C00)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="playing",
                             aliases=["np", "current", "now_playing"],
                             description="Shows current playing song"
                             )
    @commands.guild_only()
    async def now_playing(self, ctx):
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


async def setup(bot: commands.Bot):
    """Add Music commands to cogs"""
    await bot.add_cog(Music(bot))
