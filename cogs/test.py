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

# Setup
async def setup(client):
    await client.add_cog(Test(client))