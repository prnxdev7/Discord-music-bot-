import discord
from discord.ext import commands
import yt_dlp
import asyncio

ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',
    'noplaylist': True
}
ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    async def join_vc(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("⚠️ You need to be in a voice channel first.")
            return None
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            return await channel.connect()
        return ctx.voice_client

    @commands.command()
    async def play(self, ctx, *, query):
        vc = await self.join_vc(ctx)
        if vc is None:
            return

        await ctx.send(f"🔍 Searching for: **{query}**")
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        
        if "entries" in data:
            data = data["entries"][0]

        url = data["url"]
        title = data.get("title", "Unknown")
        self.queue.append((url, title))

        if not vc.is_playing():
            await self.start_playing(ctx, vc)

    async def start_playing(self, ctx, vc):
        if len(self.queue) == 0:
            await ctx.send("✅ Queue finished.")
            return

        url, title = self.queue.pop(0)
        await ctx.send(f"🎶 Now playing: **{title}**")

        vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.start_playing(ctx, vc), self.bot.loop))

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭ Skipped to next song!")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("🛑 Stopped and left the voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))