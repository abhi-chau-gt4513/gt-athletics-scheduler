# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 14:26:55 2023

@author: hgadd
"""

import csv
# open file in read mode
with open("data_final.csv", 'r', encoding='utf-8-sig') as f:
     
    dict_reader = csv.DictReader(f)
    unfilteredGameList = list(dict_reader)
    
gameList = []
for n in unfilteredGameList:
    if n not in gameList and int(n["Team1_PTS"]) > 10:
        gameList.append(n)
teamInfo = {}
count = 0
for game in gameList:
   
    team1 = game["Team1"]
    team2 = game["Team2"]
    
    if(team1 == "CalStateBakersfield" or team2 == "CalStateBakersfield"):
        print(game["Date"],game["Year"],team1, team2, )
    season = game["Year"]
    fields = ["_FG_Scored","_FG_Attempted","_FG_Percent","_2P_Scored","_2P_Attempted",
              "_2P_Percent", "_3P_Scored", "_3P_Attempted","_3P_Percent","_eFG%","_FT_Scored",
              "_FT_Attempted", "_FT_Percent","_ORB","_DRB","_AST","_STL","_BLK","_TOV","_PF","_PTS"]
    if(teamInfo.get(team1) == None):
        teamInfo[team1] = {}
    if(teamInfo[team1].get(season) == None):
        teamInfo[team1][season] = {"matches": 0,
                                   "teamName": team1}
    
    if(teamInfo.get(team2) == None):
        teamInfo[team2] = {}
    if(teamInfo[team2].get(season) == None):
        teamInfo[team2][season] = {"matches": 0,
                                   "teamName": team2}
    teamInfo[team1][season]["matches"] += 1
    teamInfo[team2][season]["matches"] += 1
    for n in fields:
        try:
            teamInfo[team1][season][n] += float(game["Team1" + n])
        except:
            teamInfo[team1][season][n] = float(game["Team1" + n])
        
        try:
            teamInfo[team1][season]["opp" + n] += float(game["Team2" + n])
        except:
            teamInfo[team1][season]["opp" + n] = float(game["Team2" + n])
        
        try:
            teamInfo[team2][season][n] += float(game["Team2" + n])
        except:
            teamInfo[team2][season][n] = float(game["Team2" + n])
        
        try:
            teamInfo[team2][season]["opp" + n] += float(game["Team1" + n])
        except:
            teamInfo[team2][season]["opp" + n] = float(game["Team1" + n])

years = ["2021","2022"]
for year in years:
    with open('dataAverages' + year + '.csv', mode='w', newline = "") as f:
        date_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        headers = ["teamName","matches"]
        for n in fields:
            headers.append(n)
            headers.append("opp"+n)
        date_writer.writerow(headers)
        for n in teamInfo:
            if(teamInfo[n].get(year) != None):
                matches = teamInfo[n][year]["matches"]
                dump = []
                for m in headers:
                    if(m != "teamName" and m != "matches"):
                        teamInfo[n][year][m] = round(float(teamInfo[n][year][m]) / float(matches),4)
                    dump.append(teamInfo[n][year][m])
                date_writer.writerow(dump)
