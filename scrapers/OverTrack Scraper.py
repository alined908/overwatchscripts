# import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from termcolor import colored
import time
import pandas
import urllib
import requests
import collections
from bs4 import BeautifulSoup

#Grab scrim links
def grab_matches():

    ids = []
    for i in range(54, 0,-1):
        id = "game-" + str(i)
        ids.append(id)

    driver = webdriver.Chrome("C:/Users/Daniel Lee/Desktop/chromedriver")
    driver.get('https://overtrack.gg/games/shu-sqd5u2wj6dc982ddhxpt4b')
    time.sleep(3)
    site = driver.page_source
    driver.close()
    soup = BeautifulSoup(site, 'html.parser')
    match_links = []
    flag = False

    for id in ids:
        row = soup.find("tr", {"id" : str(id)})

        if row.find("td", class_ = "text-unknown text-left") != None:
            flag = True
            #print("bye")

        if flag is True:
            match_links.append("kappa")
            flag = False
        else:
            link = row.find("p").get_text()
            match_links.append("https://overtrack.gg/game/" + link.strip())

    return match_links


def main():

    matches = grab_matches()
    master_master_array = []

    for index0, match in enumerate(matches):

        if match == "kappa":
            continue
        #Get Javascript info
        driver = webdriver.Chrome("C:/Users/Daniel Lee/Desktop/chromedriver")
        driver.get(match)
        time.sleep(3)
        site = driver.page_source
        soup = BeautifulSoup(site, 'html.parser')

        #Obtain info of scrims
        scrim_info = []
        scrim_info_html = soup.find("div", class_ = 'pull-left col-lg-9').findChildren()
        for child in scrim_info_html:
            scrim_info.append(child.get_text())
        map_name = scrim_info[0]
        match_id = str(index0 + 27)
        #print("Match ID:" , match_id)
        #print("Map Name: " + map_name)
        map_type = scrim_info[1]
        #print("Map Type: " + map_type)
        #map_length = scrim_info[2]
        #print("Map_Length: " + map_length)
        scrim_date = scrim_info[3]
        date = scrim_date.strip().split()[2]
        #print("Scrim Date: " + date)

        #Get number of stages and name
        stages_bar_html = soup.find("ul", class_ = "nav nav-tabs")
        stages_list_item = stages_bar_html.find_all("li")
        stages_name = []
        stages_page_source = []

        for item in stages_list_item[1:-1]:
            stages_name.append(item.find("a").get_text())
        #print("Stages_Name:", stages_name)

        #Get Html of all stages
        for i in range(2, 2 + len(stages_name)):
            try:
                stages_page_source.append(driver.find_element_by_xpath("//timeline[@id='stage_" + str(i-2) + "']").get_attribute('innerHTML'))
            except ElementNotVisibleException or NoSuchElementException:
                pass

        full_hero_time_played_dict = {}

        master_dict = {}

        #Go through each stage
        for index, stage in enumerate(stages_page_source):

            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            soup = BeautifulSoup(stage, 'html.parser')
            player_rows = soup.find("div", class_ = "timeline-players").find_all("div", class_ = "col-xs-12")
            players = player_rows[1:13]

            #Stage duration
            ticks = soup.find("g", {"transform": "translate(0,19)"})
            ticker = ticks.find_all("g", {"class":"tick"})
            round_duration = ticker[-1].get_text()
            round_duration_in_secs = 60 * int(round_duration.split(':')[0]) + int(round_duration.split(':')[1])
            #print(round_duration)
            #print("Stage_Duration_In_Seconds:", round_duration_in_secs)

            #go through each player with info given [hero name, time played, kills, deaths, ultimates, TTCU]
            #To do later Fight Win%, First Kill%, First Death%,
            for player in players:

                #get player's name
                player_name = player.find('b', class_ = lambda x: x and 'text-right' in x).get_text()
                #print("===============================================================================")
                #print("Player Name:" , player_name)
                #print("")

                #get player's heroes played & time of swap
                heroes = {}
                hero_play_order_reversed = []
                heroes_played_html = player.find_all('image', class_ = "hero-image")
                count = 0
                for hero in reversed(heroes_played_html):
                    hero_name = hero['xlink:href'][21 : -4]
                    #print(hero_name)
                    hero_play_order_reversed.append(hero_name)
                    if(count == 0):
                        heroes[hero_name] = [[float(hero['x'].strip('%')), 100]]
                    else:
                        if hero_name in heroes:
                            heroes[hero_name].insert(0,[float(hero['x'].strip('%')), end_time])
                        else:
                            heroes[hero_name] = [[float(hero['x'].strip('%')), end_time]]
                    end_time = float(hero['x'].strip('%'))
                    count += 1
                dict_heroes = list(heroes.keys())
                #print("Heroes played:", heroes)

                #get player's seconds played per hero
                hero_time_played_dict = {}
                for key in heroes:
                    count = 0
                    for item in heroes[key]:
                        count += (item[1] - item[0])
                    seconds = (count/100) * round_duration_in_secs
                    hero_time_played_dict[key] = round(seconds, 2)
                #print("Hero time:" , hero_time_played_dict)

                #get player's death timestamps and death #
                death_dict = {}
                death_count = {}
                deaths = player.find_all('image', class_ = lambda x:x and 'death' in x)
                death_timestamps = [float(x["x"].strip('%')) for x in deaths]

                for timestamp in death_timestamps:
                    for key in dict_heroes:
                        for item in heroes[key]:
                            if item[0] <= timestamp < item[1]:
                                if key in death_dict.keys():
                                    death_dict[key].append(timestamp)
                                else:
                                    death_dict[key] = [timestamp]

                for key in heroes.keys():
                    if key not in death_dict.keys():
                        death_count[key] = 0
                    else:
                        death_count[key] = len(death_dict[key])

                #print("Death Timestamps:", death_dict)
                #print("Deaths:", death_count)

                #get player's kill timestamps and kill # and k/10
                kill_dict = {}
                kill_count = {}
                kills = player.find_all('text', class_ = lambda x:x and 'kill' in x)
                kill_timestamps = [float(x["x"].strip('%')) for x in kills]

                for timestamp in kill_timestamps:
                    for key in dict_heroes:
                        for item in heroes[key]:
                            if item[0] <= timestamp < item[1]:
                                if key in kill_dict.keys():
                                    kill_dict[key].append(timestamp)
                                else:
                                    kill_dict[key] = [timestamp]

                for key in heroes.keys():
                    if key not in kill_dict.keys():
                        kill_count[key] = 0
                    else:
                        kill_count[key] = len(kill_dict[key])

                #print("Kill Timestamps: ", kill_dict)
                #print("Kills:", kill_count)

                #get player's # of ultimates, TTCU, TTUU (Time to Use Ultimate)
                #DVA ults are glitched
                ults_gain_html = player.find_all('image', class_ = lambda x:x and 'ult-icon-gain' in x)
                ult_dict = {}
                ult_gain_timestamps = [float(x["x"].strip('%')) for x in ults_gain_html]

                for ult_timestamp in ult_gain_timestamps:
                    for key in dict_heroes:
                        for item in heroes[key]:
                            if item[0] <= ult_timestamp < item[1]:
                                if key in ult_dict.keys():
                                    ult_dict[key].append(ult_timestamp)
                                else:
                                    ult_dict[key] = [ult_timestamp]
                #print("Ult gain timestamps:" , ult_gain_timestamps)
                #print("Ult gain Dict:", ult_dict)

                ults_used_html = player.find_all('image', class_ = lambda x:x and 'ult-icon-use' in x)
                ults_used_timestamps = [float(x["x"].strip('%')) for x in ults_used_html]
                #print("Ults used timestamps:", ults_used_timestamps)

                #TTCU
                ttcu_dict = {}
                previous_hero = hero_play_order_reversed[-1]
                for index1, ult_gain in enumerate(ult_gain_timestamps):
                    for key in dict_heroes:
                        for item in heroes[key]:
                            if item[0] <= ult_gain <= item[1]:
                                current_hero = key
                                if key in ttcu_dict.keys():
                                    if previous_hero != current_hero:
                                        #print('a' , ult_gain, item[0])
                                        ttcu_dict[key].append(round((ult_gain - item[0])/100 * round_duration_in_secs, 2))
                                        previous_hero = current_hero
                                    else:
                                        #print('b', ult_gain, ults_used_timestamps[index1 -1])
                                        ttcu_dict[key].append(round((ult_gain - ults_used_timestamps[index1 - 1])/100 * round_duration_in_secs, 2))
                                else:
                                    if index1 == 0:
                                        #print('c', ult_gain)
                                        ttcu_dict[key] = [round(ult_gain/100 * round_duration_in_secs, 2)]
                                    else:
                                        #print('d', ult_gain, item[0])
                                        ttcu_dict[key] = [round((ult_gain - item[0])/100 * round_duration_in_secs, 2)]
                                        previous_hero = current_hero

                #print("TTCU in seconds:", ttcu_dict)

                ult_number_dict = {}
                for hero in ult_dict.keys():
                    ult_number_dict[hero] = len(ult_dict[hero])

                #print("Ultimates:", ult_number_dict)

                #TTUU
                ttuu_html = player.find_all('rect', class_ = lambda x:x and 'ult-period' in x)
                position_ttuu = [float(x["x"].strip('%')) for x in ttuu_html]
                ttuu = [int(x["data-duration"])/1000 for x in ttuu_html]
                ttuu_dict = {}

                for index2, time_stamp in enumerate(position_ttuu):
                    for key in dict_heroes:
                        for item in heroes[key]:
                            if item[0] <= time_stamp <= item[1]:
                                if key in ttuu_dict.keys():
                                    ttuu_dict[key].append(ttuu[index2])
                                else:
                                    ttuu_dict[key] = [ttuu[index2]]

                #print("TTUU in seconds:", ttuu_dict)

                #TEST
                #print("Player Name:" , player_name)
                #print("Map:", map_name)
                #print("Hero time:" , hero_time_played_dict)
                #print("Deaths:", death_count)
                #print("Kills:", kill_count)
                #print("Ultimates:", ult_number_dict)
                #print("TTCU in seconds:", ttcu_dict)
                #print("TTUU in seconds:", ttuu_dict)


                if index == 0:
                    master_dict[player_name] = {"Hero Time": hero_time_played_dict, "Kills": kill_count, "Deaths": death_count, "Ultimates": ult_number_dict, "K/10":{}, "D/10": {}, "U/10": {}, "TTCU" : ttcu_dict, "TTUU" : ttuu_dict}

                else:
                    for master_key in master_dict.keys():
                        if master_key == player_name:
                            for key in hero_time_played_dict.keys():
                                if key in master_dict[master_key]["Hero Time"].keys():
                                    master_dict[master_key]["Hero Time"][key] += round(hero_time_played_dict[key], 2)
                                else:
                                    master_dict[master_key]["Hero Time"][key] = round(hero_time_played_dict[key], 2)
                            for key in kill_count.keys():
                                if key in master_dict[master_key]["Kills"].keys():
                                    master_dict[master_key]["Kills"][key] += kill_count[key]
                                else:
                                    master_dict[master_key]["Kills"][key] = kill_count[key]
                            for key in death_count.keys():
                                if key in master_dict[master_key]["Deaths"].keys():
                                    master_dict[master_key]["Deaths"][key] += death_count[key]
                                else:
                                    master_dict[master_key]["Deaths"][key] = death_count[key]
                            for key in ult_number_dict.keys():
                                if key in master_dict[master_key]["Ultimates"].keys():
                                    master_dict[master_key]["Ultimates"][key] += ult_number_dict[key]
                                else:
                                    master_dict[master_key]["Ultimates"][key] = ult_number_dict[key]
                            for key in ttcu_dict.keys():
                                if key in master_dict[master_key]["TTCU"].keys():
                                    for item in ttcu_dict[key]:
                                        master_dict[master_key]["TTCU"][key].append(item)
                                else:
                                    master_dict[master_key]["TTCU"][key] = ttcu_dict[key]
                            for key in ttcu_dict.keys():
                                if key in master_dict[master_key]["TTUU"].keys():
                                    for item in ttuu_dict[key]:
                                        master_dict[master_key]["TTUU"][key].append(round(item, 2))
                                else:
                                    master_dict[master_key]["TTUU"][key] = ttuu_dict[key]
                            if index + 1 == len(stages_page_source):
                                for hero in master_dict[master_key]["Hero Time"].keys():
                                    master_dict[master_key]["K/10"][hero] = round(((master_dict[master_key]["Kills"][hero])/(master_dict[master_key]["Hero Time"][hero]) * 600), 2)
                                    master_dict[master_key]["D/10"][hero] = round(((master_dict[master_key]["Deaths"][hero])/(master_dict[master_key]["Hero Time"][hero]) * 600), 2)
                                    if hero in master_dict[master_key]["Ultimates"].keys():
                                        master_dict[master_key]["U/10"][hero] = round(((master_dict[master_key]["Ultimates"][hero])/(master_dict[master_key]["Hero Time"][hero]) * 600), 2)
                                    else:
                                        master_dict[master_key]["U/10"][hero] = "N/A"

        count = 0
        master_array = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        #print(master_dict)
        #for player
        for index5, master_key in enumerate(master_dict.keys()):
            #for heroes played
            for index4, key in enumerate(master_dict[master_key]["Hero Time"].keys()):
                #for stat
                for index3, key1 in enumerate(master_dict[master_key].keys()):
                    if index3 == 0:
                        master_array[count] += [match_id, date, map_name, master_key, key]
                    if key not in master_dict[master_key][key1]:
                        if key1 == "Ultimates":
                            master_array[count].append(0)
                        else:
                            master_array[count].append("N/A")
                    else:
                        master_array[count].append(master_dict[master_key][key1][key])
                count+=1
        real_master_array = [x for x in master_array if x!= []]
        #print(real_master_array)
        master_master_array += real_master_array

    if index0 + 1 == len(matches):
        pd = pandas.DataFrame(master_master_array)
        title = ("example1.csv").replace("\n", "")
        pd.to_csv(title)


main()
