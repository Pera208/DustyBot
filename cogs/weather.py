import os
import sys
import logging
from dotenv import load_dotenv
import random
import asyncio
import itertools

import discord
from discord.ext import commands, tasks
import aiohttp

# Load weather api
load_dotenv()
WEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

class Weather(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Send weather data
    @discord.app_commands.command(name="weather", description="Get weather information of a city")
    async def fetch_weather(self, interaction: discord.Interaction, city: str) -> None:
            base_url = 'https://api.openweathermap.org/data/2.5/weather'
            async with aiohttp.ClientSession() as session:
                params = {
                    'q': city,
                    'appid': WEATHER_API_KEY,
                    'units': 'metric'
                }
                async with session.get(base_url, params=params) as response: 
                    await interaction.response.send_message("Fetching weather data...")
                    if response.status == 200:
                        data = await response.json()
                        print(data)
                        weather_embed = discord.Embed(title=f"Weather data for {city}, {data['sys']['country']}", color=discord.Color.random())
                        weather_embed.set_author(name=f"Requested by {interaction.user.name}", icon_url = interaction.user.avatar)
                        weather_embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}.png")

                        weather_description = data['weather'][0]['description']
                        temperature = data['main']['temp']
                        humidity = data['main']['humidity']
                        feels_like = data['main']['feels_like']

                        weather_embed.add_field(name="⛅ Weather", value=weather_description, inline=True)
                        weather_embed.add_field(name="🌡️ Temperature", value=f"{temperature}°C", inline=True)
                        weather_embed.add_field(name="🤒 Feels like", value=f"{feels_like}°C", inline=True)
                        weather_embed.add_field(name="💧 Humidity", value=f"{humidity}%", inline=True)
                        weather_embed.add_field(name="🌬️ Wind speed", value=f"{data['wind']['speed']} m/s", inline=True)
                        weather_embed.add_field(name="👁️ Visibility", value=f"{data['visibility'] / 1000} km", inline=True)

                        await interaction.edit_original_response(content="Done fetching!", embed=weather_embed)

                    else:
                        await interaction.edit_original_response(content=f"Could not retrieve weather data for {city}.")

async def setup(client):
    await client.add_cog(Weather(client))