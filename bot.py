### This is a discord bot that will show a picture of an actor or actress and the user will have to guess their name
### The output embed box will be only visible to the person playing, and will show the picture and what they are known for
### Data will be taken from IMDBs top 100 actors/actresses list which will be refreshed every 30 days

### The bot will be activated with !play followed by an integer, with the integer determining how many actors the user wants to guess
### The integer will be used to select a random amount of actors from a list of 100

import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
import web_scraper
import pandas as pd

load_dotenv()

# reading CSV file of actors if one exists, otherwise the web_scraper module will be ran in order to generate one
path = os.path.join(os.path.dirname(__file__), 'actors.csv')
file_exists = os.path.isfile(path)
if file_exists == True:
    actors_df = pd.read_csv('actors.csv')
else:
    web_scraper.main()
    actors_df = pd.read_csv('actors.csv')

# Setting a task to repeatedly run a function to check if there are any NaNs in the actors csv file and run the 
# get_picture_error function from web_scraper to replace them.
# The minutes parameter is how many minutes it waits to run the function, the count is how many times it will repeat
# the task. The task will execute once when the program is initially ran and then waits the set number of minutes to repeat.
minutes_in_day = 10
@tasks.loop(minutes = minutes_in_day)
async def check_nan():
    actors_df = pd.read_csv('actors.csv')
    actors_df_null = actors_df.isnull()

    if actors_df_null['Picture'].any:
        # Extracting the list of names
        name = []
        for i in actors_df['Names']:
            name.append(i)

        # Extracting the url of the picture
        picture = []
        for i in actors_df['Picture']:
            picture.append(i)

        # Extracting the known for
        known_for = []
        for i in actors_df['Known For']:
            known_for.append(i)

        # Creating a list of names that do not have a picture url associated with them
        name_error = []       
        for k, v in zip(name, actors_df_null['Picture']):
            if v == True:
                name_error.append(k)     

        error_num = 1       # setting the error_num for the function, necessary when creating the table but not entirely needed here.

        # Replacing the NaNs with urls in picture
        picture, name_error, error_num = web_scraper.get_picture_error(name, picture, name_error, error_num)

        # Updating the dataframe
        picture_df = pd.DataFrame({'Picture URL': picture})
        actors_df['Picture'] = picture_df['Picture URL'].values

        # Overwriting the original csv file using Pandas, where Names, Known For, and Picture are the names of the columns
        df = pd.DataFrame({'Names': name, 'Known For': known_for, 'Picture': picture})
        df.to_csv('actors.csv', index = False, encoding = 'utf-8')

        # Loading the updated csv file
        actors_df = pd.read_csv('actors.csv')


# Getting the token and channel that the bot will type to
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_TOKEN'))

# Creating the bot and setting the prefix
bot = commands.Bot(command_prefix = "!", intents = discord.Intents.all())

# Getting the bot to print a message when it is active
@bot.event
async def on_ready():
    print("Hello! I am ready!")

@bot.event
async def setup_hook():
    # Starting the task to get the loop initialised
    check_nan.start()



# Initialising the bot
bot.run(TOKEN)