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
intents.message_content = True
intents.guilds = True
intents.voice_states = True  # Ensure the bot can track voice state changes

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to track which user the bot should follow
tracked_users = {}

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.command()
async def test(ctx):
    await ctx.send('The bot is awake and responding.')

@bot.command()
async def annoy(ctx, member: discord.Member):
    """Tracks a user and makes the bot join their VC when they do."""
    await ctx.send(f"✅ I am now annoying {member.display_name}.")
    
    guild = ctx.guild
    print(f"Tracking request received for: {member.display_name} ({member.id})")

    # Check if the bot can find the member
    if member is None:
        return

    # Check if the user is already in a voice channel
    if member.voice and member.voice.channel:
        voice_channel = member.voice.channel
        vc = await voice_channel.connect()
        bot.tracked_vc = vc  # Store VC connection
        tracked_users[member.id] = voice_channel.id  # Keep tracking them
    else:
        tracked_users[member.id] = ctx.channel.id  # Store text channel for notifications
    
    print(f"Tracked users: {tracked_users}")


@bot.event
async def on_voice_state_update(member, before, after):
    if member.id in tracked_users:
        text_channel = bot.get_channel(tracked_users[member.id])  # Get stored text channel

        if after.channel is not None:  # User joined VC
            vc = await after.channel.connect()
            bot.tracked_vc = vc  # Store VC connection

        elif before.channel is not None and after.channel is None:  # User left VC
            if bot.tracked_vc:
                await bot.tracked_vc.disconnect()
                bot.tracked_vc = None
            # ❗ Don't remove `member.id` from `tracked_users` so bot remembers them!

@bot.command()
async def stop_annoying(ctx, member: discord.Member):
    if member.id in tracked_users:
        del tracked_users[member.id]
        await ctx.send(f"🚫 No longer annoying {member.display_name}.")


# Run the bot
bot.run(TOKEN)
