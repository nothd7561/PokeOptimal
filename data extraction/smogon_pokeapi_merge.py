import pandas as pd

#GOAL: Merge both extraction csv's to get the initial master csv
##comp stats and base stats for each pokemon in GEN4OU


smogon_input = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\data extraction\fetch_smogon.csv'
pokeapi_input = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\data extraction\fetch_pokeapi.csv'
#load the data extraction inputs in

smogon_df = pd.read_csv(smogon_input)
pokeapi_df = pd.read_csv(pokeapi_input)
#read both csv's into pandas dataframes

merged_df = pd.merge(smogon_df, pokeapi_df, on='Pokemon', how='left')
#merge the two dataframes on the 'Pokemon' column, keeping all rows from smogon_df and adding matching rows from pokeapi_df

merged_csv = merged_df.to_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\data extraction\data_merged.csv', index=False)
#create and export the merged csv