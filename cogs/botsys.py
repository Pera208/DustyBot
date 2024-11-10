import os
import sys
import asyncio

import discord
from discord.ext import commands

from main import change_bot_status

# Cog for bot system commands, and some tests

class botsys(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Ping command with slash command
    @discord.app_commands.command(name="ping", description="Get bot latency in ms")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency = self.client.latency * 1000
        embedcolor = None
        if latency < 100:
            embedcolor = discord.Color.green()
        elif latency < 300:
            embedcolor = discord.Color.orange()
        else:
            embedcolor = discord.Color.red()
        ping_embed = discord.Embed(title="Pong!", description=f'Latency: **{latency:.2f}** ms', color=embedcolor)
        ping_embed.set_footer(text="Requested by " + interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=ping_embed)

    @discord.app_commands.command(name="shutdown", description="Shutdown the bot")
    async def shutdown(self, interaction: discord.Interaction) -> None:
        if interaction.user.id == 853588392843018310:
            print("Bot is shutting down...")
            await interaction.response.send_message("Bot shutting down...")
            change_bot_status.cancel()
            await self.client.close()
        else:
            await interaction.response.send_message("Error: No permission to shutdown bot", ephemeral=True)
            await asyncio.sleep(7)
            await interaction.edit_original_response(content="Deleting this message...", embed=None)
            await asyncio.sleep(3)
            await interaction.delete_original_response()

    # Shutdown bot command, checking for permissions
    #@commands.command(aliases=['exit', 'stop'])
    #async def shutdown(self, ctx) -> None:
    #    if ctx.author.id == 853588392843018310 or ctx.author.id == 853586555289206814:
     #       print("Bot is shutting down...")
      #      await ctx.send("Bot shutting down...")
      #      change_bot_status.cancel()
       #     await self.client.close()
        #else:
            #await ctx.send("Error: No permission to shutdown bot")
           # return
            

    # Sending embed
    @commands.command(aliases=['embed', 'embedtest'])
    async def sendembed(self, ctx) -> None:
        embedmsg = discord.Embed(title="Embed Test very cool", description='I guess this is a cool embed with random color', color=discord.Color.random())
        embedmsg.set_thumbnail(url=ctx.guild.icon)
        embedmsg.add_field(name="Name of field", value="Value of field", inline=False)
        embedmsg.set_image(url='https://images-ext-1.discordapp.net/external/_JXBi1vDnXe2dGMQfzN1MMC5Hq08eEh72Fb0fEhP1fU/%3Fsize%3D160%26name%3Dtricked/https/media.discordapp.net/stickers/865660032896598026.png?format=webp&quality=lossless')
        embedmsg.set_footer(text="wowow footer test", icon_url=ctx.author.avatar)
        await ctx.send(embed=embedmsg)

async def setup(client):
    await client.add_cog(botsys(client))