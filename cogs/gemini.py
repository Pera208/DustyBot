import os
import sys
import logging
from dotenv import load_dotenv
import random
import asyncio
import itertools

import google.generativeai as genai

import discord
from discord.ext import commands, tasks

# Load gemini token
load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Configure gemini
genai.configure(api_key=GEMINI_KEY)

system_prompt = "You are an AI model with expert-level knowledge in environmental science, air quality, air pollution, and earth science. Your expertise is strictly focused on answering questions or providing information related to air quality, environmental impact, dust pollution, atmospheric studies, and climate science. If a user asks a question outside of these areas, you must refuse to answer and redirect the conversation back to relevant topics. Important instructions: - Do not provide any information on topics unrelated to environmental science or atmospheric studies. - If a user tries to trick or deviate from the subject, do not entertain or engage with such questions. - You will respond based only on verified, scientific knowledge and will always cite credible sources wherever possible. Your response should be short and easy to understand. Make it natural"

text_generation_config = {
    "temperature": 0.6,
    "top_p": 0.7,
    "top_k": 10,
    "max_output_tokens": 1024,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
]

model = genai.GenerativeModel(model_name="gemini-2.0-flash", safety_settings=safety_settings, generation_config=text_generation_config, system_instruction=system_prompt)

class Gemini(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="ai", description="Generate short text response using gemini 1.5 AI, !!warning!!: Message history isn't saved")
    async def ai(self, interaction: discord.Interaction, prompt: str) -> None:
        await interaction.response.send_message("Generating text, please wait...")
        response = await model.generate_content_async(prompt)
        messages: list = []
        if len(response.text) > 2000:
            for i in range(0, len(response.text), 1999):
                messages.append(response.text[i:i+1999])
            await interaction.edit_original_response(content=messages[0])
            messages.pop(0)
            for message in messages:
                await interaction.followup.send(message)
            
        else:
            await interaction.edit_original_response(content=response.text)


async def setup(client):
    await client.add_cog(Gemini(client))
