import pandas as pd


input_merged_csv = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\data extraction\data_merged.csv'
merged_normalized = pd.read_csv(input_merged_csv)
#Input our merged 1st faster csv 
#read the csv into a dataframe and store it inside a variable to be used later

merged_normalized['hp_normalized'] = ((merged_normalized['HP'] - merged_normalized['HP'].min()) / (merged_normalized['HP'].max() - merged_normalized['HP'].min())) 
merged_normalized['attack_normalized'] = ((merged_normalized['Attack'] - merged_normalized['Attack'].min()) / (merged_normalized['Attack'].max() - merged_normalized['Attack'].min()))
merged_normalized['defense_normalized'] = ((merged_normalized['Defense'] - merged_normalized['Defense'].min()) / (merged_normalized['Defense'].max() - merged_normalized['Defense'].min()))
merged_normalized['special_attack_normalized'] = ((merged_normalized['Special Attack'] - merged_normalized['Special Attack'].min()) / (merged_normalized['Special Attack'].max() - merged_normalized['Special Attack'].min()))
merged_normalized['special_defense_normalized'] = ((merged_normalized['Special Defense'] - merged_normalized['Special Defense'].min()) / (merged_normalized['Special Defense'].max() - merged_normalized['Special Defense'].min()))
merged_normalized['speed_normalized'] = ((merged_normalized['Speed'] - merged_normalized['Speed'].min()) / (merged_normalized['Speed'].max() - merged_normalized['Speed'].min()))
#used the normalization formula to normalize the base stats for each pokemon
#created new columns for each stat to store the normalized values, keep the base stats for user knowledge and maybe IV/EV spreads

merged_normalized['hp_tier'] = pd.qcut(merged_normalized['HP'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
merged_normalized['attack_tier'] = pd.qcut(merged_normalized['Attack'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
merged_normalized['defense_tier'] = pd.qcut(merged_normalized['Defense'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
merged_normalized['special_attack_tier'] = pd.qcut(merged_normalized['Special Attack'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
merged_normalized['special_defense_tier'] = pd.qcut(merged_normalized['Special Defense'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
merged_normalized['speed_tier'] = pd.qcut(merged_normalized['Speed'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
#assign each pokemon's base stats a tier based on the quartiles of the base stat distribution, with 4 tiers: Low, Medium, High, Very High


normalized_csv = merged_normalized.to_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\fixing stats\data_merged_normalized.csv', index=False)
