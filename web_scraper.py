### A basic application that will scrape data from the IMDB top 100 actors and actresses and output it for use in a Discord bot
### The data will be a url link to their profile picture, their name, and what roles they are known for

# As IMDB is written in javascript, the Selenium package is used
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from dotenv import load_dotenv
from google_images_search import GoogleImagesSearch

load_dotenv()


def get_picture(name):
    '''list of strings -> list of strings

    This is a function that takes an input of celebrity names and returns a url
    to a picture of each celebrity
    '''
    name_error = []
    picture = []
    error_num = 0       # If this number remains 0 then no errors have occurred, if the number changes to 1 then an HTTPError 500 has occurred but the code
    # can continue. If the number changes to 2, then there is a problem with the API credentials, either they are incorrect or daily quotas have been reached

    # Searching google images and returning a url of the first result for the celebrity
    for element in name:
        # Setting the search parameters
        search_params = {
            'q': element + ' imdb',       # what we are searching for
            'num': 1,
            'fileType': 'jpg'
        }

        # This code returns errors occasionally due to issues with google's backend servers
        # Adding error handling to mitigate this
        try:
            # Executing the search
            gis.search(search_params = search_params)
            # Storing the results
            for i in gis.results():

                # Extracting the image url which is the only thing we want
                picture.append(i.url)
        except Exception as error:
            error_string = str(error)
            if "HttpError 500" in error_string:
                print(f"HttpError 500 occurred processing {element}, continuing with list")
                picture.append(np.nan)
                name_error.append(element)
                error_num = 1
                continue
            else:
                print("An error occurred due to a problem with the credentials. Please check the credentials are correct"
                       " and your queries per day has not been reached")
                picture.append(np.nan)
                name_error.append(element)
                error_num = 2

    return picture, name_error, error_num

def get_picture_error(name, picture, name_error, error_num):
    '''list of strings -> list of strings
    This method does the same thing as get_picture except it only finds the names that have created errors
    name is the full list of actors names
    picture is the full list of images associated with each actor
    name_error is the full list of actors that were not able to be completed due to errors
    '''
    print("Names detected in name_error, retrieving images for them")

    GOOGLE_TOKEN = os.getenv('GOOGLE_TOKEN')
    GOOGLE_CX = os.getenv('GOOGLE_CX')
    gis = GoogleImagesSearch(GOOGLE_TOKEN, GOOGLE_CX)

    # Initialising increment count for picture
    i_count = 0

    # Searching google images and returning a url of the first result for the celebrity
    for element in name:
        if element in name_error:
            # Setting the search parameters
            search_params = {
                'q': element + ' imdb',       # what we are searching for
                'num': 1,
                'fileType': 'jpg'
            }

            # This code returns errors occasionally due to issues with google's backend servers
            # Adding error handling to mitigate this
            try:
                # Executing the search
                gis.search(search_params = search_params)
                # Storing the results
                for i in gis.results():
                    # Extracting the image url which is the only thing we want and replacing the NaN
                    # That was stored there
                    picture[i_count] = i.url
                    # Removing the name from the element when it gets a picture associated with it
                    name_error.remove(element)
            except Exception as error:
                error_string = str(error)
                if "HttpError 500" in error_string:
                    print(f"HttpError 500 occurred processing {element}, continuing with list")
                    continue
                else:
                    print("An error occurred due to a problem with the credentials. Please check the credentials are correct"
                           " and your queries per day has not been reached")
                    error_num = 2
            
            # Incrementing index counter for picture
            i_count += 1
        
        else:
            # Incrementing index counter for picture
            i_count += 1
            continue

    
    # If name_error list is blank after the loop has occurred then error_num is set to 0 and the function stops
    if not name_error:
        error_num = 0

    return picture, name_error, error_num

# Creating a def main if __name__ == '__main__' so that this code isn't automatically ran when imported
def main():
    # Setting the google api key for image searching and project cx
    GOOGLE_TOKEN = os.getenv('GOOGLE_TOKEN')
    GOOGLE_CX = os.getenv('GOOGLE_CX')

    # Setting a global variable is bad practice and should be done as little as possible
    global gis 
    gis = GoogleImagesSearch(GOOGLE_TOKEN, GOOGLE_CX)

    # Setting the browser that we will be using
    driver = webdriver.Firefox()

    # Setting the target URL that we will get the data from
    driver.get('https://www.imdb.com/chart/starmeter/')

    # Creating a blank list for our results
    name = []
    known_for = []

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
    
    # Closing the Selenium browser
    driver.quit()
    
    picture, name_error, error_num = get_picture(name)
    print(name_error)

    while error_num == 1:
        picture, name_error, error_num = get_picture_error(name, picture, name_error, error_num)
        if error_num == 2:
            pass

    # Exporting the results into a csv file using Pandas, where Names, Known For, and Picture are the names of the columns
    df = pd.DataFrame({'Names': name, 'Known For': known_for, 'Picture': picture})
    df.to_csv('actors.csv', index = False, encoding = 'utf-8')

if __name__ == '__main__':
    main()