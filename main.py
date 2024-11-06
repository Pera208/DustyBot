import os
import sys
import logging
from dotenv import load_dotenv
import random

import discord
from discord.ext import commands

# Local file
from responses import get_response

# Step 0: Load bot Token
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Step 1: Bot setup
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='?', intents=intents)

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
"""

# Step 3: Send message to console when bot is started up
@client.event
async def on_ready() -> None:
    print(f'-- {client.user} has connected to Discord! --')

# Commands

@client.command(aliases=['hi', 'hey'])
async def hello(ctx) -> None:
    await ctx.send("Hello World!")

@client.command(aliases=['yo', 'sup'])
async def mention(ctx) -> None:
    await ctx.send(f'Sup ma sigma {ctx.author.mention}!')

# Sending embed
@client.command(aliases=['embed', 'embedtest'])
async def sendembed(ctx) -> None:
    embedmsg = discord.Embed(title="Embed Test very cool", description='I guess this is a cool embed with random color', color=discord.Color.random())
    embedmsg.set_thumbnail(url=ctx.guild.icon)
    embedmsg.add_field(name="Name of field", value="Value of field", inline=False)
    embedmsg.set_image(url='https://images-ext-1.discordapp.net/external/_JXBi1vDnXe2dGMQfzN1MMC5Hq08eEh72Fb0fEhP1fU/%3Fsize%3D160%26name%3Dtricked/https/media.discordapp.net/stickers/865660032896598026.png?format=webp&quality=lossless')
    embedmsg.set_footer(text="wowow footer test", icon_url=ctx.author.avatar)
    await ctx.send(embed=embedmsg)

# Ping command using embed
@client.command(aliases=['latency'])
async def ping(ctx) -> None:
    latency = client.latency * 1000
    embedcolor = None
    if latency < 100:
        embedcolor = discord.Color.green()
    elif latency < 300:
        embedcolor = discord.Color.orange()
    else:
        embedcolor = discord.Color.red()
    ping_embed = discord.Embed(title="Pong!", description=f'Latency: **{latency:.2f}** ms', color=embedcolor)
    ping_embed.set_footer(text="Requested by " + ctx.author.name, icon_url=ctx.author.avatar)
    await ctx.send(embed=ping_embed)

# Shutdown bot command
@client.command(aliases=['exit', 'stop'])
async def shutdown(ctx) -> None:
    if ctx.author.id == 853588392843018310 or ctx.author.id == 853586555289206814:
        await ctx.send("Bot shutting down...")
        sys.exit()
    else:
        await ctx.send("Error: No permission to shutdown bot")
        return

"""
# Step 4: Handling messages
@client.event
async def on_message(message) -> None:
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
# Step 5: Main entry point
def main() -> None:

    # Step 6: Set up logging
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

    client.run(token=TOKEN, log_handler=handler, root_logger=True)

if __name__ == '__main__':
    main()