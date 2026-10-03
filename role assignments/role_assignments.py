import pandas as pd
#pandas for data manipulation

input_moves_df = pd.read_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\moves\pokemon_has_moves.csv')
#read the move categorie csv

ROLE_CONFIG = {
    "Sweeper": {
        "stats_all": [("speed", ["High", "Very High"])],
        "stats_any": [("attack", ["High", "Very High"]), ("special_attack", ["High", "Very High"])],
        "moves": []
    },
    "Wallbreaker": {
        "stats_all": [],
        "stats_any": [("attack", ["High", "Very High"]), ("special_attack", ["High", "Very High"])],
        "moves": []
    },
    "Cleaner": {
        "stats_all": [],
        "stats_any": [],
        "moves": ["has_priority"]
    },
    "Wall": {
        "stats_all": [],
        "stats_any": [("defense", ["High", "Very High"]), ("special_defense", ["High", "Very High"])],
        "moves": ["has_recovery"]
    },
    "Tank": {
        "stats_all": [],
        "stats_any": [("defense", ["Medium", "High"]), ("special_defense", ["Medium", "High"])],
        "moves": []
    },
    "Cleric": {
        "stats_all": [],
        "stats_any": [],
        "moves": ["has_recovery", "has_status_heal"]
    },
    "Hazard Setter": {
        "stats_all": [],
        "stats_any": [],
        "moves": ["has_hazards"]
    },
    "Hazard Control": {
        "stats_all": [],
        "stats_any": [],
        "moves": ["has_hazard_removal"]
    },
    "Pivot": {
        "stats_all": [],
        "stats_any": [],
        "moves": ["has_volt_turn"]
    },
    "Screener": {
        "stats_all": [],
        "stats_any": [],
        "moves": ["has_screen"]
    },
    "Stallbreaker": {
        "stats_all": [],
        "stats_any": [],
        "moves": ["has_status"]
    },
    "Annoyer": {
        "stats_all": [],
        "stats_any": [],
        "moves": ["has_status"]
    },
    "Suicide Lead": {
        "stats_all": [],
        "stats_any": [("defense", ["Low", "Medium"]), ("special_defense", ["Low", "Medium"])],
        "moves": ["has_hazards"]
    },
}

def check_role_req(pokemon_data, role_requirements):
    for stat, acceptable_tiers in role_requirements['stats_all']:
        if pokemon_data[f"{stat}_tier"] not in acceptable_tiers:
            return False

    if role_requirements["stats_any"]:
        if not any(pokemon_data[f"{stat}_tier"] in acceptable_tiers for stat, acceptable_tiers in role_requirements["stats_any"]):
            return False

    if role_requirements["moves"]:
        if not any(pokemon_data[category] == 1 for category in role_requirements["moves"]):
            return False
    #check move categories, at least one move category must have value 1

    return True

role_results = {}
for _, row in input_moves_df.iterrows():
    pokemon = row["Pokemon"]
    #focus on the pokemon column
    role_results[pokemon] = {}
    #give each pokemon an initial empty dictionary to store the role results
    for role, requirements in ROLE_CONFIG.items():
        role_results[pokemon][role] = check_role_req(row, requirements)
        #check the role requirements for each role, and store the result in the pokemon's dictionary

role_results_df = pd.DataFrame.from_dict(role_results, orient='index')
final_role_assignment_df = pd.merge(input_moves_df, role_results_df, left_on='Pokemon', right_index=True)
final_role_assignment_df.to_csv(r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\role assignments\final_role_assignment.csv', index=False)
