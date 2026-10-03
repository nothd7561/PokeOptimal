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

del category_moves['none']
#delete the none category, it's unhelpful for the final role assignment
all_categories = {}
for key,value in category_moves.items():
    all_categories[key] = 0
    
#make a dictionary with all the categories as keys, and 0 as the value to use later for cross checking

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

role_assignment = {}
for key, value in move_dict.items():
    role_assignment[key] = dict(all_categories)
    #create a copy of the all_categories dict, to prevent all pokemon from sharing the same dictionary

for pokemon, pokemon_moves in move_dict.items():
    qualified_moves = {move for move, usage_rate in pokemon_moves.items() if usage_rate >= 0.25}
    #for each pokemon, check it's moves. They are qualified if they are above the threshold of 0.25 usage rate.
    #we use a set because the same move can show up in multiple pokemons movesets

    for move_category, moves_in_category in category_moves.items():
        for pokemon_move in qualified_moves:
            if pokemon_move in moves_in_category:
                role_assignment[pokemon][move_category] = 1
    #looped over each move category, for each one, we looped over the moves in the qualified moves dict
    #then if the qualified move was also in the values for moves in said category, then we give the move_category value for said pokemon a 1
    #we're using binary values for the role assignments later for optimization portion

role_assignment_df = pd.DataFrame(role_assignment).T.reset_index()
#turn the dict into a dataframe so we could merge with the previous dataframe later on
#use transpose to flip rows and columns, making pokemon as the rows and categories as columns to match merged_csv
#reset index so that pokemon names arent the index
role_assignment_df = role_assignment_df.rename(columns={'index':'Pokemon'})
#since reset index sets the pokemon column name to index, rename it to Pokemon to match merged csv

final_role_assignment = pd.merge(input_pokemon_info, role_assignment_df, on='Pokemon')

              
print(final_role_assignment)