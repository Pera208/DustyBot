import os
import sys
import logging
from dotenv import load_dotenv
import random
import asyncio
import itertools
import datetime

import google.generativeai as genai

import discord
from discord.ext import commands, tasks
import aiohttp

# Load env
load_dotenv()
IQAIR_API_KEY = os.getenv('AIRVISUAL_API_KEY')
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Configure gemini
genai.configure(api_key=GEMINI_KEY)

system_prompt = "You are an AI model with expert-level knowledge in environmental science, air quality, air pollution, and earth science. Your expertise is strictly focused on answering questions or providing information related to air quality, environmental impact, dust pollution, atmospheric studies, and climate science. If a user asks a question outside of these areas, you must refuse to answer and redirect the conversation back to relevant topics. Important instructions: - Do not provide any information on topics unrelated to environmental science or atmospheric studies. - If a user tries to trick or deviate from the subject, do not entertain or engage with such questions. - You will respond based only on verified, scientific knowledge and will always cite credible sources wherever possible. Your response should be short and easy to understand. Make it natural, You will be get sent the current air quality index and you should give a summary and some tips or advice or guidelines however do not make it long, you could include some emojis too!"

text_generation_config = {
    "temperature": 0.6,
    "top_p": 0.8,
    "top_k": 30,
    "max_output_tokens": 1024,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash", safety_settings=safety_settings, generation_config=text_generation_config, system_instruction=system_prompt)

class Iqair(commands.Cog):
    def __init__ (self, client):
        self.client = client
        
    @discord.app_commands.command(name="airquality", description="Get air quality data of a city")
    async def fetch_aqi(self, interaction: discord.Interaction, country: str, state_or_province: str, city: str="none", aisummary: bool=True) -> None:
        city = state_or_province if city == "none" else city
        base_url = 'https://api.airvisual.com/v2/city'
        async with aiohttp.ClientSession() as session:
            params = {
                'city': city,
                'state': state_or_province,
                'country': country,
                'key': IQAIR_API_KEY
            }
            async with session.get(base_url, params=params) as response:
                await interaction.response.defer()
                data = await response.json()
                print(data)
                
                # If info is found
                if data['status'] == 'success':
                    # Get data from response
                    aqi = data['data']['current']['pollution']['aqius']
                    mainus = data['data']['current']['pollution']['mainus']
                    
                    # Match case for main pollutant
                    match mainus:
                        case "p1":
                            mainus = "PM10"
                        case "p2":
                            mainus = "PM2.5"
                        case "o3":
                            mainus = "Ozone"
                        case "n2":
                            mainus = "Nitrogen dioxide"
                        case "s2":
                            mainus = "Sulfur dioxide"
                        case "co":
                            mainus = "Carbon monoxide"
                            
                    # Embed color based on aqi
                    embedcolor = None
                    if aqi < 50:
                        embedcolor = discord.Color.green()
                    elif aqi < 100:
                        embedcolor = discord.Color.yellow()
                    elif aqi < 150:
                        embedcolor = discord.Color.orange()
                    elif aqi < 200:
                        embedcolor = discord.Color.red()
                    elif aqi < 300:
                        embedcolor = discord.Color.purple()
                    else:
                        embedcolor = discord.Color.from_str("#7e0023")
                        
                    # Create embed
                    aqi_embed = discord.Embed(title=f"Current air quality data for {city}, {country}", color=embedcolor)
                    aqi_embed.set_author(name=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
                    
                    aqi_embed.add_field(name="🏭 Air Quality Index", value=aqi, inline=True)
                    aqi_embed.add_field(name="🌫️ Main Pollutant", value=mainus, inline=True)
                    
                    await interaction.followup.send(embed=aqi_embed)
                    
                    # If user requested for summary
                    if aisummary == True:
                        summary_message = await interaction.followup.send("Generating AI summary, please wait...")
                        response = await model.generate_content_async(f"Aqi : {aqi}")
                        messages: list = []
                        # If message exceeds 2000 characters
                        if len(response.text) > 2000:
                            for i in range(0, len(response.text), 1999):
                                messages.append(response.text[i:i+1999])
                            await summary_message.edit(content=messages[0])
                            messages.pop(0)
                            for message in messages:
                                await interaction.followup.send(message)
                        # If message does not exceed 2000 characters
                        else:
                            await summary_message.edit(content=response.text)
                    
                else:
                    await interaction.followup.send(f"Fetching aqi failed : {data['data']['message']}")
                
    
async def setup(client):
    await client.add_cog(Iqair(client))
