import pandas as pd
import requests
import time


csv_in = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\data extraction\fetch_smogon.csv'
#store the msogon csv file in a variable to be used later
df = pd.read_csv(csv_in)
#read the said csv in and put it itno a pandas df

names = df['Pokemon'].tolist()
#stores the names of all the pokemon in the Pokemon column of the df into a list to be used later

def extract_pokeapi(name):
    name = name.lower()
    #lower the first letter of each pokemon name to match the api request format

    api_link = requests.get(f'https://pokeapi.co/api/v2/pokemon/{name}')
    if api_link.status_code == 200:
        return api_link.json()
    else:
        return None
    #returns the json format for each pokemon, which is a dictionary with all the data we want to extract
    #for each name, put substitute it in the api link to get the data for that specific pokemon

pokeapi_list = []
#empty list to store the data we want from the api for each pokemon

for name in names:
    api_data = extract_pokeapi(name)
    #for each name in the list of names, call the function to extract the data from the api
    if api_data is not None:
        print('Extracting data for', name)
        poke_dic = {
            'Pokemon': name,
            'HP': api_data['stats'][0]['base_stat'],
            'Attack': api_data['stats'][1]['base_stat'],
            'Defense': api_data['stats'][2]['base_stat'],
            'Special Attack': api_data['stats'][3]['base_stat'],
            'Special Defense': api_data['stats'][4]['base_stat'],
            'Speed': api_data['stats'][5]['base_stat'],
            #creating a dictionary with the data(stats) we want from the api for each pokemon,
            #these lines are found from analyzing the json data from the api and finding where the data we want is stored
            'Type1': api_data['types'][0]['type']['name'],
            'Type2': api_data['types'][1]['type']['name'] if len(api_data['types']) > 1 else None
            #if the pokemon has a second type, we extract it, if not we store None
    }
    time.sleep(0.5)
    #add a 0.5 second delay between each request to avoid hitting api rate limits

    pokeapi_list.append(poke_dic)
    #append the dictionary to the list for each pokemon, ending up with a list of dictionaries to set up for a dataframe

pokeapi_df = pd.DataFrame(pokeapi_list)
pokeapi_df.to_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\data extraction\fetch_pokeapi.csv', index=False)