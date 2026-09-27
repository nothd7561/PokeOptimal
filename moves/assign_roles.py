import pandas as pd
###GOAL is to turn the categorized move list into a binary matrix
###then for each category, list all the moves contained so that we can iterate over them later


input_moves_list_csv = pd.read_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\made_outside_of_coding\all_moves_categorized_multicategory.csv')
#read the csv generated the chatGPT into a dataframe

category_moves = {}

for _, row in input_moves_list_csv.iterrows():
    move = row['move']
    categories = row['category'].split(',')  # splits "has_recovery,has_setup" into ["has_recovery", "has_setup"]

    for category in categories:
        if category not in category_moves:
            category_moves[category] = []
        category_moves[category].append(move)
print(category_moves)