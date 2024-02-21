### A basic application that will scrape data from the IMDB top 100 actors and actresses and output it for use in a Discord bot
### The data will be a url link to their profile picture, their name, and what roles they are known for

# As IMDB is written in javascript, the Selenium package is used
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from dotenv import load_dotenv
from google_images_search import GoogleImagesSearch
import time

load_dotenv()

# Setting the google api key for image searching and project cx
GOOGLE_TOKEN = os.getenv('GOOGLE_TOKEN')
GOOGLE_CX = os.getenv('GOOGLE_CX')

gis = GoogleImagesSearch(GOOGLE_TOKEN, GOOGLE_CX)

# Setting the browser that we will be using
driver = webdriver.Firefox()

# Setting the target URL that we will get the data from
driver.get('https://www.imdb.com/chart/starmeter/')

# Creating a blank list for our results
name = []
known_for = []
picture = []

# Add the page source to the variable 'content'
content = driver.page_source
# Load the contents of the page (its source) into beautifulsoup
# class, which analyses the HTML as a nested data structure and allows to select
# its elements by using various selectors
soup = BeautifulSoup(content, 'html.parser')

# Loop over all elements returned by the 'findAll' call. it has the filter 'attrs' given
# to it in order to limit the data returned to those elements with a given class only
# Setting the class to the object containing the name of the actors

for element in soup.find_all(attrs={'class': 'ipc-title__text'}):
    # element will refer to the name of the actor

    if element not in name:         # Ensuring there are no duplicate entries
        name.append(element.text)

# Cleaning the names data into the things we actually want
del name[0]
del name[0] # This is repeated twice to remove the first two elements of the results which were not actually names
name = name[0:100] # Everything in results after the 99th index was not names and therefore irrelevant

# Finding the titles the actor is known for and setting the class to where the data is held
for element in soup.find_all(attrs={'class': 'ipc-link ipc-link--base sc-a3c468bb-0 jBQmsW'}):
    # element will refer to the tv show or film they are known for
    known_for.append(element.text)

# No need to clean the known_for data

# Searching google images and returning a url of the first result for the celebrity since the thumbnail on the imdb page is too small
for element in name:
    # Setting the search parameters
    search_params = {
        'q': element + ' imdb',       # what we are searching for
        'num': 1,
        'fileType': 'jpg'
    }

    # Executing the search
    gis.search(search_params = search_params)
    # Storing the results
    for i in gis.results():
        # Extracting the image url which is the only thing we want
        picture.append(i.url)
        print(element, i.url)

        #time.sleep(15)

for x in picture:
    print(x)



# Exporting the results into a csv file using Pandas, where Names, Known For, and Picture are the names of the columns
df = pd.DataFrame({'Names': name, 'Known For': known_for, 'Picture': picture})
df.to_csv('actors.csv', index = False, encoding = 'utf-8')