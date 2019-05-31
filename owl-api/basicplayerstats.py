import requests
import json
import pandas as pd
import csv
import numpy as np

import inspect

#Helper function
def retrieve_name(var):
    """
    Gets the name of var. Does it from the out most frame inner-wards.
    :param var: variable to get name from.
    :return: string
    """
    for fi in reversed(inspect.stack()):
        names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
        if len(names) > 0:
            return names[0]

#GET JSON from API
def get_json():
    response = requests.get("https://api.overwatchleague.com/stats/players")
    parsed = json.loads(response.content)
    keys = parsed['data'][0].keys()

    with open('Stage1/Playoff/SFvsVancouver.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(parsed['data'])

#Maintanks
maintank = ["Marve1", "Yakpung", "ameng", "Axxiom", "BenBest", "BUMPER", "Fate", "Fissure", "Fusions", "Gamsu", "Gator", "Gesture", "Guxue",
            "Janus", "Mano", "Muma", "NoSmite", "OGE", "Pokpo", "Rio", "rOar", "Sado", "Smurf", "super", "SWoN"]
#OffTanks
offtank = ["ZUNBA", "Mcgravy", "Choihyobin", "coolmatt", "Daco", "Elsa", "Envy", "Finnsi", "Fury", "Geguri", "JJANU", "HOTBA",
        "lateyoung", "MekO", "Michelle", "Nevix", "NotE", "Poko", "rCk", "Ria", "Sansam", "SPACE", "SPREE", "Void", "xepheR"]
#MainDPS
maindps = ["FITS", "ShadowBurn", "Decay", "Surefour", "STRIKER", "SoOn", "SeoMinSoo", "sinatraa", "KariV", "Fleta", "Happy",
        "GodsB", "dafran", "Danteh", "EFFECT", "Corey", "carpe", "bqb", "ColourHex", "BIRDRING", "aKm", "ivy", "Nenne", "Profit", "sayaplayer", "Baconjack", "diem", "Stitch", "KSF"]
#FlexDPS
flexdps = ["Rascal", "Saebyeolbe", "Stratus", "Apply", "ZachaREEE", "TviQ", "Hydration", "snillo", "eqo", "NiCOgdh", "LiNkzr", "Libero", "Kyb",
        "JinMu", "Jake", "Guard", "blase", "Architect", "Agilities", "Ado", "NLaaeR", "Haksal", "YOUNGJIN", "Stellar", "Erster", "Eileen", "Bazzi", "Adora", "Munchkin"]
#Main Supports
mainsupport = ["tobi", "Masaa", "moth", "neptuNo", "NUS", "alemao", "Anamo", "ArK", "BigG00se", "Boink", "Chara",
            "Closer", "CoMa", "Custa", "Fahzix", "Hyeonu", "iDK", "Jecse", "Kellex", "Kris", "Kruise", "RoKy", "SLIME", "Yveltal", "KuKi"]
#Flex Supports
flexsupport = ['HyP', "Bani", "Neko", "RAPEL", "Twilight", "uNKOE", "Viol2t", "Gido", "HaGoPeun", "JJONAK", "IZaYaKI", "Luffy", "Hyp", "Kodak", "Kyo",
            "ryujehong", "Shaz", "shu", "sleepy", "Rawkus", "Revenge", "Dogman", "Elk", "BEBE", "Bdosin", "AimGod", "Aid", "Boombox"]
positions = [maintank, offtank, maindps, flexdps, mainsupport, flexsupport]

#Change Offense, Support, Tank to subroles
def change_role():
    pos = ""
    df = pd.read_csv('Stage1/Playoff/SFvsFusion.csv', sep = ",")

    for i, row in df.iterrows():
        player_name = row['name']
        for position in positions:
            if player_name in position:
                pos = retrieve_name(position)
                break
        df.at[i, 'role'] = pos
        df.loc[i, 'total_elims'] = (row['eliminations_avg_per_10m']/10) * (row['time_played_total']/60)
        df.loc[i, 'total_deaths'] = (row['deaths_avg_per_10m']/10) * (row['time_played_total']/60)
        df.loc[i, 'total_hero_damage'] = (row['hero_damage_avg_per_10m']/10) * (row['time_played_total']/60)
        df.loc[i, 'total_healing'] = (row['healing_avg_per_10m']/10) * (row['time_played_total']/60)
        df.loc[i, 'total_ultimates'] = (row['ultimates_earned_avg_per_10m']/10) * (row['time_played_total']/60)
        df.loc[i, 'total_final_blows'] = (row['final_blows_avg_per_10m']/10) * (row['time_played_total']/60)
    df.to_csv('Stage1/Playoff/SFvsFusionTotal.csv', sep=',')

#Full outer join prev and curr tables
def create_prev_curr_week_merged():
    df_prev = pd.read_csv('Stage1/Playoff/SFvsFusionTotal.csv', sep = ",")
    df_curr = pd.read_csv('Stage1/Playoff/SFvsVancouverTotal.csv', sep = ",")
    df_merged = pd.merge(df_prev, df_curr, on="name", how ="outer", suffixes = ('_prev', '_curr'))
    df_merged.to_csv("Stage1/Playoff/SFvsVancouvermerged.csv", sep=',')

#Find out stats for the week
def weekly_change():
    #Change this to and from read_csv, to_csv
    df_merged = pd.read_csv("Stage1/Playoff/SFvsVancouvermerged.csv", sep=',')
    merged_len = len(df_merged.index)
    row_index = [str(i) for i in range(merged_len)]
    df_weekly = pd.DataFrame(columns=['status', 'player_id', 'team_id', 'role', 'name','team', 'elim_per_10m', 'death_per_10m','dmg_per_10m', 'heal_per_10m', 'ults_per_10m', 'finalblows_per_10m', 'duration', 'elims', 'deaths', 'damage', 'heal', 'ults', 'finalblows'] ,index = row_index)

    for i,row in df_merged.iterrows():
        print(i)
        df_weekly.loc[str(i)]['player_id'] = row['playerId_curr']
        df_weekly.loc[str(i)]['name'] = row['name']
        df_weekly.loc[str(i)]['team_id'] = row['teamId_curr']
        df_weekly.loc[str(i)]['role'] = row['role_curr']
        df_weekly.loc[str(i)]['team'] = row['team_curr']

        if np.isnan(row['time_played_total_prev']):
            time_played = round(row['time_played_total_curr'])
            total_elims = round(row['total_elims_curr'])
            total_deaths = round(row['total_deaths_curr'])
            total_damage = row['total_hero_damage_curr']
            total_healing = round(row['total_healing_curr'])
            total_ultimates = round(row['total_ultimates_curr'])
            total_finalblows = round(row['total_final_blows_curr'])
        else:
            time_played = round(row['time_played_total_curr'] - row['time_played_total_prev'])
            total_elims = round(row['total_elims_curr'] - row['total_elims_prev'])
            total_deaths = round(row['total_deaths_curr'] - row['total_deaths_prev'])
            total_damage = row['total_hero_damage_curr'] - row['total_hero_damage_prev']
            total_healing = round(row['total_healing_curr'] - row['total_healing_prev'])
            total_ultimates = round(row['total_ultimates_curr'] - row['total_ultimates_prev'])
            total_finalblows = round(row['total_final_blows_curr'] - row['total_final_blows_prev'])

        if time_played == 0:
            df_weekly.loc[str(i)]['status'] = "NO_CHANGE"
            continue

        df_weekly.loc[str(i)]['duration'] = time_played
        df_weekly.loc[str(i)]['elims'] = total_elims
        df_weekly.loc[str(i)]['deaths'] = total_deaths
        df_weekly.loc[str(i)]['damage'] = total_damage
        df_weekly.loc[str(i)]['heal'] = total_healing
        df_weekly.loc[str(i)]['ults'] = total_ultimates
        df_weekly.loc[str(i)]['finalblows'] = total_finalblows
        df_weekly.loc[str(i)]['elim_per_10m'] = (total_elims)/(time_played/600)
        df_weekly.loc[str(i)]['death_per_10m'] = (total_deaths)/(time_played/600)
        df_weekly.loc[str(i)]['dmg_per_10m'] = (total_damage)/(time_played/600)
        df_weekly.loc[str(i)]['heal_per_10m'] = (total_healing)/(time_played/600)
        df_weekly.loc[str(i)]['ults_per_10m'] = (total_ultimates)/(time_played/600)
        df_weekly.loc[str(i)]['finalblows_per_10m'] = (total_finalblows)/(time_played/600)
        df_weekly.loc[str(i)]['status'] = "Updated"

    df_weekly.to_csv("Stage1/Playoff/SFvsVancouver-matchly.csv", sep=',')

if __name__ == "__main__":
    get_json()
    change_role()
    create_prev_curr_week_merged()
    weekly_change()
