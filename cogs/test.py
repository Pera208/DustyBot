import os
import sys
import random

import discord
from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Simple hello command
    @commands.command(aliases=['hi', 'hey'])
    async def hello(self, ctx) -> None:
        greetings: list = ['Yo', 'Hello World', 'Hey', 'Hi', 'Sup ma bro', 'I\'m a tired discord bot thats speaking with']
        await ctx.send(f"{random.choice(greetings)} {ctx.author.name}")

    # Simple mention command
    @commands.command(aliases=['yo', 'sup'])
    async def mention(self, ctx) -> None:
        await ctx.send(f'Sup ma sigma {ctx.author.mention}!')

    # Slash command for hello
    @discord.app_commands.command(name="hello", description="Say hello")
    async def slashhello(self, interaction: discord.Interaction, mention: bool=False) -> None:
        greetings: list = ['Yo', 'Hello World', 'Hey', 'Hi', 'Sup ma bro', 'I\'m a tired discord bot thats speaking with']
        if mention:
            await interaction.response.send_message(f"{random.choice(greetings)} {interaction.user.mention}")
        else:
            await interaction.response.send_message(f"{random.choice(greetings)} {interaction.user.name}")

# Setup
async def setup(client):
    await client.add_cog(Test(client))