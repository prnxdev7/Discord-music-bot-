import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import random

# 🔑 Environment Variables
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

# 🚀 Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

queues = {}
volumes = {}

# ===================
# HELPERS
# ===================
def create_embed(title, description="", color=0x1DB954):
    """Creates a styled embed"""
    return discord.Embed(title=title, description=description, color=color)

def play_next(ctx):
    if queues[ctx.guild.id]:
        url, title = queues[ctx.guild.id].pop(0)
        play_song(ctx, url, title)
    else:
        # Autoplay random music when queue is empty 🎶
        suggestions = [
            "Alan Walker Faded", "Imagine Dragons Believer",
            "Billie Eilish Bad Guy", "Drake God's Plan",
            "Eminem Rap God", "Shape of You Ed Sheeran"
        ]
        choice = random.choice(suggestions)
        asyncio.run_coroutine_threadsafe(ctx.send(embed=create_embed("🎵 Autoplay", f"Now auto-playing: **{choice}**")), bot.loop)
        asyncio.run_coroutine_threadsafe(play(ctx, search=choice), bot.loop)

def play_song(ctx, url, title):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    ydl_opts = {'format': 'bestaudio'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
    voice.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: play_next(ctx))
    asyncio.run_coroutine_threadsafe(ctx.send(embed=create_embed("▶️ Now Playing", f"**{title}**")), bot.loop)


# ===================
# BOT EVENTS
# ===================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}play <song>"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=create_embed("❌ Error", "That command doesn’t exist. Type `!help`"))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=create_embed("⚠️ Missing Argument", str(error)))
    else:
        await ctx.send(embed=create_embed("⚠️ Error", f"Something went wrong: `{error}`"))
        raise error


# ===================
# MUSIC COMMANDS
# ===================
@bot.command()
async def join(ctx):
    """Join the user's voice channel"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(embed=create_embed("✅ Joined", f"Connected to **{channel}**"))
    else:
        await ctx.send(embed=create_embed("❌ Error", "You must be in a voice channel!"))

@bot.command()
async def play(ctx, *, search: str):
    """Play a song by name or URL"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        await join(ctx)
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {'format': 'bestaudio', 'noplaylist': 'True'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        url = info['url']
        title = info['title']

    if ctx.guild.id in queues and voice.is_playing():
        queues[ctx.guild.id].append((url, title))
        await ctx.send(embed=create_embed("🎶 Added to Queue", f"**{title}**"))
    else:
        queues[ctx.guild.id] = []
        play_song(ctx, url, title)

@bot.command()
async def skip(ctx):
    """Skip the current song"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
        await ctx.send(embed=create_embed("⏭ Skipped", "Skipped current song"))
    else:
        await ctx.send(embed=create_embed("❌ Error", "Nothing is playing."))

@bot.command()
async def stop(ctx):
    """Stop music & clear queue"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice:
        queues[ctx.guild.id] = []
        voice.stop()
        await ctx.send(embed=create_embed("⏹ Stopped", "Music stopped and queue cleared."))

@bot.command()
async def leave(ctx):
    """Bot leaves VC"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice:
        await voice.disconnect()
        await ctx.send(embed=create_embed("👋 Left", "Disconnected from voice channel."))

@bot.command()
async def pause(ctx):
    """Pause music"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        await ctx.send(embed=create_embed("⏸ Paused", "Music paused."))
    else:
        await ctx.send(embed=create_embed("❌ Error", "No music to pause."))

@bot.command()
async def resume(ctx):
    """Resume music"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        await ctx.send(embed=create_embed("▶️ Resumed", "Music resumed."))
    else:
        await ctx.send(embed=create_embed("❌ Error", "No paused music to resume."))

@bot.command()
async def queue(ctx):
    """Show queue"""
    if ctx.guild.id not in queues or not queues[ctx.guild.id]:
        await ctx.send(embed=create_embed("📜 Queue", "No songs in queue."))
    else:
        qlist = "\n".join([f"{i+1}. {title}" for i, (_, title) in enumerate(queues[ctx.guild.id])])
        await ctx.send(embed=create_embed("📜 Current Queue", qlist))

@bot.command()
async def nowplaying(ctx):
    """Show now playing"""
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        await ctx.send(embed=create_embed("🎵 Now Playing", "Check above ⬆️"))
    else:
        await ctx.send(embed=create_embed("❌ Error", "Nothing is playing."))


# ===================
# HELP COMMAND
# ===================
@bot.command()
async def help(ctx):
    embed = create_embed("🎶 Music Bot Help")
    embed.add_field(name="▶️ Play", value=f"`{PREFIX}play <song>` - Play music", inline=False)
    embed.add_field(name="⏸ Pause / ▶️ Resume", value=f"`{PREFIX}pause` / `{PREFIX}resume`", inline=False)
    embed.add_field(name="⏭ Skip / ⏹ Stop", value=f"`{PREFIX}skip` / `{PREFIX}stop`", inline=False)
    embed.add_field(name="📜 Queue / 🎵 Now Playing", value=f"`{PREFIX}queue` / `{PREFIX}nowplaying`", inline=False)
    embed.add_field(name="👋 Leave", value=f"`{PREFIX}leave` - Disconnect bot", inline=False)
    await ctx.send(embed=embed)


# ===================
# RUN BOT
# ===================
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("❌ DISCORD_TOKEN environment variable not set!")
    bot.run(TOKEN)