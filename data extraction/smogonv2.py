import pandas as pd
import requests
from pathlib import Path
#pandas for df cleaning and manipulation
#requestes for extracting data from the web

###This script will pull data from recent 3 months of smogon competitive 
###data and create a csv file for all the 3 months with the data in it.
###want to make a df from the data then export that as a csv

monthly_urls =['https://www.smogon.com/stats/2026-08/chaos/gen4ou-1500.json',
               'https://www.smogon.com/stats/2026-07/chaos/gen4ou-1500.json',
               'https://www.smogon.com/stats/2026-06/chaos/gen4ou-1500.json']
#the urls for the smogon static files for the last 3 months of data

def extract(link):
### this function takes a link as an argument, then converts the json into a python dictionary. Then it extracts desired data and stores
### each one into a variable, which then forms a dataframe by appending the variables (dictionaries) into an empty list. so the df is a list of dicts
    extraction = requests.get(link)
    #requests extract the info from the link and stores it in a variable
    data = extraction.json()
    #the data is in json format so we convert it to a python dictionary which can actually be modified
    pokemon_data = data['data'] 
    #specifically for smogon, the data we want is stored in the 'data' key of the dictionary, so we extract that and store it in a variable

    desired_data = [] 
    #an empty list to store our wanted data after extraction
    for pokemon_name, stats in pokemon_data.items(): #for each pokemon, we extract name and stats
        usage = stats['usage']
        abilities = stats['Abilities']
        items = stats['Items']
        teammates = stats['Teammates']
        moves = stats['Moves']
        #we extract the data we want from the stats dictionary and store it in variables

        desired_data.append({
            'Pokemon': pokemon_name,
            'Usage': usage,
            'Abilities': abilities,
            'Items': items,
            'Teammates': teammates,
            'Moves': moves
        })
        #we append the data we want to our empty list as a dictionary with the keys being the column names and the values being the data we extracted

    smogon_frame = pd.DataFrame(desired_data) #makes a pandas df from the list of dictionaries
    return smogon_frame #returns the df to be used later

monthly_data = []
for url in monthly_urls:
    extract(url)
    monthly_data.append(extract(url))
    #get the data from each month and append it to the list of monthly data, a total of 3 months
    #monthly_data is a list of 3 dataframes, one for each month
total_data = pd.concat(monthly_data, ignore_index=True) #combine the 3 months of data into one df

total_data_average = total_data.groupby('Pokemon')['Usage'].mean().reset_index()
for i, df in enumerate(monthly_data):
    df['month_priority'] = i  # 0=Jan, 1=Dec, 2=Feb (higher = more recent)

# tag each monthly df with its actual calendar month (string-sortable, e.g. "2026-08"), not list position
for i, df in enumerate(monthly_data):
    df['month_priority'] = monthly_urls[i].split('/')[4]

# combine the tagged monthly frames, then sort so the most recent month comes first per Pokemon
all_moveset_data = pd.concat(monthly_data, ignore_index=True).sort_values('month_priority', ascending=False)

moveset_data = all_moveset_data.drop_duplicates(subset='Pokemon', keep='first')[["Pokemon", "Moves", "Items", "Abilities", "Teammates"]]
#drop duplicates so we keep the only the most recent month for each Pokemon, and keep only the columns we want

final_smogon = pd.merge(total_data_average, moveset_data, on="Pokemon")
#merge the average data with the movest data to create a final df with all the data we want

final_smogon.to_csv(f'C:\\Users\\lucas\\Downloads\\personal coding\\pokemon optimizer v2\\data extraction\\fetch_smogon.csv', index=False)
#converts the final df into a csv file and saves it to the base directory

print("Csv file created successfully.")
#print a message to let the user know the script has completed successfully