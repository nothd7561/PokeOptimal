import ast
import pandas as pd

input_merged_df = pd.read_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\data extraction\data_merged.csv')

THRESHOLD = 0.10  # an ability counts if it's on at least 10% of that Pokemon's sets

unique_abilities = set()

for abilities_str in input_merged_df['Abilities']:
    abilities = ast.literal_eval(abilities_str)   # string -> real dict
    total = sum(abilities.values())               # this Pokemon's total weighted sets
    if total == 0:
        continue
    for ability, count in abilities.items():
        if ability and count / total >= THRESHOLD:  # `ability and` skips blank keys
            unique_abilities.add(ability)

ability_df = pd.DataFrame({'ability': sorted(unique_abilities), 'category': ''})
ability_df.to_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\made_outside_of_coding\unique_abilities.csv', index=False)

print(len(unique_abilities))