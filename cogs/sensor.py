import os
import sys
import logging
from dotenv import load_dotenv
import random
import asyncio
import itertools
import json

import discord
from discord.ext import commands, tasks
import aiohttp
from aiomqtt import Client as AsyncMqttClient

import google.generativeai as genai

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load env
load_dotenv()
MQTT_BROKER_IP = os.getenv('MQTT_BROKER_IP')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

#Configure gemini
genai.configure(api_key=GEMINI_KEY)
system_prompt = "You are an AI model with expert-level knowledge in environmental science, air quality, air pollution, and earth science. Your expertise is strictly focused on answering questions or providing information related to air quality, environmental impact, dust pollution, atmospheric studies, and climate science. If a user asks a question outside of these areas, you must refuse to answer and redirect the conversation back to relevant topics. Important instructions: - Do not provide any information on topics unrelated to environmental science or atmospheric studies. - If a user tries to trick or deviate from the subject, do not entertain or engage with such questions. - You will respond based only on verified, scientific knowledge and will always cite credible sources wherever possible. Your response should be short and easy to understand. Make it natural, You will be sent the local indoor pm1, pm2.5, pm10, temperature and humidity from an esp32 system and you should give a summary and some tips or advice or guidelines(try to focus on the pm levels rather than the temp and humid) however do not make it long, you could include some emojis too!"

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

# MQTT Config
MQTT_PORT = 1884
MQTT_TOPIC = "home/sensors"

class Sensor(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.latest_data = None
        self.mqtt_task = self.client.loop.create_task(self.mqtt_listener())
        
    async def connect_mqtt(self):
        while True:
            try:
                # Connect to mqtt broker and listen for messages
                async with AsyncMqttClient(MQTT_BROKER_IP, username=MQTT_USER, password=MQTT_PASS, port=MQTT_PORT) as mqtt_client:
                    # print("Connected to MQTT broker")
                    await mqtt_client.subscribe(MQTT_TOPIC)
                    print(f"Subscribed to {MQTT_TOPIC}")
                    # async with mqtt_client.filtered_messages(MQTT_TOPIC) as messages:
                    async for message in mqtt_client.messages:
                        # print(f"Raw message: {message}")
                        # print(f"Topic: {message.topic}, Payload: {message.payload.decode()}")
                        try:
                            self.latest_data = json.loads(message.payload.decode())
                            # print(f"Recieved MQTT data: {self.latest_data}")
                        except Exception as e:
                            print(f"Error: {e}")
            except Exception as e:
                print(f"Error connecting to MQTT broker: {e}")
                print("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
                
    async def mqtt_listener(self):
        self.client.loop.create_task(self.connect_mqtt())
        
    @discord.app_commands.command(name="sensor", description="Get local dht11 & pms7003 sensor data")
    async def fetch_sensor_data(self, interaction: discord.Interaction, aisummary: bool=True) -> None:
        # Fetch latest sensor data available
        await interaction.response.defer()
        
        if self.latest_data:
            # Send an embed if data is available
            temp = self.latest_data['temperature']
            humid = self.latest_data['humidity']
            pm1 = self.latest_data['PM1']
            pm25 = self.latest_data['PM2_5']
            pm10 = self.latest_data['PM10']
            
            color = None
            # Set embed color based on tmp
            if temp < 25:
                color = discord.Color.blue()
            elif temp < 30:
                color = discord.Color.green()
            elif temp < 35:
                color = discord.Color.orange()
            else:
                color = discord.Color.red()
            
            humid_embed = discord.Embed(title="DHT11 & PMS7003 Sensor Data", color=color)
            humid_embed.set_author(name=f"Requested by {interaction.user.name}", icon_url = interaction.user.avatar)
            humid_embed.add_field(name="🌫️ PM1", value=f"{pm1} ug/m³", inline=True)
            humid_embed.add_field(name="😷 PM2.5", value=f"{pm25} ug/m³", inline=True)
            humid_embed.add_field(name="🏭 PM10", value=f"{pm10} ug/m³", inline=True)
            humid_embed.add_field(name="🌡️ Temperature", value=f"{temp}°C", inline=True)
            humid_embed.add_field(name="💧 Humidity", value=f"{humid}%", inline=True)
            
            await interaction.followup.send(embed=humid_embed)
            
            # Ai summary
            if aisummary:
                summary_message = await interaction.followup.send("Generating AI summary, please wait...")
                response = await model.generate_content_async(f"PM1 : {pm1}, PM2.5 : {pm25}, PM10 : {pm10}")
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
            await interaction.followup.send("No data available yet")
    
    def cog_unload(self):
        # Cancel mqtt listener when cog is unloaded
        if self.mqtt_task:
            self.mqtt_task.cancel()

async def setup(client):
    await client.add_cog(Sensor(client))
