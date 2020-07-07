#!/usr/bin/env python
# coding: utf-8

# ## Importing the required modules

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
#Setting the years for the scrape
years = [n for n in range (2017, 2020)]
#Main website we are scrping from
bref = 'https://www.baseball-reference.com'

#Creating a list of urls that contain pitcher and batter stats for each year indicated above
batter_urls = []
pitcher_urls =[]
stat_url = 'https://www.baseball-reference.com/leagues/MLB/'
batters = '-standard-batting.shtml'
pitchers = '-standard-pitching.shtml'
for year in years:
    bat_url = stat_url + str(year) + batters
    batter_urls.append(bat_url)
    pitch_url = stat_url + str(year) + pitchers
    pitcher_urls.append(pitch_url)


player_links =[]



batters = []

def batter_statistics(list_of_urls):
    for url in list_of_urls:
        #Navigating to the correct table on each year's page for batter stats
        page = requests.get(url).text
        table_code = page[page.find('<table class="sortable stats_table" id="players_standard_batting"'):]
        soup = BeautifulSoup(table_code, 'lxml')
        div_tags = soup.find('tbody')
        players = [t for t in div_tags.find_all('tr')]
        #for each players on the page, we create a dictionary containing all relevant information
        for player in players:
            team = player.find('td', {'data-stat': 'team_ID'})
            #Skips players without a team listed
            if team == None:
                continue
            team_txt = team.get_text()
            #Skips aggregate data in the event a player played for more than one team in a year
            if team_txt == 'TOT' or team_txt == '':
                continue
            #Creates a template dictionary so that we only recover relevant stats
            batter_stats = {'team_ID':0, 'G':0, 'AB':0, 'R':0, 'H':0, '2B':0, '3B':0, 'HR':0, 'RBI':0, 'SB':0,
                        'BB':0, 'SO':0, 'onbase_perc':0, 'slugging_perc':0,}
            #Our 0's are replaced by the actual statistics
            for key in batter_stats.keys():
                txt = player.find('td', {'data-stat': key})
                batter_stats[key] = txt.get_text()
            link_tag = player.find('a')
            ending = link_tag.get('href')
            name = link_tag.get_text().replace('\xa0', ' ')
            link = bref+ending
            #player name added to dictionary
            batter_stats['Name'] = name
            #collects a link to each player's personal page so that we can later retrieve personal info (such as hometown)
                #only collects the link if it hasn't been collected before
            batter_stats['link'] = link
            if link not in player_links:
                player_links.append(link)
            batter_stats['Year'] = url[47:51]
            #Editing some of the statistics to be more easily readable
            if batter_stats['onbase_perc'] != '':
                batter_stats['onbase_perc'] = '0' + batter_stats['onbase_perc']
            elif batter_stats['onbase_perc'] == '':
                batter_stats['onbase_perc'] = '0.000'
            if batter_stats['slugging_perc'] != '':
                batter_stats['slugging_perc'] = '0' + batter_stats['slugging_perc']
            elif batter_stats['slugging_perc'] == '':
                batter_stats['slugging_perc'] = '0.000'
            batters.append(batter_stats)
    return batters


batter_statistics(batter_urls)


# # Pitchers
#
# ## First, creating the list to store the data
#
# ## Second, defining the function to scrape the data.

pitchers = []


def pitcher_statistics(list_of_urls):
    for url in list_of_urls:
        #Navigating to the correct table on each year's page for pitcher stats
        page = requests.get(url).text
        table_code = page[page.find('<table class="sortable stats_table" id="players_standard_pitching"'):]
        soup = BeautifulSoup(table_code, 'lxml')
        div_tags = soup.find('tbody')
        players = [t for t in div_tags.find_all('tr')]
        for player in players:
            #for each players on the page, we create a dictionary containing all relevant information
            team = player.find('td', {'data-stat': 'team_ID'})
            #Skips players without a team listed
            if team == None:
                continue
            team_txt = team.get_text()
            #Skips aggregate data in the event a player played for more than one team in a year
            if team_txt == 'TOT' or team_txt == '':
                continue
            #Creates a template dictionary so that we only recover relevant stats
            pitcher_stats = {'team_ID':0, 'G':0, 'earned_run_avg':0.00, 'CG':0, 'SHO':0, 'IP':0.0, 'H':0, 'R':0, 'ER':0, 'HR':0,
                        'BB':0, 'SO':0, 'whip':0.00}
            #Our 0's are replaced by the actual statistics
            for key in pitcher_stats.keys():
                txt = player.find('td', {'data-stat': key})
                pitcher_stats[key] = txt.get_text()
            link_tag = player.find('a')
            ending = link_tag.get('href')
            name = link_tag.get_text().replace('\xa0', ' ')
            link = bref+ending
            #player name added to dictionary
            pitcher_stats['Name'] = name
            #collects a link to each player's personal page so that we can later retrieve personal info (such as hometown)
                #only collects the link if it hasn't been collected before
            pitcher_stats['link'] = link
            if link not in player_links:
                player_links.append(link)
            pitcher_stats['Year'] = url[47:51]
            #Editing some of the statistics to be more easily readable
            if pitcher_stats['earned_run_avg'] == '':
                pitcher_stats['earned_run_avg'] = '0.00'
            if pitcher_stats['IP'] == '':
                pitcher_stats['IP'] = '0.0'
            if pitcher_stats['whip'] == '':
                pitcher_stats['whip'] = '0.000'
            pitchers.append(pitcher_stats)
    return pitchers

pitcher_statistics(pitcher_urls)


player_data = []

#Simple function to convert the height format to a more easily readable format
def height_conv(hite):
    h = hite.split('-')
    feet = int(h[0]) * 12
    inches = int(h[1])
    return feet + inches

#Follows a very similar format as the batter/pitcher stat retrieval in order to bring in personal information on each player
def player_info(list_of_links):
    #The count goes up everytime a player's info is scraped in order to assign each player a unique ID
    count = 0
    for link in list_of_links:
        data = {'PlayerID':0, 'Name':0, 'D.O.B.':0, 'Height':0, 'Weight':0, 'link':0}
        html = requests.get(link)
        soup = BeautifulSoup(html.text, 'html.parser')
        d_tag = soup.find('div', {'itemtype':"https://schema.org/Person"})
        data['Height'] = height_conv(d_tag.find('span', {'itemprop':'height'}).get_text())
        data['Weight'] = int(d_tag.find('span', {'itemprop':'weight'}).get_text()[:-2])
        data['D.O.B.'] = d_tag.find('span', {'itemprop':'birthDate'}).get('data-birth')
        data['Name'] = d_tag.find('h1', {'itemprop':'name'}).get_text()
        data['PlayerID'] = count
        data['link'] = link
        count += 1
        player_data.append(data)
    return player_data

#uses the new function on the list of player links collected earlier
player_info(player_links)


# # Manipulation

# ## Adding player ID to both the batter and pitcher records
for batter in batters:
    for player in player_data:
        if batter['link'] == player['link']:
            batter['PlayerID'] = player['PlayerID']

for pitcher in pitchers:
    for player in player_data:
        if pitcher['link'] == player['link']:
            pitcher['PlayerID'] = player['PlayerID']


# ## Adding the roster id from the roster records to the batter/pitcher records
#
# ## Then, deleting the irrelevant data from the batter/pitcher records

roster_count = 0


rosters = []

#Creating a Roster ID number to identify individual seasons for each player
    #EX: Player A has PlayerID 1, and their 2012 season's stats as RosterID 0, their 2013 season's stats has RosterID 27323, and so on
for batter in batters:
    batter['RosterID'] = roster_count
    roster_add = {}
    roster_add['RosterID'] = batter['RosterID']
    roster_add['Team'] = batter['team_ID']
    roster_add['PlayerID'] = batter['PlayerID']
    roster_add['Year'] = batter['Year']
    roster_add['Pitcher/Batter'] = 'Batter'
    roster_count += 1
    rosters.append(roster_add)


for pitcher in pitchers:
    pitcher['RosterID'] = roster_count
    roster_add = {}
    roster_add['RosterID'] = pitcher['RosterID']
    roster_add['Team'] = pitcher['team_ID']
    roster_add['PlayerID'] = pitcher['PlayerID']
    roster_add['Year'] = pitcher['Year']
    roster_add['Pitcher/Batter'] = 'Pitcher'
    roster_count += 1
    rosters.append(roster_add)

#Deleting information that was used to identify individual seasons. The RosterID has taken the place of this information.
for batter in batters:
    del batter['team_ID']
    del batter['Year']
    del batter['PlayerID']
    del batter['Name']
    del batter['link']

for pitcher in pitchers:
    del pitcher['team_ID']
    del pitcher['Year']
    del pitcher['PlayerID']
    del pitcher['Name']
    del pitcher['link']

for pla in player_data:
    del pla['link']


# ## Changing all numbers from strings to int/floats
ints = ['G', 'AB', 'R', '2B', '3B', 'HR', 'RBI', 'SB', 'BB', 'SO']
floats = ['onbase_perc', 'slugging_perc']
for batter in batters:
    for key in batter.keys():
        if key in ints:
            batter[key] = int(batter[key])
        elif key in floats:
            batter[key] = float(batter[key])

ints = ['G', 'CG', 'SHO', 'H', 'R', 'ER', 'HR', 'BB', 'SO']
floats = ['earned_run_avg', 'IP', 'whip']
for pitcher in pitchers:
    for key in pitcher.keys():
        if key in ints:
            pitcher[key] = int(pitcher[key])
        elif key in floats:
            pitcher[key] = float(pitcher[key])


#Adding a dictionary of all teams and their acronyms
team_acronyms = {'Boston Red Sox':'BOS',
 'Chicago White Sox':'CHW',
 'Colorado Rockies':'COL',
 'Washington Nationals':'WSN',
 'Atlanta Braves':'ATL',
 'St. Louis Cardinals':'STL',
 'Detroit Tigers':'DET',
 'Cincinnati Reds':'CIN',
 'Minnesota Twins':'MIN',
 'Milwaukee Brewers':'MIL',
 'Arizona Diamondbacks':'ARI',
 'Seattle Mariners':'SEA',
 'Kansas City Royals':'KCR',
 'Philadelphia Phillies':'PHI',
 'Toronto Blue Jays':'TOR',
 'Cleveland Indians':'CLE',
 'Chicago Cubs':'CHC',
 'Oakland Athletics':'OAK',
 'Houston Astros':'HOU',
 'Los Angeles Angels':'LAA',
 'Baltimore Orioles':'BAL',
 'Miami Marlins':'MIA',
 'Texas Rangers':'TEX',
 'New York Yankees':'NYY',
 'New York Mets':'NYM',
 'Tampa Bay Rays':'TBR',
 'San Francisco Giants':'SFG',
 'San Diego Padres':'SDP',
 'Los Angeles Dodgers':'LAD',
 'Pittsburgh Pirates':'PIT'}


html = requests.get('https://en.wikipedia.org/wiki/Major_League_Baseball')
soup = BeautifulSoup(html.text, 'lxml')
links = []
wiki = 'https://en.wikipedia.org'


t = soup.find_all('table', {'class':"wikitable"})
team_table = t[0].find('tbody')
li = t[0].find('tbody')
children = li.findChildren("tr" , recursive=False)


teams = []
team_data = []
team_data = children[2:]

team_data.pop(15)

#Creating a dictionary for each team, which includes basic information along with the link to their individual pages
for t in team_data:
    divs = ['East', 'Central', 'West']
    a = t.find_all('a')
    team_link = a[0]
    city = a[1].get_text()
    team = {}
    if team_link.get_text() in divs:
        team_link = a[1]
        city = a[2].get_text()
    team['Team'] = team_link.get_text()
    team['Acronym'] = team_acronyms[team_link.get_text()]
    home = city.split(',')
    team['City'] = home[0]
    team['link'] = wiki + team_link.get('href')
    teams.append(team)

#Creating list of all divisions in MLB
divs = ["American League East", "American League Central", "American League West",
        "National League East", "National League Central", "National League West"]

#Now that we have links to the teams' individual pages, we can scrape their info
for team in teams:
    #Navigating to the correct part of the page
    html = requests.get(team['link'])
    soup = BeautifulSoup(html.text, 'lxml')
    table = soup.find('table', {'class':"infobox vcard"})
    teamname = table.find_all('tr')
    name = teamname[0].get_text()
    pennent = 'Pennants '
    divis = 'Division titles '
    division =''
    #retrieving each team's division name
    for d in divs:
        if table.find('a', {'title': d}) != None and division == '':
            division = d
    leagues = ''
    divisions = ''
    #navigating to the table that houses each team's win numbers
    wins = table.find_all('th', {'scope':'row'})
    #pulling out each number of wins (World Series wins, league wins, etc) and adding them to the team's dictionary
    for win in wins:
        ws = win.find('span', {'class':"nowrap"})
        if ws != None:
            world_series = ws.find('span', {'class':"nobold"}).get_text()
            world_series = world_series.replace(' ', '').replace('(', '').replace(')', '')
        pen = win.get_text()
        if pennent in pen and leagues == '':
            p = pen.split(' ')
            leagues = p[-1].replace(' ', '').replace('(', '').replace(')', '')
        div = win.get_text()
        if divis in div and divisions == '':
            d = div.split(' ')
            divisions = d[-1].replace(' ', '').replace('(', '').replace(')', '')
    team['Division'] = division
    team['World Series Wins'] = int(world_series)
    team['League Wins'] = int(leagues)
    team['Division Wins'] = int(divisions)

#Removes the team's link now that we have pulled all needed info
for team in teams:
    del team['link']


# # Stadiums

stadium_link = 'https://en.wikipedia.org/wiki/List_of_current_Major_League_Baseball_stadiums'

#Navigating to the correct part of page to pull all stadium info
stadiums_final = []
html = requests.get(stadium_link)
soup = BeautifulSoup(html.text, 'lxml')
stadium_table = soup.find_all('table')[1]
stadiums = stadium_table.find_all('tr')
body = stadiums[1:]

park = body[6]
#navigates to the correct part of the page and then creating a dictionary with all needed info on each stadium
for park in body:
    stad_dict = {}
    td = park.find_all('td')
    stad_dict['Roof Type'] = td[-1].get_text().replace('\n', '')
    capacity_open = park.find_all('td', {'align': 'center'})
    capacity = int(capacity_open[0].get_text()[:6].replace(',', ''))
    stad_dict['Capacity'] = capacity
    opening = capacity_open[1].get_text()[:4].replace('\n', '')
    stad_dict['Opening Year'] = opening
    titles = []
    a_tags = park.find_all('a')
    for a in a_tags:
        if 'title' in a.attrs:
            titles.append(a)
    stad_tag = titles[0]
    stad_dict['Stadium'] = stad_tag.get_text()
    city_tag = titles[1]
    city = city_tag.get_text().split(',')[0]
    stad_dict['City'] = city
    team_tag = titles[2]
    team_name = team_tag.get_text()
    for team_d in teams:
        if team_d['Team'] == team_tag.get_text():
            team = team_d['Acronym']
    stad_dict['Team'] = team
    stadiums_final.append(stad_dict)


# # Divisions and Leagues
#Creating a list of all division names and another of league names
ds = []
for d in teams:
    if d['Division'] not in ds:
        ds.append(d['Division'])
leagues = []
divisions = []
ls =[]
for div in ds:
    l = {}
    d = {}
    if div[:15] not in ls:
        ls.append(div[:15])
    d['League Name'] = div[:15]
    d['Division Name'] = div
    divisions.append(d)

for leg in ls:
    l_d = {}
    l_d['League Name'] = leg
    leagues.append(l_d)

#Creating pandas dataframes from the results
batter_df = pd.DataFrame(batters)
batter_df.set_index('RosterID', inplace=True)

pitcher_df = pd.DataFrame(pitchers)
pitcher_df.set_index('RosterID', inplace=True)

rosters_df = pd.DataFrame(rosters)
rosters_df.set_index('RosterID', inplace=True)

player_df = pd.DataFrame(player_data)
player_df.set_index('PlayerID', inplace=True)

team_df = pd.DataFrame(teams)
team_df.set_index('Acronym', inplace=True)

stadiums_df = pd.DataFrame(stadiums_final)
stadiums_df.set_index('Stadium', inplace=True)

leagues_df = pd.DataFrame(leagues)
leagues_df.set_index('League Name', inplace=True)

divisions_df = pd.DataFrame(divisions)
divisions_df.set_index('Division Name', inplace=True)

#Exporting all results to csvs
batter_df.to_csv('/Users/Tim/Desktop/Project/CSVs/batters.csv')

pitcher_df.to_csv('/Users/Tim/Desktop/Project/CSVs/pitchers.csv')

rosters_df.to_csv('/Users/Tim/Desktop/Project/CSVs/rosters.csv')

player_df.to_csv('/Users/Tim/Desktop/Project/CSVs/players.csv')

team_df.to_csv('/Users/Tim/Desktop/Project/CSVs/teams.csv')

stadiums_df.to_csv('/Users/Tim/Desktop/Project/CSVs/stadiums.csv')

leagues_df.to_csv('/Users/Tim/Desktop/Project/CSVs/leagues.csv')

divisions_df.to_csv('/Users/Tim/Desktop/Project/CSVs/divisions.csv')
