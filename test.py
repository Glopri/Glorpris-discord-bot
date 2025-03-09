import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
FFMPEG_PATH = "C:/FFmpeg/bin/ffmpeg.exe"  # Update this path if needed
SOUND_FILE = "sound.mp3"  # Make sure this file exists in your bot's folder

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def join(ctx):
    """Make the bot join the user's voice channel."""
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        await ctx.send(f"🔊 Joined **{channel.name}**!")
    else:
        await ctx.send("❌ You must be in a voice channel first!")

@bot.command()
async def leave(ctx):
    """Make the bot leave the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel!")
    else:
        await ctx.send("❌ I'm not in a voice channel!")

@bot.command()
async def play(ctx):
    """Make the bot play a sound file."""
    if not ctx.voice_client:
        await ctx.send("❌ I'm not in a voice channel! Use `!join` first.")
        return
    
    vc = ctx.voice_client
    if vc.is_playing():
        await ctx.send("❌ Already playing audio!")
        return

    if not os.path.exists(SOUND_FILE):
        await ctx.send("❌ Sound file not found! Make sure `sound.mp3` is in the bot folder.")
        return

    # Create audio source properly
    audio_source = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=SOUND_FILE)

    vc.play(audio_source, after=lambda e: print("✅ Finished playing sound."))
    await ctx.send(f"🎵 Now playing: `{SOUND_FILE}`")


bot.run(TOKEN)