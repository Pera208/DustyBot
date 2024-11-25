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

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load env
load_dotenv()
MQTT_BROKER_IP = os.getenv('MQTT_BROKER_IP')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')

# MQTT Config
MQTT_PORT = 1884
MQTT_TOPIC = "home/sensors/dht11"

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
        
    @discord.app_commands.command(name="humidity", description="Get dht11 sensor data")
    async def fetch_sensor_data(self, interaction: discord.Interaction) -> None:
        # Fetch latest sensor data available
        await interaction.response.defer()
        
        if self.latest_data:
            # Send an embed if data is available
            temp = self.latest_data['temperature']
            humid = self.latest_data['humidity']
            
            humid_embed = discord.Embed(title="DHT11 Sensor Data", color=discord.Color.random())
            humid_embed.set_author(name=f"Requested by {interaction.user.name}", icon_url = interaction.user.avatar)
            humid_embed.add_field(name="🌡️ Temperature", value=f"{temp}°C", inline=True)
            humid_embed.add_field(name="💧 Humidity", value=f"{humid}%", inline=True)
            
            await interaction.followup.send(embed=humid_embed)
            
        else:
            await interaction.followup.send("No data available yet")
    
    def cog_unload(self):
        # Cancel mqtt listener when cog is unloaded
        if self.mqtt_task:
            self.mqtt_task.cancel()

async def setup(client):
    await client.add_cog(Sensor(client))
