import pandas as pd
import os
import math
from datetime import datetime
import calendar
DATA_PATH = "C:/Users/Daniel Lee/Desktop/Blizzard Stats/Season2/"
cleaned_hero_switch_PATH = "cleaned_hero_switch.csv.gz"
hero_guids = "payload_guids_heroes.tsv"
week_folder = DATA_PATH + '20190429/'
team_comp_folder = week_folder + 'Team Comps'
team_comp_test = week_folder + 'Team Comps Test'

def convert_to_secs(ms):
    return ms / 1000

def create_team_comps(folder, compression):
  files = os.listdir(folder)
  sorted_files = sorted(files, key=lambda x: str(x.split('.')[0]))
  csvs = []
  for file in sorted_files:
    if file.endswith(".csv"):
        csvs.append(file)
  for i, daily_comp in enumerate(csvs):
    print(daily_comp)
    hero_switch = pd.read_csv(folder + "/" + daily_comp, sep = ',')
    comp_tracking = dict()
    comp = []
    map_arr = []
    duration = []
    team_arr = []
    round_arr = []
    date_arr = []
    prev_map = -1
    prev_round = -1
    hero_switch_length = len(hero_switch.index)
    for index, row in hero_switch.iterrows():
        #if index == 22:
            #exit()
        #print(index)
        #print(row)
        team = row['Team']
        player = row['short battletag']
        old_hero_guid = row['old_hero_guid']
        old_hero = row['old hero']
        new_hero = row['new hero']
        map = row['map_name']
        round = row['round_name']
        starttime = row['time_x']

        # Team is not in dictionary yet
        if team not in comp_tracking:
          #print("A")
          #New Team and new Map, so update old comps
          if old_hero_guid == 0 and prev_map != -1 and map != prev_map:
            #print("Aa")
            hero_list = comp_tracking[prev_team][prev_map][0]
            comp.append(", ".join(hero_list))
            team_arr.append(prev_team)
            map_arr.append(prev_map)
            round_arr.append(prev_round)
            date_arr.append(daily_comp)
            duration.append(convert_to_secs(round_end - comp_tracking[prev_team][prev_map][1]))

            for z in reversed(team_arr):
                if z != team and z!= prev_team:
                    other_team2 = z
                    break
            hero_list = comp_tracking[other_team2][prev_map][0]
            comp.append(", ".join(hero_list))
            round_arr.append(prev_round)
            team_arr.append(other_team2)
            map_arr.append(prev_map)
            date_arr.append(daily_comp)
            duration.append(convert_to_secs(round_end - comp_tracking[other_team2][prev_map][1]))
            prev_map = map
            prev_round = round

          comp_tracking[team] = dict()
          comp_tracking[team][map] = [[new_hero], starttime]
        else:
          #This map already exists
          if map in comp_tracking[team]:
            #print("B")
            hero_list = comp_tracking[team][map][0]
            #print("BBBBB Hero list:", hero_list)
            #Starting comps
            if old_hero_guid == 0 and len(hero_list) < 6:
              #print("C")
              hero_list.append(new_hero)
              comp_tracking[team][map][1] = starttime
            elif old_hero_guid == 0 and len(hero_list) >= 6:
              #print("D")
              hero_list.sort()
              comp.append(", ".join(hero_list))
              round_arr.append(round)
              team_arr.append(team)
              map_arr.append(map)
              date_arr.append(daily_comp)
              duration.append(convert_to_secs(starttime - comp_tracking[team][map][1]))
              comp_tracking[team][map] = [[new_hero], starttime]
              comp_tracking[team][map][1] = starttime
            elif len(hero_list) < 6 and old_hero_guid != 0:
              #print("E")
              #Reset the comp and show the new one
              for index2, old_h in enumerate(hero_list):
                if old_h == old_hero:
                  #print("F")
                  hero_list[index2] = new_hero
                  break
              comp_tracking[team][map][1] = starttime
            #New comp on same map
            else:
              #print("G")
              #Store the comp and information
              hero_list.sort()
              comp.append(", ".join(hero_list))
              round_arr.append(round)
              team_arr.append(team)
              map_arr.append(map)
              date_arr.append(daily_comp)
              duration.append(convert_to_secs(starttime - comp_tracking[team][map][1]))
              #print("GGGGGGG Duration: ", convert_to_secs(starttime - comp_tracking[team][map][1]))
              #print("GGGGGGG comp: ", comp[-1])
              #Reset the comp and show the new one
              for index3, old_h in enumerate(hero_list):
                if old_h == old_hero:
                  #print("H")
                  hero_list[index3] = new_hero
                  break
              comp_tracking[team][map][1] = starttime
              #print("Last Duration: ", duration[-1])
              #print("Last Comp Array: ", comp[-1])
              prev_map = map
              prev_round = round
              round_end = row['time_y']
          #We are a new map
          else:
            #print("I")
            #Store previous map information
            if old_hero_guid == 0:
              #print("J")
              hero_list = comp_tracking[team][prev_map][0]
              comp.append(", ".join(hero_list))
              team_arr.append(team)
              round_arr.append(prev_round)
              map_arr.append(prev_map)
              date_arr.append(daily_comp)
              duration.append(convert_to_secs(round_end - comp_tracking[team][prev_map][1]))
              #print("Last Duration: ", duration[-1])
              #print("Last Comp Array: ", comp[-1])
              #print("Round end: ", round_end)
              #print("time prev map: ", comp_tracking[team][prev_map][1])
              comp_tracking[team][map] = [[new_hero], starttime]
              comp_tracking[team][map][1] = starttime
            elif len(hero_list) < 6 and old_hero_guid != 0:
              #print("K")
              #Reset the comp and show the new one
              for index4, old_h in enumerate(hero_list):
                if old_h == old_hero:
                  #print("L")
                  hero_list[index4] = new_hero
                  break
              comp_tracking[team][map][1] = starttime
        prev_team = row['Team']

        if (index >= hero_switch_length - 1):
            print("LAST ROWW")
            #Get Other Team
            for z in reversed(team_arr):
                if z != team:
                    other_team = z
                    break
            hero_list.sort()
            comp.append(", ".join(hero_list))
            round_arr.append(round)
            team_arr.append(team)
            map_arr.append(map)
            date_arr.append(daily_comp)
            duration.append(convert_to_secs(round_end - comp_tracking[team][map][1]))

            #Append Last Team Comp for Other team
            hero_list = comp_tracking[other_team][map][0]
            hero_list.sort()
            round_arr.append(round)
            comp.append(", ".join(hero_list))
            team_arr.append(other_team)
            map_arr.append(map)
            date_arr.append(daily_comp)
            duration.append(convert_to_secs(round_end - comp_tracking[other_team][map][1]))

    sorted_comps = prioritize_comp_order(comp)
    d = {'date': date_arr, 'comp': sorted_comps, 'duration': duration, 'map': map_arr, 'round': round_arr, 'team': team_arr}
    df = pd.DataFrame(data = d)

    df = df.loc[df['duration'] >= 15]
    if i == 0:
      master_df = df
    else:
      master_df = pd.concat([master_df, df])

  if compression:
      master_df.to_csv(week_folder+ "/" + "team_comps.csv.gz", compression = 'gzip')
  else:
      master_df.to_csv(week_folder + "/" + "team_comps.csv")

def prioritize_comp_order(comp_array):
    heroes = {'Soldier: 76': 3, 'Genji': 3, 'Reaper': 3, 'Ana': 5, 'Bastion': 3, 'Brigitte': 3, 'Doomfist': 3, 'D.Va': 1, 'Hanzo':3,
    'Junkrat': 3, 'Lucio': 5, 'McCree': 3, 'Mei': 3, 'Mercy': 5, 'Moira': 5, 'Orisa': 0, 'Pharah': 3, 'Reinhardt': 0,
    'Roadhog': 1, 'Sombra': 3, 'Symmetra': 3, 'Torbjorn': 3, 'Tracer': 3, 'Widowmaker': 3, 'Winston': 0, 'Zarya': 1,
    'Zenyatta': 4, 'Wrecking Ball': 0, 'Ashe': 3, 'Baptiste': 4}
    sorted_comps = []

    for index, comp in enumerate(comp_array):
        array = comp.split(", ")
        if len(array) != 6:
            print("This row is wrong for some reason: " + str(index))
        if len(set(array)) != len(array):
            print("This row has duplicate hero: " + str(index) + " : " + comp)
        keys = []
        for hero in array:
            keys.append(heroes[hero])
        sorted_comp = [x for _,x in sorted(zip(keys,array))]
        sorted_comps.append(", ".join(sorted_comp))
    return sorted_comps

def create_daily_matches(folder, compression):
  hero_switch = pd.read_csv(folder + "/" + cleaned_hero_switch_PATH, sep = ',', compression = "gzip")
  dates = []
  for index, row in hero_switch.iterrows():
    datetime_obj = datetime.strptime(row['switch time'], '%Y-%m-%d %H:%M:%S')
    if datetime_obj.hour - 8 < 0:
      if datetime_obj.day == 1 and datetime_obj.month == 1:
        day = str(calendar.monthrange(datetime_obj.year - 1, 12)[1])
        month = str(12)
      elif datetime_obj.day == 1:
        day = str(calendar.monthrange(datetime_obj.year, datetime_obj.month - 1)[1])
        month = str(datetime_obj.month - 1)
      else:
        day = str(datetime_obj.day - 1)
        month = str(datetime_obj.month)
    else:
      day = str(datetime_obj.day)
      month = str(datetime_obj.month)
    if len(day) < 2:
      day  = "0"+day
    dates.append(month + "-" + day)
  hero_switch['date'] = dates
  dates = hero_switch['date'].unique()
  for date in dates:
    new_df = hero_switch[hero_switch['date'] == date]
    if compression:
      new_df.to_csv(folder + "Team Comps/" + date + "team_comps.csv.gz", compression = 'gzip')
    else:
      new_df.to_csv(folder + "Team Comps/" + date + "team_comps.csv")
    print("Date Processed: " + str(date))

def write():
    create_daily_matches(week_folder, False)
    create_team_comps(team_comp_folder, compression = False)
    print("CSV is being processed!")

if __name__ == '__main__':
    write()
