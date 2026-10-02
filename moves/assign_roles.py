import pandas as pd
###GOAL is to turn the categorized move list into a binary matrix
###then for each category, list all the moves contained so that we can iterate over them later
import ast

input_moves_list_csv = pd.read_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\made_outside_of_coding\all_moves_categorized_multicategory.csv')
#read the csv generated the chatGPT into a dataframe

input_pokemon_info = pd.read_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\data extraction\data_merged.csv')
#read the merged csv so that we can cross check the moves

category_moves = {}
#create an empty dictionary to store the category moves

for _, row in input_moves_list_csv.iterrows():
    #loops through each row, returning a pair ()
    move = row['move']
    #assign the move name of the df to the variable move
    categories = row['category'].split(',')  # splits "has_recovery,has_setup" into ["has_recovery", "has_setup"]
    #splits the category assignment since we have multi-assign, by string, returns a list

    for category in categories:
        #loop over the category list
        if category not in category_moves:
            category_moves[category] = []
            #if the category isnt in the dict yet, append an empty list as the valur
        category_moves[category].append(move)
        #append the move associated with that category as the value to that category

all_categories = {}
for key,value in category_moves.items():
    all_categories[key] = 0


moves = input_pokemon_info['Moves']
#create a moves variable that stores the Moves column of the df, which is a pandas series
moves = moves.tolist()
#convert the series into a list for iteration



move_dict = {}

for _, row in input_pokemon_info.iterrows():
    pokemon_name = row['Pokemon']
    parsed_moves = ast.literal_eval(row['Moves'])
    #converts each move string into a dict
    move_dict[pokemon_name] = parsed_moves
    #stores the pokemon name as key, the mvoes and usage rate as value

binary_roles = {}
for key, value in move_dict.items():
    binary_roles[key] = all_categories
                


print(binary_roles)
print(all_categories)