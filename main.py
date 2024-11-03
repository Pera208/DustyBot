import os
from dotenv import load_dotenv
import discord
# Local file
from responses import get_response

# Step 0: Load bot Token
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Step 1: Bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Step 2: Message functionality
async def send_message(message, user_message: str) -> None:
    if not user_message:
        print('Message was empty because intents were not enabled probably')
        return
    if is_private := '?p' in user_message:
        user_message = user_message[2:]

    try:
        response = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# Step 3: Handling bot startup
@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')

# Step 4: Handling messages
@client.event
async def on_message(message) -> None:
    if message.author == client.user:
        return

    dumlist = [853586555289206814, 803765294488616960, 1095643735603298384, 791482512773873734]
    if message.author.id in dumlist:
        await message.channel.send("ดำ ไม่อยากคุยด้วย")
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f"[{channel}] {username}: '{user_message}'")
    await send_message(message, user_message)

# Step 5: Main entry point
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()