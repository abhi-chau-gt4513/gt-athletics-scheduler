import requests
import numpy as np
import pandas as pd
import json

from bs4 import BeautifulSoup


# Original method for scraping the html content based on url provided
def get_content(url):
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup.prettify())

    return soup

# def get_team_schedules

# Get specific html content per team per season
def get_content_per_team_per_year(team_name, year):
    team_name = team_name.replace(' ', '-')
    url = f"https://www.warrennolan.com/basketball/{year}/schedule/{team_name}"
    # print(url)
    return get_content(url=url)

# Get specific html structure for team schedule info
def get_team_schedule(team_name, year):
    soup = get_content_per_team_per_year(team_name=team_name, year=year)

    team_schedule = None

    # The "div" tags show the information about team schedule, 
    # specifically with class attribute = main-body-row__flex-scroll-column
    soup.find_all("div")[0]["class"]
    for elem in soup.find_all("div"):
        if elem.has_attr("class") and elem["class"][0] == "main-body-row__flex-scroll-column":
            team_schedule = elem.ul
            break
    return team_schedule

# This method is there if you want to get the team schedule in a list, not as a single ul element
def get_team_schedule_list(team_name, year):
    soup = get_content_per_team_per_year(team_name=team_name, year=year)

    team_schedule = None

    # The "div" tags show the information about team schedule, 
    # specifically with class attribute = main-body-row__flex-scroll-column
    soup.find_all("div")[0]["class"]
    for elem in soup.find_all("div"):
        if elem.has_attr("class") and elem["class"][0] == "main-body-row__flex-scroll-column":
            team_schedule = elem.find_all("li")
            break
    return team_schedule

# Get the match dates per team per season.
# This goes one deeper: looks in the unordered list returned from get_team_schedule() method
# with class = "team-schedule__game ...".
def get_match_dates(team_name, year):
    team_schedule = get_team_schedule_list(team_name=team_name, year=year)

    dates = []
    for k in range(len(team_schedule)):
        date = ""
        for i in team_schedule[k].find_all("span"):
            if i.has_attr("class") and ("team-schedule__game-date" in i["class"][0]
                                    and "dow" not in i["class"][0]):
                date += i.text + " "
        if date != "":
            dates.append(date + "2022")
    

    return dates

def get_match_locations(team_name, year):
    team_schedule = get_team_schedule_list(team_name=team_name, year=year)
    # print(team_schedule[0])

    locations = []
    for k in range(len(team_schedule)):
        location = ""
        arena = ""
        count = 0
        for i in team_schedule[k].find_all("span"):
            if i.has_attr("class") and ("team-schedule__info" in i["class"][0]
                                    and "tv" not in i["class"][0]):
                if (count % 2 == 0):
                    location = i.text
                else:
                    arena = i.text
                count += 1
        if location != "":
            locations.append(arena)
    

    return locations

def get_opponents(team_name, year):
    team_schedule = get_team_schedule_list(team_name=team_name, year=year)
    # print(team_schedule[0])

    opponents = []
    for k in range(len(team_schedule)):
        opponent = ""
        
        for i in team_schedule[k].find_all("span"):
            if i.has_attr("class") and ("team-schedule__opp-line" in i["class"][0]):
                opponent = i.text
        
        if opponent != '':
            opponents.append(opponent)
    

    return opponents

def get_matches(team_name, year):
    dates = get_match_dates(team_name, year)
    locations = get_match_locations(team_name, year)
    opponents = get_opponents(team_name, year)

    # print(len(dates), len(locations), len(opponents))

    # for i in range(len(opponents)):
    #     print(dates[i], locations[i], opponents[i])

# This only gets stats for first match. The code works, but just for the first match. 
# More formatting of stats is needed to include all matches played.
def get_stats(team_name, year):
    team_schedule = get_team_schedule(team_name=team_name, year=year)

    labels = []
    data = []
    data1 = []
    data2 = []

    checkmarks = [4, 4, 14, 14]
    
    for i in team_schedule[0].find_all("tr"):

        for j1 in i.find_all("th"):
            labels.append(j1.text)
        
        for j2 in i.find_all("td"):
            # Handle the ones with the percentages
            if j2.find("b") is not None:
                str1 = j2.text
                str2 = j2.find("b").text

                str1 = str1.replace(str2, "")
                data.append((str1, str2))
            else:
                data.append(j2.text)

    
    checkmark = 0
    counter = 0
    for j2 in data:
        if checkmark % 2 == 0:
            data1.append(j2)
        else:
            data2.append(j2)
        
        counter += 1
        if counter == checkmarks[checkmark]:
            checkmark += 1
            counter = 0
    # for i, j, k in zip(labels, data1, data2):
    #     print(i, j, k)


# Function to reformat each statistic
# Assumes 'labels' and 'stats' are of the same length
# 
# labels: list of strings identifying the type of statistic that needs reformatting
# stats: list of tuples with the value of each team's statistic, respectively
# 
# Returns a dictionary with all reformatted statistics and their new labels
def stat_formatter(col_names, vals):
    text = set(["TEAMS"])
    points = set(["ORB", "DRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"])
    percents = set(["eFG%"])
    points_and_percents = set(["FG", "2P", "3P", "FT"])

    new_stats = {}

    for i in range(len(col_names)):
        col = col_names[i]
        val = vals[i]
        
        if col in text:
            t1_name = val[0].replace(" ", "")
            t2_name = val[1].replace(" ", "")
            new_stats["Team1_Team2"] = t1_name + "_" + t2_name

        elif col in points:
            new_stats["Team1_" + col] = int(val[0])
            new_stats["Team2_" + col] = int(val[1])
            
        elif col in percents:
            new_stats["Team1_" + col] = float(val[0][:-1])
            new_stats["Team2_" + col] = float(val[1][:-1])

        else:
            v1 = val[0].split("-")
            v2 = val[1].split("-")
            scored1, attempts1, pct1 = int(v1[0]), int(v1[1][:2]), float(v1[1][2:-1])
            scored2, attempts2, pct2 = int(v2[0]), int(v2[1][:2]), float(v2[1][2:-1])
            
            new_stats["Team1_" + col + "_Scored"] = scored1
            new_stats["Team1_" + col + "_Attempted"] = attempts1
            new_stats["Team1_" + col + "_Percent"] = pct1
            new_stats["Team2_" + col + "_Scored"] = scored2
            new_stats["Team2_" + col + "_Attempted"] = attempts2
            new_stats["Team2_" + col + "_Percent"] = pct2
        
    return new_stats

def get_home_venues():
    soup = get_content("https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_basketball_arenas")

    headers = None

    soup.find_all("table")
    counter = 0
    table_datasets = []
    for elem in soup.find_all("table"):
        # Only want the first table with class attribute
        if elem.has_attr("class") and counter == 0:

            # Get all the headers
            headers = elem.find_all("th")
            
            if len(headers) > 0:

                # Get all table data html objects
                body = elem.find_all("td")
                length = len(body)

                # List comprehension for just getting the team name, arena, and arena location
                entries = [[body[k * 8 + i].text.replace('\n', '') if i % 8 == 1 or i % 8 == 2 or i % 8 == 4 else None for i in range(len(body[k * 8 : (k + 1) * 8]))] for k in range((int) (length / 8))]
                counter += 1
                [table_datasets.append(i) for i in entries]
        
        

    # print(table_datasets[-2:])
    table_datasets = np.array(table_datasets)
    # print(table_datasets[:, 4])
    table_datasets[:, 4] = [i[4].replace( ' ', '') for i in table_datasets]
    length_table = len(table_datasets)
    # print(length_table)
    # print(table_datasets[:, 4])
    
    print(*table_datasets[:, 4], sep = '\n')
    home_venues = dict()

    problematic_team_names = {
        "NorthCarolinamen": "NorthCarolina",
        "NorthCarolinaStatemen": "NorthCarolinaState",

    }

    for i in table_datasets:
        
        # table_datasets
        if i[4] in home_venues:
            string = i[1] + "+" + home_venues[i[4]]
            home_venues[i[4]] = string
            # print(string)
            # print(home_venues[i[4] + " 1"][0])
            # home_venues[i[4] + " " + (str)(home_venues[i[4] + " 1"][0] + 1)] = (1, i[2], i[1])
            # home_venues[i[4] + " 1"] = (home_venues[i[4] + " 1"][0] + 1, home_venues[i[4] + " 1"][1], home_venues[i[4] + " 1"][2]) # Update count 
            # print(home_venues[i[4]])
            # print(i)
        else:
            home_venues[i[4]] = i[1]
    # print(home_venues.items())
    # print(len(home_venues))
    # print(home_venues)

    return home_venues

# get_home_venues()

def get_all_teams():
    soup = get_content("https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_basketball_arenas")

    headers = None

    soup.find_all("table")
    counter = 0
    table_datasets = []
    for elem in soup.find_all("table"):
        # Only want the first table with class attribute
        if elem.has_attr("class") and counter == 0:

            # Get all the headers
            headers = elem.find_all("th")
            
            if len(headers) > 0:

                # Get all table data html objects
                body = elem.find_all("td")
                length = len(body)

                # List comprehension for just getting the team name, arena, and arena location
                entries = [[body[k * 8 + i].text.replace('\n', '') if i % 8 == 1 or i % 8 == 2 or i % 8 == 4 else None for i in range(len(body[k * 8 : (k + 1) * 8]))] for k in range((int) (length / 8))]
                counter += 1
                [table_datasets.append(i) for i in entries]
        
        

    # print(table_datasets[-2:])
    table_datasets = np.array(table_datasets)
    # print(table_datasets[:, 4])
    table_datasets[:, 4] = [i[4] for i in table_datasets]
    length_table = len(table_datasets)

    teams = []

    for i in table_datasets:
        teams.append(i[4])

    return teams

get_all_teams()

# Determine if game is home (0) or away (1) for team_name based on venues and game venue
def determine_home_or_away(team_name, venues, game_venue):
    for i in venues:
        if i == game_venue:
            return 0
    
    return 1

def get_dataset(team, year, team_pairs):
    team_schedule = get_team_schedule(team, year)
    if team_schedule is not None:
        
        matches = []
        locations = get_match_locations(team, year)
        # team_pairs.add(matches[0]['Team1_Team2'])
        stats_tables = team_schedule.find_all("table", class_ = "team-schedule-bottom__stat")
        #cnt = 0
        
        match_no = 0
        for table in stats_tables:
            # get table headers and data
            rows = table.find_all("tr")
            headers = rows[0].find_all("th")
            team_1_stats = rows[1].find_all("td")
            team_2_stats = rows[2].find_all("td")

            # extract labels and stats for each match
            labels = [h.text for h in headers]
            labels[0] = "TEAMS"
            temp1 = [t1.text for t1 in team_1_stats]
            temp2 = [t2.text for t2 in team_2_stats]
            stats = [(temp1[i], temp2[i]) for i in range(len(temp1))]
            
            match_stats = stat_formatter(labels, stats)

            match_stats["Location"] = locations[match_no]
            match_stats["Year"] = year
            if match_stats['Team1_Team2'] not in team_pairs:
                team_pairs.add(match_stats['Team1_Team2'])
                matches.append(match_stats)
            # else :
            #     print(match_stats['Team1_Team2'] not in team_pairs)
            
            match_no += 1

        df = pd.DataFrame(matches)

        # df.drop(0)
        return df

def get_dataset_with_home_away(team, year, team_pairs):
    df = get_dataset(team, year, team_pairs)

    home_venues_per_team = get_home_venues()

    teams_per_match = df["Team1_Team2"]

    team_1_home_or_away = []
    team_2_home_or_away = []

    row = 0
    for i in teams_per_match:
        team1, team2 = i.split("_")
        game_venue = df["Location"].values[row]
        # print(game_venue)
        if team1 in home_venues_per_team and team2 in home_venues_per_team:
            string1 = home_venues_per_team[team1]
            string2 = home_venues_per_team[team2]
            home1 = determine_home_or_away(team1, string1.split("+"), game_venue)
            home2 = determine_home_or_away(team2, string2.split("+"), game_venue)
            team_1_home_or_away.append("home" if home1 == 0 else "away")
            team_2_home_or_away.append("home" if home2 == 0 else "away")
            # print(team1, home1, team2, home2)
        else :
            # TODO: Remove this once all bugs have been patched with the team name reconciliation
            team_1_home_or_away.append(-1)
            team_2_home_or_away.append(-1)
        row += 1

    df['Team 1 Home or Away'] = team_1_home_or_away
    df['Team 2 Home or Away'] = team_2_home_or_away
    df['Year'] = year
    return df          


# print(get_stats("Iona", '2022'))
# print("Hello")
# get_home_venues()
print(json.dumps(get_home_venues(), indent=4))

# Map of teams with home arenas: from https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_basketball_arenas 

home_venues_0 = {
    'BostonCollege': 'Conte Forum',
    'Clemson': 'Littlejohn Coliseum',
    'Duke': 'Cameron Indoor Stadium',
    'Florida State': 'Donald L. Tucker Civic Center',
    'Georgia Tech': 'Hank McCamish Pavilion',
    'Louisville': 'KFC Yum! Center',
    'Miami': 'Watsco Center',
    'North Carolina': 'Dean Smith Center',
    'North Carolina State': 'PNC Arena',
    'Notre Dame': 'Edmund P. Joyce Center',
    'Pittsburgh': 'Petersen Events Center',
    'Syracuse': 'JMA Wireless Dome',
    'Virginia': 'John Paul Jones Arena',
    'Virginia Tech': 'Cassell Coliseum',
    'Wake Forest': 'Lawrence Joel Veterans Memorial Coliseum'
}