import pandas as pd
###GOAL is to turn the categorized move list into a binary matrix
###then for each category, list all the moves contained so that we can iterate over them later


input_moves_list_csv = pd.read_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\made_outside_of_coding\all_moves_categorized_multicategory.csv')
#read the csv generated the chatGPT into a dataframe

binary_matrix = input_moves_list_csv['category'].str.get_dummies(sep=',')
#turns the dataframe into a wide, binary matrix

binary_matrix.index = input_moves_list_csv['move']
#set moves as the index of the df

print(binary_matrix)

