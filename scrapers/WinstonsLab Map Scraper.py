# import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
import time
import pandas
import urllib
from bs4 import BeautifulSoup

#get those matches
def grab_matches():

    #id of matches we want
    ids = []
    for i in range(164,532,2):
        id = "tzDate_" + str(i)
        ids.append(id)

    match_links = []
    match_page = urllib.request.urlopen('https://www.winstonslab.com/events/event.php?id=86')
    soup = BeautifulSoup(match_page, 'html.parser')

    #get match link of matches
    for id in ids:
        row = soup.find("a", {"id" : str(id)})
        link = row['href']
        match_links.append("https://www.winstonslab.com" + link)

    return match_links

#get info on maps
def maps(match):

    match_page = urllib.request.urlopen(match)
    soup = BeautifulSoup(match_page, 'html.parser')
    map_names = []
    button_htmls = []
    map_list = soup.find_all("div", {"class": "map-wrapper"})

    for map in map_list:
        map_names.append(map.find("div", {"class": "map"})["title"])

    number_of_maps = len(map_list)

    return number_of_maps, map_names, map_list

#Find stats, data, and team names
def find_info(match):

    #maps info
    number_of_maps, map_names, map_list = maps(match)

    #sellenium click map stats + detailed stats
    driver = webdriver.Chrome("C:/Users/Daniel Lee/Desktop/chromedriver")
    driver.get(match)

    for i in range(1, number_of_maps*2, 2):
        try:
            button = driver.find_element_by_xpath("//div[@class='match-div']//div[" + str(i) + "]//div[3]//button[1]")
            button.click()
            button2 = driver.find_element_by_xpath("//div[@class='match-div']//div[" + str(i+1) + "]//div[1]//button[2]")
            button2.click()
        except ElementNotVisibleException or NoSuchElementException:
            pass
        time.sleep(4)

    site = driver.page_source
    driver.close()
    #beautifulsoup find relevant rows
    soup = BeautifulSoup(site, 'html.parser')
    data = []
    true_data = []
    map1, map2, map3, map4, map5 = [], [], [], [], []

    for i in range(1, number_of_maps + 1):
        data = []

        table = soup.find("div", {"id": "detailedStatsDiv_" + str(i)})
        if (table == None):
            continue
        body = table.find('tbody')
        if (body == None):
            continue
        rows = body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])

        #filter out NEDs
        for row in data:
            row = [map_names[i - 1]] + row
            if(i == 1):
                map1.append(row)
            if(i == 2):
                map2.append(row)
            if(i == 3):
                map3.append(row)
            if(i == 4):
                map4.append(row)
            if(i == 5):
                map5.append(row)

    if (number_of_maps == 3):
        merged_maps_stats = map1 + map2 + map3
    if (number_of_maps == 4):
        merged_maps_stats = map1 + map2 + map3+ map4
    if (number_of_maps == 5):
        merged_maps_stats = map1 + map2 + map3+ map4 + map5

    #find team names & Date
    row1 = soup.find('div', {'class' : 'team1-name'})
    team1 = str(row1.get_text())
    row2 = soup.find('div', {'class' : 'team2-name'})
    team2 = str(row2.get_text())
    full_date = str(soup.find('span', {'id' : 'tzDate_1'}).get_text()).split(" ", 4)
    date = full_date[1] + " " + full_date[2] + " " + full_date[3]

    return date, team1, team2, merged_maps_stats

def main():

    match_links = grab_matches()

    #loop through matches
    for match in match_links:

        date, team1, team2, merged_maps_stats = find_info(match)

        #export to csvs with format Date - Team vs Team
        pd = pandas.DataFrame(merged_maps_stats)
        title = (date + " " + team1 + " vs " + team2 + ".csv").replace("\n", "")
        pd.to_csv(title)

main()
