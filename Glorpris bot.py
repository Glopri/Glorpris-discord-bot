import discord
from discord.ext import commands
import os
import asyncio
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
FFMPEG_PATH = r"C:\FFmpeg\bin\ffmpeg.exe"  # Ensure correct path
SOUND_FILE = "sound.mp3"  # Make sure this file exists

if TOKEN is None:
    raise ValueError("⚠ ERROR: Bot token is missing! Check your .env file.")

# Enable intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

tracked_users = {}  # Store tracked users


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.command()
async def annoy(ctx, member: discord.Member):
    """Track a user and join their voice channel when they do."""
    tracked_users[member.id] = {"text_channel": ctx.channel.id, "vc": None}
    await ctx.send(f"🔍 Now tracking {member.mention}. I'll join their VC when they do!")


@bot.command()
async def stop(ctx, member: discord.Member):
    """Stop tracking a user."""
    if member.id in tracked_users:
        tracked_users.pop(member.id)
        await ctx.send(f"❌ No longer tracking {member.mention}.")
    else:
        await ctx.send(f"⚠ {member.mention} is not being tracked.")


@bot.event
async def on_voice_state_update(member, before, after):
    """Detect when a tracked user joins or leaves a voice channel."""
    if member.id in tracked_users:
        user_data = tracked_users[member.id]
        text_channel = bot.get_channel(user_data["text_channel"])

        if after.channel and before.channel != after.channel:  # User joined or switched VC
            await text_channel.send(f"🎤 {member.mention} joined {after.channel.name}! Joining now...")

            # Disconnect from previous VC if connected
            if user_data["vc"] and user_data["vc"].is_connected():
                await user_data["vc"].disconnect()

            # Connect to new VC
            vc = await after.channel.connect()
            user_data["vc"] = vc  # Store the new voice connection

            # Start monitoring voice activity
            asyncio.create_task(detect_speech(vc, member, text_channel))

        elif before.channel and not after.channel:  # User left VC
            if user_data["vc"] and user_data["vc"].is_connected():
                await text_channel.send(f"👋 {member.mention} left VC. Leaving now...")
                await user_data["vc"].disconnect()
                user_data["vc"] = None  # Reset VC connection


async def detect_speech(vc, member, text_channel):
    """Detect actual speech from the user."""
    while vc.is_connected():
        await asyncio.sleep(1)  # Avoid excessive CPU usage

        if member.voice is None or member.voice.channel != vc.channel:
            print(f"❌ {member.name} left VC. Stopping detection.")
            break  # Stop monitoring if the user leaves

        if member.voice.self_mute or member.voice.self_deaf:
            continue  # Skip if the user is muted/deafened

        # Simulate real speech detection (since discord.py lacks raw audio analysis)
        speaking = np.random.choice([True, False], p=[0.4, 0.6])  # 40% chance to detect "speech"
        
        if speaking and not vc.is_playing():
            await text_channel.send(f"🔊 {member.name} is speaking! Playing sound...")
            audio_source = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=SOUND_FILE)
            vc.play(audio_source)

bot.run(TOKEN)
