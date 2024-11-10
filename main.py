import os
import sys
import logging
from dotenv import load_dotenv
import random
import asyncio
import itertools

import discord
from discord.ext import commands, tasks

# Local file
from responses import get_response

# Load bot Token
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Configure logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', style='{')
handler.setFormatter(formatter)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

# Bot setup
intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix='?', intents=intents)

# Load cogs
async def load() -> None:
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            await client.load_extension(f'cogs.{filename[:-3]}')

# Remove help command
client.remove_command('help')

# Bot status loop
artists: list = ["Coldplay", "Avicii", "The Beatles", "C418", "Radwimps", "Whal & Dolph", "Dept", "Purpeech", "Tilly birds", "The weeknd", "Harry styles", "Yoasobi", "Bruno Mars", "25 hours", "Yew", "Polycat"]

bot_status = itertools.cycle([
    discord.Activity(type=discord.ActivityType.listening, name=f"{random.choice(artists)}"),
    discord.Game("with your feelings"),
    discord.Game("discord.py"),
    discord.Activity(type=discord.ActivityType.listening, name=f"{random.choice(artists)}"),
    discord.Game("with your mother"),
    discord.Activity(type=discord.ActivityType.watching, name="hindi python tutorial"),
    discord.Activity(type=discord.ActivityType.listening, name=f"{random.choice(artists)}"),
    discord.Activity(type=discord.ActivityType.watching, name="how to be god hacker 111"),
    discord.Game("discord.py poggers"),
    discord.Activity(type=discord.ActivityType.listening, name=f"{random.choice(artists)}"),
    discord.Activity(type=discord.ActivityType.watching, name="skibidi toilet"),
])

@tasks.loop(seconds=60)
async def change_bot_status():
    # Debug : print("Attempting to change bot status")
    await client.change_presence(activity=next(bot_status))
    # Debug : print("Cycling through bot status")

@change_bot_status.before_loop
async def before_change_bot_status():
    print("Waiting for bot to connect to change status...")
    await client.wait_until_ready()

# When bot is online
@client.event
async def on_ready():
    print(f"-- {client.user} has connected to Discord! --")
    if not change_bot_status.is_running():
        await asyncio.sleep(3)
        change_bot_status.start()
    # Check if theres a mistake with slash commands -> Here for now, will move to using slash commands
    try:
        synced_commands = await client.tree.sync()
        print(f"Synced {len(synced_commands)} commands")
    except Exception as e:
        print(f"Error with syncing application commands: {e}")

# Main entry point
async def main() -> None:

    async with client:
        await load()
        change_bot_status.start()
        await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())





# Unused old code
    # Step 6: Set up logging -> Removed for now
    # handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    # handler.setLevel(logging.INFO)
    # formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', style='{')
    # handler.setFormatter(formatter)

    # logger = logging.getLogger('discord')
    # logger.setLevel(logging.INFO)
    # logger.addHandler(handler)

    # Old run(for file without cogs) -> client.run(token=TOKEN, log_handler=handler, root_logger=True)
"""
# Step 2: Function to send message, called when some users sent a message
async def send_message(message, user_message: str) -> None:
    if not user_message:
        print('Message was empty because intents were not enabled probably')
        return
    if is_private := '?p' in user_message:
        user_message = user_message[2:]
    elif 'mention me' in user_message:
        await message.channel.send(f'Hello {message.author.mention}!')
        return
    elif 'ping' in user_message.strip():
        latency = client.latency * 1000
        await message.channel.send(f'Pong! Latency : {latency:.2f}ms')
        return
    elif user_message.strip().startswith('?shutdown'):
        if message.author.id == 853588392843018310:
            await message.channel.send("Bot shutting down...")
            sys.exit()
        else:
            await message.channel.send("Error : Unauthorized to shutdown bot")
            return

    try:
        response = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)
        
# Step 3: Send message to console when bot is started up
@client.event
async def on_ready() -> None:
    print(f'-- {client.user} has connected to Discord! --')
"""

"""
# Step 4: Handling messages
@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return

    dumlist = [853586555289206814, 803765294488616960, 1095643735603298384, 791482512773873734]
    if message.author.id in dumlist:
        await message.channel.send("ดำ ไม่อยากคุยด้วย")
        return
    elif message.author.id == 1127994079662317750:
        await message.channel.send("หวัดดีครับสุดหล่อ")
        return
    elif message.content.strip().startswith("emoji test"):
        await message.add_reaction("🤖")
        await message.channel.send("😭😭😭")
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f"[{channel}] {username}: '{user_message}'")
    await send_message(message, user_message)

    # Make it compatible with discord.ext
    await client.process_commands(message)
"""