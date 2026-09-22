import pandas as pd
import ast 
#pandas for importing
#ast for converting the strings in the list to dictionaries in the list

role_assignments_csv = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\fixing stats\data_merged_normalized.csv'
role_assignments_df = pd.read_csv(role_assignments_csv)

move_list = []
moves = role_assignments_df['Moves']
moves = moves.tolist()
for sets in moves:
    set_dicts = ast.literal_eval(sets)
    for key, value in set_dicts.items():
        move_list.append(key)

#moves is a list with strings
#need to conver the list of strings into a list of dictionaries, where each dictionary is a moveset for a pokemon
test = moves[1]
print(set(move_list))
