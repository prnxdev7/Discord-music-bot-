import discord
from discord.ext import commands
import os
import toml
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load config from toml (fallback)
def load_config(path="./config.toml"):
    if os.path.exists(path):
        return toml.load(path)
    return {}

# Load environment variables
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", "!")

# If not provided in env, fallback to config.toml
config = load_config()
if not TOKEN:
    TOKEN = config.get("token")
if not PREFIX:
    PREFIX = config.get("prefix", "!")

# Safety check
if not TOKEN:
    raise ValueError("❌ No bot TOKEN found! Please set it in Render env or config.toml")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

# Bot setup
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Events
@bot.event
async def on_ready():
    logging.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="🎶 Music Bot"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Unknown command. Use `!help` to see available commands.")
    else:
        logging.error(f"Error: {error}")
        await ctx.send(f"⚠️ An error occurred: `{error}`")

# Example ping command
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Bot is alive.")

# Load cogs dynamically
async def load_cogs():
    for folder in ["cogs"]:
        for filename in os.listdir(folder):
            if filename.endswith(".py"):
                await bot.load_extension(f"{folder}.{filename[:-3]}")
                logging.info(f"🔌 Loaded cog: {filename}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())