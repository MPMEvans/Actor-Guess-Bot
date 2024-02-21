### This is a discord bot that will show a picture of an actor or actress and the user will have to guess their name
### The output embed box will be only visible to the person playing, and will show the picture and what they are known for
### Data will be taken from IMDBs top 100 actors/actresses list which will be refreshed every 30 days

### The bot will be activated with !play followed by an integer, with the integer determining how many actors the user wants to guess
### The integer will be used to select a random amount of actors from a list of 100

import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import web_scraper

load_dotenv()

# reading CSV file of actors if one exists, otherwise the web_scraper module will be ran in order to generate one
path = os.path.join(os.path.dirname(__file__), 'birthday_dict.json')
file_exists = os.path.isfile(path)
if file_exists == False:
    web_scraper()

# Getting the token and channel that the bot will type to
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_TOKEN'))

# Creating the bot and setting the prefix
bot = commands.Bot(command_prefix = "!", intents = discord.Intents.all())

# Getting the bot to print a message when it is active
@bot.event
async def on_ready():
    print("Hello! I am ready!")

# Initialising the bot
bot.run(TOKEN)