import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from ffmpeg_downloader import download_ffmpeg

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

# Download ffmpeg if missing (for Render free plan)
if not os.path.isfile("ffmpeg"):
    print("Downloading ffmpeg...")
    download_ffmpeg("ffmpeg", os.getcwd())

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Load music cog
initial_extensions = ["cogs.music"]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

for extension in initial_extensions:
    bot.load_extension(extension)

bot.run(TOKEN)