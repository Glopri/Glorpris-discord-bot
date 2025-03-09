import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if TOKEN is None:
    raise ValueError("⚠ ERROR: Bot token is missing! Check your .env file.")

# Enable intents
intents = discord.Intents.default()
intents.message_content = True  # This is required for the bot to read messages

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello! I am your bot.')

# Run the bot
bot.run(TOKEN)
