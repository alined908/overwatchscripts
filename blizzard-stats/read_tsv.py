import pandas as pd
import os
import numpy as np

DATA_PATH = "C:/Users/Daniel Lee/Desktop/Blizzard Stats/Season2/"
cleaned_game_result_PATH = 'cleaned_game_result.csv'
cleaned_game_info_PATH = 'cleaned_game_info.csv'
game_info_PATH = "game_info.gz"
game_result_PATH = "game_result.gz"
hero_switch_PATH = "hero_switch.gz"
kill_PATH = "kill.gz"
player_hero_stats_PATH = "player_hero_stats.gz"
player_status_PATH = "player_status.gz"
team_stats_PATH = "team_stats.gz"
#payload_guid_PATH = "C:/Users/Daniel Lee/Desktop/Blizzard Stats/OWL Matches/20180114/payload_guid_stats.gz"

def fix_game_info(folder):
    df = pd.read_csv(folder + "/" + cleaned_game_info_PATH)
    df.drop(['time', 'time_c', 'context', 'team_id_1', 'attacking_team_id', 'time_banked_1'], inplace = True, axis= 1)
    df.drop(['payload_distance_1', 'score_1', 'control_info_1', 'team_id_2', 'payload_distance_2', 'time_banked_2', 'score_2', 'control_info_2', 'Unnamed: 0'], inplace = True, axis = 1)
    df.drop_duplicates(keep = 'first', inplace = True)

    for index, row in df.iterrows():
        if row['round_name_guid'] == 0:
            df.drop(index, inplace=True)
            continue

    df.drop_duplicates(subset = ['esports_match_id', 'round_num'], keep = 'last', inplace = True)
    df.rename(columns = {'round_num': 'round_x'}, inplace = True)
    df.to_csv(folder + "/plain_game_info.csv")

def read_game_info(folder, write, compression):
    if write:
        df = pd.read_csv(folder + "/" + game_info_PATH, sep = '\t', compression = "gzip")

        df.drop_duplicates(subset = ['score_info', 'esports_match_id'], keep = 'first', inplace = True)
        info_df = df['score_info'].str.replace(r'(,[^:]*:|{[^:]*:)', ',')
        score_info_df = info_df.str.split(",", expand =True)

        score_info_df.iloc[:,2] = score_info_df.iloc[:,2].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,5] = score_info_df.iloc[:,5].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,11] = score_info_df.iloc[:,11].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,12] = score_info_df.iloc[:,12].map(lambda x: str(x)[:-2])
        score_info_df.iloc[:,13] = score_info_df.iloc[:,13].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,19] = score_info_df.iloc[:,19].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,20] = score_info_df.iloc[:,20].map(lambda x: str(x)[:-3])
        score_info_df.iloc[:,22] = score_info_df.iloc[:,22].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,23] = score_info_df.iloc[:,23].map(lambda x: str(x)[:-3])

        cols = [0, 4, 10, 18, 21, 24, 25, 26, 27]
        score_info_df.drop(score_info_df.columns[cols], axis = 1, inplace = True)

        df['round_num'] = score_info_df.iloc[:,0]
        df['attacking_team_id'] = score_info_df.iloc[:,1]
        df['round_name_guid'] = score_info_df.iloc[:,2]
        df['team_id_1'] = score_info_df.iloc[:,3]
        df['payload_distance_1'] = score_info_df.iloc[:,4]
        df['time_banked_1'] = score_info_df.iloc[:,5]
        df["score_1"] = score_info_df.iloc[:,6]
        df["control_info_1"] = score_info_df.iloc[:,7]
        df['team_id_2'] = score_info_df.iloc[:,10]
        df['payload_distance_2'] = score_info_df.iloc[:,11]
        df["time_banked_2"] = score_info_df.iloc[:,12]
        df['score_2'] = score_info_df.iloc[:,13]
        df['control_info_2'] = score_info_df.iloc[:,14]

        df['context'] = df['context'].map(lambda x: str(x)[9:-2])

        for i, row in df.iterrows():
            match_game_number = row['info'].split(',')[7].split(":")[1]
            df.at[i, 'match_game_number'] = match_game_number
            if not isinstance(row['round_name'], str):
                continue
            else:
                name = row['round_name'].split(',')[2].split(':')[1][1:-1]
                df.at[i, 'round_name'] = name


        df.drop(columns = ['schema_name','info', 'score_info'], inplace = True)

        if compression:
            df.to_csv(folder + "/cleaned_game_info.csv.gz", compression='gzip')
        else:
            df.to_csv(folder + "/cleaned_game_info.csv")
    else:
        df = pd.read_csv(folder + "/" + game_info_PATH, sep = '\t', compression = "gzip")
        df.to_csv(folder + "/game_info.csv")

def read_game_result(folder, write, compression):
    if write:
        df = pd.read_csv(folder + "/" + game_result_PATH, sep = '\t', compression = "gzip")

        map_info_df = df['info'].str.extract('("map_guid":\d*,)("map_type":"[^"]*",)("round":\d*)')
        map_info_df.iloc[:,0] = map_info_df.iloc[:,0].map(lambda x: str(x)[11:-1])
        map_info_df.iloc[:,1] = map_info_df.iloc[:,1].map(lambda x: str(x)[12:-2])
        map_info_df.iloc[:,2] = map_info_df.iloc[:,2].map(lambda x: str(x)[8:])

        df['map_guid'] = map_info_df.iloc[:,0]
        df['map_type'] = map_info_df.iloc[:,1]
        df['round'] = map_info_df.iloc[:,2]

        info_df = df['score_info'].str.replace(r'(,[^:]*:|{[^:]*:)', ',')
        score_info_df = info_df.str.split(",", expand =True)

        score_info_df.iloc[:,2] = score_info_df.iloc[:,2].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,5] = score_info_df.iloc[:,5].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,11] = score_info_df.iloc[:,11].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,12] = score_info_df.iloc[:,12].map(lambda x: str(x)[:-2])
        score_info_df.iloc[:,13] = score_info_df.iloc[:,13].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,19] = score_info_df.iloc[:,19].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,20] = score_info_df.iloc[:,20].map(lambda x: str(x)[:-3])
        score_info_df.iloc[:,22] = score_info_df.iloc[:,22].map(lambda x: str(x)[1:-1])
        score_info_df.iloc[:,23] = score_info_df.iloc[:,23].map(lambda x: str(x)[:-3])

        cols = [0, 4, 10, 18, 21]
        score_info_df.drop(score_info_df.columns[cols], axis = 1, inplace = True)

        df['round_num'] = score_info_df.iloc[:,0]
        df['attacking_team_id'] = score_info_df.iloc[:,1]
        df['round_name_guid'] = score_info_df.iloc[:,2]
        df['team_id_1'] = score_info_df.iloc[:,3]
        df['payload_distance_1'] = score_info_df.iloc[:,4]
        df['time_banked_1'] = score_info_df.iloc[:,5]
        df["score_1"] = score_info_df.iloc[:,6]
        df["control_info_1"] = score_info_df.iloc[:,7]
        df['team_id_2'] = score_info_df.iloc[:,10]
        df['payload_distance_2'] = score_info_df.iloc[:,11]
        df["time_banked_2"] = score_info_df.iloc[:,12]
        df['score_2'] = score_info_df.iloc[:,13]
        df['control_info_2'] = score_info_df.iloc[:,14]

        df.drop(columns = ['schema_name','info', 'end_reason'], inplace = True)
        df = df[df['total_game_time_ms'] > 0]
        if compression:
            df.to_csv(folder + "/cleaned_game_result.csv.gz", compression = 'gzip')
        else:
            df.to_csv(folder + "/cleaned_game_result.csv")
    else:
        df = pd.read_csv(folder + "/" + game_result_PATH, sep = '\t', compression = "gzip")
        df.to_csv(folder + "/game_result.csv")

def read_hero_switch(folder , write, compression):
    if write:
        df = pd.read_csv(folder + "/" + hero_switch_PATH, sep = '\t', compression = "gzip")
        game_results = pd.read_csv(folder + "/" + cleaned_game_result_PATH)

        hero_switch_df = df['info'].str.extract('("map_guid":\d*,)("map_type":"[^"]*",)("round":\d*)')
        hero_switch_df.iloc[:,0] = hero_switch_df.iloc[:,0].map(lambda x: str(x)[11:-1])
        hero_switch_df.iloc[:,1] = hero_switch_df.iloc[:,1].map(lambda x: str(x)[12:-2])
        hero_switch_df.iloc[:,2] = hero_switch_df.iloc[:,2].map(lambda x: str(x)[8:])
        df['map_guid'] = hero_switch_df.iloc[:,0]
        df['map_type'] = hero_switch_df.iloc[:,1]
        df['round'] = hero_switch_df.iloc[:,2]

        for i, row in df.iterrows():
            match_game_number = row['info'].split(',')[7].split(":")[1]
            df.at[i, 'match_game_number'] = match_game_number

        df['old_hero_guid'] = df['old_hero_guid'].astype(str)
        df['new_hero_guid'] = df['new_hero_guid'].astype(str)
        df['esports_match_id'] = df['esports_match_id'].astype(int)
        df['map_guid'] = df['map_guid'].astype(str)
        game_results['esports_match_id'] = game_results['esports_match_id'].astype(int)
        game_results['map_guid'] = game_results['map_guid'].astype(str)

        player_df = df['player'].str.extract('("battletag":"[^"]*",)("esports_player_id":\d*)')
        player_df.iloc[:,0] = player_df.iloc[:,0].map(lambda x: str(x)[13:-2])
        player_df.iloc[:,1] = player_df.iloc[:,1].map(lambda x: str(x)[20:])
        df['battletag'] = player_df.iloc[:,0]
        df['esports_player_id'] = player_df.iloc[:,1]
        df.drop(columns = ['schema_name','info', 'player'], inplace = True)

        game_info = pd.read_csv(folder + "/plain_game_info.csv")
        game_info['esports_match_id'] = game_info['esports_match_id'].astype(int)
        game_info['round_x'] = game_info['round_x'].astype(str)
        game_info['match_game_number'] = game_info['match_game_number'].astype(str)

        #Find the heroes that each player is playing
        team_players = pd.read_csv(DATA_PATH + "TeamRosters.csv", sep = ",")
        team_players['Players'] = team_players['Players'].str.lower()
        hero_ids = pd.read_csv(DATA_PATH + "payload_guids_heroes.csv", sep = ",")
        map_ids = pd.read_csv(DATA_PATH + "cleaned_payload_guids_maps.csv", sep = ",")
        temp = df['battletag'].str.split("#", expand = True)
        df['short battletag']= temp.iloc[:,0].str.lower()
        hero_ids['hero_guid'] = hero_ids['hero_guid'].astype(str)
        hero_ids['hero_guid'] = hero_ids['hero_guid'].astype(str)
        map_ids['guid'] = map_ids['guid'].astype(str)
        df = df.merge(team_players, how = 'left', left_on = 'short battletag', right_on = "Players")
        df = df.merge(hero_ids, how = 'left', left_on = 'new_hero_guid', right_on = 'hero_guid')
        df = df.merge(hero_ids, how = 'left', left_on = 'old_hero_guid', right_on = 'hero_guid')
        df = df.merge(map_ids, how = 'left', left_on = 'map_guid', right_on = 'guid')
        df.rename(columns = {'Hero_x': 'new hero', 'Hero_y': 'old hero'}, inplace = True)
        df.drop(columns = ['hero_guid_x', 'hero_guid_y', 'Unnamed: 0', 'guid'], inplace = True)
        df = df.merge(game_results, how = 'inner', on = ['esports_match_id', 'map_guid'])
        df.rename(columns = {'time_c_y': 'end time', 'time_c_x': 'switch time'}, inplace = True)
        df.drop(df.columns[20:], axis = 1, inplace = True)
        df = df.merge(game_info, how = 'left', on = ['esports_match_id', 'round_x', 'match_game_number'])
        df.drop_duplicates(inplace = True)
        df.drop_duplicates(subset = ['short battletag', 'new hero', 'old hero', 'map_name', 'time_x'], keep = 'last', inplace = True)
        df.sort_values(by = 'time_x', ascending = True, inplace = True)
        df = df[pd.notnull(df['Team'])]

        if compression:
            df.to_csv(folder + "/cleaned_hero_switch.csv.gz", compression = 'gzip')
        else:
            df.to_csv(folder + "/cleaned_hero_switch.csv")
    else:
        df = pd.read_csv(folder + "/" + hero_switch_PATH, sep = '\t', compression = "gzip")
        df.to_csv(folder + "/hero_switch.csv")

def read_kills(folder, write, compression):
    if write:
        df = pd.read_csv(folder + "/" + kill_PATH, sep = '\t', compression = "gzip")

        hero_switch_df = df['info'].str.extract('("map_guid":\d*,)("map_type":"[^"]*",)("round":\d*)')
        hero_switch_df.iloc[:,0] = hero_switch_df.iloc[:,0].map(lambda x: str(x)[11:-1])
        hero_switch_df.iloc[:,1] = hero_switch_df.iloc[:,1].map(lambda x: str(x)[12:-2])
        hero_switch_df.iloc[:,2] = hero_switch_df.iloc[:,2].map(lambda x: str(x)[8:])
        df['map_guid'] = hero_switch_df.iloc[:,0]
        df['map_type'] = hero_switch_df.iloc[:,1]
        df['round'] = hero_switch_df.iloc[:,2]

        killed_id_df = df['killed_player_id'].str.extract('("seq":\d*)')
        killed_id_df.iloc[:,0] = killed_id_df.iloc[:,0].map(lambda x: str(x)[6:])
        df['killed_player_id'] = killed_id_df.iloc[:,0]

        final_blow_player_id_df = df['final_blow_player_id'].str.extract('("seq":\d*)')
        final_blow_player_id_df.iloc[:,0] = final_blow_player_id_df.iloc[:,0].map(lambda x: str(x)[6:])
        df['final_blow_player_id'] = final_blow_player_id_df.iloc[:,0]

        recent_damagers_df = pd.DataFrame(df['recent_damagers'].str.findall('("seq":\d*)').tolist(), columns = ['rd_1','rd_2', 'rd_3', 'rd_4', 'rd_5', 'rd_6'])

        recent_damagers_df.iloc[:,0] = recent_damagers_df.iloc[:,0].map(lambda x: str(x)[6:])
        recent_damagers_df.iloc[:,1] = recent_damagers_df.iloc[:,1].map(lambda x: str(x)[6:])
        recent_damagers_df.iloc[:,2] = recent_damagers_df.iloc[:,2].map(lambda x: str(x)[6:])
        recent_damagers_df.iloc[:,3] = recent_damagers_df.iloc[:,3].map(lambda x: str(x)[6:])
        recent_damagers_df.iloc[:,4] = recent_damagers_df.iloc[:,4].map(lambda x: str(x)[6:])
        recent_damagers_df.iloc[:,5] = recent_damagers_df.iloc[:,5].map(lambda x: str(x)[6:])

        df['damager_1'] = recent_damagers_df.iloc[:,0]
        df['damager_2'] = recent_damagers_df.iloc[:,1]
        df['damager_3'] = recent_damagers_df.iloc[:,2]
        df['damager_4'] = recent_damagers_df.iloc[:,3]
        df['damager_5'] = recent_damagers_df.iloc[:,4]
        df['damager_6'] = recent_damagers_df.iloc[:,5]

        df.drop(columns = ['schema_name', 'death_yaw', 'killer_yaw', 'info', 'killed_player_id', 'final_blow_player_id', 'recent_damagers'], inplace = True)
        if compression:
            df.to_csv(folder + "/cleaned_kills.csv.gz", compression = 'gzip')
        else:
            df.to_csv(folder + "/cleaned_kills.csv")

def read_player_hero_stats(folder, write, compression):
    return None

def read_player_status(folder, write, compression):
    if write:
        df = pd.read_csv(folder + "/" + player_status_PATH, sep = '\t', compression = "gzip")

        hero_switch_df = df['info'].str.extract('("map_guid":\d*,)("map_type":"[^"]*",)("round":\d*)')
        hero_switch_df.iloc[:,0] = hero_switch_df.iloc[:,0].map(lambda x: str(x)[11:-1])
        hero_switch_df.iloc[:,1] = hero_switch_df.iloc[:,1].map(lambda x: str(x)[12:-2])
        hero_switch_df.iloc[:,2] = hero_switch_df.iloc[:,2].map(lambda x: str(x)[8:])
        df['map_guid'] = hero_switch_df.iloc[:,0]
        df['map_type'] = hero_switch_df.iloc[:,1]
        df['round'] = hero_switch_df.iloc[:,2]

        statuses_df = df['statuses'].str.replace('\"player\":{\"player_id\":{\"src\":\d*,\"seq\":\d*},\"battletag\":\"[^\"]*\",\"esports_player_id\":\d*}},', '')
        statuses_df = statuses_df.str.replace(':{\"src\":\d*,\"seq\"','')
        statuses_df = statuses_df.str.split(",", expand =True)

        for i in range(0,12):
            val = i

            df['player_id_seq' + '_' + str(i)] = statuses_df.iloc[:,(16*i)].map(lambda x: str(x)[14:-1])
            df['hero_guid'+ '_' + str(i)] = statuses_df.iloc[:,(16*i + 2)].map(lambda x: str(x)[12:])
            df['health' + '_' + str(i)] = statuses_df.iloc[:,(16*i + 3)].map(lambda x: str(x)[9:])
            df['armor' + '_' + str(i)] = statuses_df.iloc[:,(16*i + 4)].map(lambda x: str(x)[8:])
            df['shield'+ '_' + str(i)] = statuses_df.iloc[:,(16*i + 5)].map(lambda x: str(x)[10:])
            df['max_health'+ '_' + str(i)] = statuses_df.iloc[:,(16*i + 6)].map(lambda x: str(x)[13:])
            df['max_armor'+ '_' + str(i)] = statuses_df.iloc[:,(16*i + 7)].map(lambda x: str(x)[12:])
            df['max_shield'+ '_' + str(i)] = statuses_df.iloc[:,(16*i + 8)].map(lambda x: str(x)[14:])
            df['ultimate_percent'+ '_' + str(i)] = statuses_df.iloc[:,(16*i + 10)].map(lambda x: str(x)[19:])
            df['is_dead'+ '_' + str(i)] = statuses_df.iloc[:,(16*i + 12)].map(lambda x: str(x)[10:])
        if compression:
            df.to_csv(folder + "/cleaned_player_status.csv.gz", compression = 'gzip')
        else:
            df.to_csv(folder + "/cleaned_player_status.csv")

def read_team_stats(folder, write, compression):
    if write:
        df = pd.read_csv(folder + "/" + team_stats_PATH, sep = '\t', compression = "gzip")
        df.drop_duplicates(subset = ['stat', 'team', 'esports_match_id'], keep = 'first', inplace = True)

        TEAM_ID_df = df['team'].str.extract('(team_id":"[^"]*",)("esports_team_id":\d*)')
        TEAM_ID_df.iloc[:,0] = TEAM_ID_df.iloc[:,0].map(lambda x: str(x)[10:-2])
        TEAM_ID_df.iloc[:,1] = TEAM_ID_df.iloc[:,1].map(lambda x: str(x)[18:])

        STATS_df = df['stat'].str.extract('(short_stat_guid":\d*,)("amount":\d*\.*\d*)')
        STATS_df.iloc[:,0] = STATS_df.iloc[:,0].map(lambda x: str(x)[17:-1])
        STATS_df.iloc[:,1] = STATS_df.iloc[:,1].map(lambda x: str(x)[9:])

        df['team_id'] = TEAM_ID_df.iloc[:,0]
        df['esports_team_id'] = TEAM_ID_df.iloc[:,1]
        df['context'] = df['context'].map(lambda x: str(x)[9:-2])
        df['short_stat_guid'] = STATS_df.iloc[:,0]
        df['amount'] = STATS_df.iloc[:,1]

        #df.drop(columns = ['schema_name','info', 'team', 'stat'], inplace = True)
        if compression:
            df.to_csv(folder+"/cleaned_team_stats.csv.gz", compression = 'gzip')
        else:
            df.to_csv(folder+"/cleaned_team_stats.csv")

def read():
    folder = DATA_PATH + '20190429'
    #game_info
    read_game_info(folder = folder, write = True, compression = False)
    fix_game_info(folder)

    #game_result
    read_game_result(folder = folder, write = True, compression = False)

    #hero_switch
    read_hero_switch(folder = folder, write = True, compression = True)
    read_hero_switch(folder = folder, write = True, compression = False)

    #kill
    #read_kills(folder = folder, write = False, compression = True)

    #player_hero_stats
    #TODO

    #player_status
    #read_player_status(folder = folder, write = False, compression = True)

    #team_stats
    #read_team_stats(folder = folder, write = False, compression = True)

def decompress(filename):
    df = pd.read_csv(filename, sep = '\t', compression = "gzip")
    df.to_csv(filename+".csv")

if __name__ == '__main__':
    read()
