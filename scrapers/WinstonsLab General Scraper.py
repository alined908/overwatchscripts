# import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas
import urllib
from bs4 import BeautifulSoup

#get those matches
def grab_matches():

    #id of matches we want
    ids = []
    for i in range(176,533,2):
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

#Find stats, data, and team names
def find_info(match):

    #sellenium click detailed stats
    driver = webdriver.Chrome("C:/Users/Daniel Lee/Desktop/chromedriver")
    driver.get(match)
    button = driver.find_element_by_xpath("//div[@class='side-by-side-stats spoiler']//div//button[@class='multiple-choice-button showDetailedStatsBut'][contains(text(),'Detailed Stats')]")
    button.click()
    time.sleep(5)
    site = driver.page_source

    #beautifulsoup find relevant rows
    soup = BeautifulSoup(site, 'html.parser')
    data = []
    table = soup.find("div", {"id": "detailedStatsDiv_0"})
    body = table.find('tbody')
    rows = body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])

    #filter out NEDs
    true_data = []
    for row in data:
        if 'NED' not in row:
            true_data.append(row)

    #find team names & Date
    row1 = soup.find('div', {'class' : 'team1-name'})
    team1 = str(row1.get_text())
    row2 = soup.find('div', {'class' : 'team2-name'})
    team2 = str(row2.get_text())
    full_date = str(soup.find('span', {'id' : 'tzDate_1'}).get_text()).split(" ", 4)
    date = full_date[1] + " " + full_date[2] + " " + full_date[3]
    return date, team1, team2, true_data

if __name__ == '__main__':
    match_links = grab_matches()
    #loop through matches
    for match in match_links:
        #stats rows
        date, team1, team2, stats = find_info(match)
        #export to csvs with format Date - Team vs Team
        pd = pandas.DataFrame(stats)
        title = (date + " " + team1 + " vs " + team2 + ".csv").replace("\n", "")
        pd.to_csv(title)
