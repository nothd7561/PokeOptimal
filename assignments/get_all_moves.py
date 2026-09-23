import pandas as pd
import ast 
#pandas for importing
#ast for converting the strings in the list to dictionaries in the list

role_assignments_csv = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\fixing stats\data_merged_normalized.csv'
role_assignments_df = pd.read_csv(role_assignments_csv)
 

move_list = []
#create an empty list to store all the moves
moves = role_assignments_df['Moves']
#create a moves variable that stores the Moves column of the df, which is a pandas series
moves = moves.tolist()
#convert the series into a list for iteration

for sets in moves:
    #for every item in the moves list, convert that item (string) into a dictionary
    set_dicts = ast.literal_eval(sets)
    for key, value in set_dicts.items():
        #iterate through the dictionary and append the key (move name) to the move_list
        move_list.append(key)

test = moves[1]
move_set = set(move_list)
move_list_df = pd.DataFrame(move_set, columns=['Moves'])
#make move_list a set to remove duplicates and print it to the console for testing purposes
#convert to df for csv in the future
move_list_df.to_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\assignments\all_moves.csv', index=False)
