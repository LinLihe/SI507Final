from bs4 import BeautifulSoup
import unittest
import requests
import re
import psycopg2
import psycopg2.extras
from Secret import *
import os, errno
import shutil
from flask import Flask, render_template, request
import tempfile
    
### Control Variables
Cache_data_and_reset_table = False
Select_season = "09" # The lastest season is (20)18
Update = False # If Update = True, all cached files will be remove 
run_app = False
hard_path = 'D:/507np1/SI507Final/html_files/' # User Input: Please change it according to your preference.

### Global Variables
Reset_Tables = Cache_data_and_reset_table 
basic_link = "http://www.hoopsstats.com/"
path = hard_path+str(Select_season)+'season/' 
### Function definition

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory): 
        try:
            os.makedirs(directory)

        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return False   
    else:
        return True

def Update_data_for_one_season(file_path = path, select_year = Select_season):
    directory = os.path.dirname(file_path)
    if os.path.exists(directory):
        shutil.rmtree(file_path)
        ensure_dir(file_path)
        return True
    else:
        ensure_dir(file_path)
        return False

def cache_or_read_html(file_name, web_link = basic_link, folder_path = path, select_year = Select_season):
    try:
        file = open(os.path.join(folder_path,file_name+"_"+str(select_year)+".html"),"r", encoding = "utf-8")
        stats = file.read()
        file.close()
    except:
        stats = requests.get(web_link).text
        ensure_dir(folder_path)
        f = open(os.path.join(folder_path,file_name+"_"+str(select_year)+".html"), "w", encoding = "utf-8")
        f.write(stats)
        f.close()
    return stats

def get_team_name_and_link(main_page_data, select_year = Select_season):
    Team_list = []
    Team_link_list = []
    nba_bs = BeautifulSoup(main_page_data, "html.parser")
    all_teams = nba_bs.find("div", id ='nbateams').find_all("table", cellspacing = "0")
    for j in range(2):
      for n in range(15):
        single_name= all_teams[j].find_all("tr", class_="submenu")[n].text.strip()
        Team_list.append(single_name)
        Team_link = all_teams[j].find_all("tr", class_="submenu")[n].find("a")["href"].replace("18", str(select_year),1)
        # print (Team_link)
        Team_link_list.append(Team_link) # Default season is 2017-2018, replace function makes season to be 2016-2017
    return Team_list, Team_link_list

def get_player_stats_page_in_each_team(team_names_list):
    team_player_link_list = []
    for n in range (len(team_names_list)):
        team_data = cache_or_read_html(team_names_list[n])
        team_soup = BeautifulSoup(team_data, "html.parser")
        player_button = team_soup.find("table", id = "sub/3")
        player_button_link = player_button.find("a")["href"]
        team_player_link_list.append(player_button_link)
    return team_player_link_list 

def get_individual_player_data(team_name, basic_link, p_link, path):
    player_data = cache_or_read_html(team_name+"_player_stats",basic_link+p_link, path)
    player_soup = BeautifulSoup(player_data, "html.parser")
    player_item = player_soup.find_all("table", class_="statscontent")
    return player_item

### Class Definition

# Player class
class nba_player(object):

    def __init__(self, individual_bs):

        individual_link = individual_bs.find("td",width = "9%").find("a")["href"]     
        self.name = re.search(r'players/([A-Za-z-]+)/', individual_link).group(1).replace("-"," ").title()
        # self.team = team_name
        self.att = int(individual_bs.find("td", width = "3%").text)
        self.min = float(individual_bs.find_all("td", width = "4%")[0].text)
        self.pts = float(individual_bs.find_all("td", width = "4%")[1].text)
        self.reb = float(individual_bs.find_all("td", width = "4%")[2].text)
        self.ast = float(individual_bs.find_all("td", width = "4%")[3].text)
        self.stl = float(individual_bs.find_all("td", width = "4%")[4].text)
        self.blk = float(individual_bs.find_all("td", width = "4%")[5].text)
        self.to = float(individual_bs.find_all("td", width = "4%")[6].text)
        self.pct_all = float(individual_bs.find_all("td", width = "3%")[2].text)
        self.pct_3ps = float(individual_bs.find_all("td", width = "3%")[3].text)
        self.pct_fs = float(individual_bs.find_all("td", width = "3%")[4].text)
        self.eff = float(individual_bs.find_all("td", width = "4%")[10].text)


    def __repr__(self):
        return "Name: {}\nAttendance: {}\nMinute: {}\nPoint: {}\nRebound: {}\nAssist: {}\nSteal: {}\nBlock: {}\nTurnover: {}\nFiled_Goals_Made_Pct: {}\n3_Points_Pct: {}\nFree_Throws_Pct: {}\nEfficiency: {}\n".format(self.name,self.att,self.min,self.pts,self.reb,self.ast,self.stl,self.blk,self.to,self.pct_all,self.pct_3ps,self.pct_fs,self.eff)

    def __contains__(self, attribute):
        result = attribute in self.__repr__()
        return result

    def return_for_database(self):
        return (self.name,self.att,self.min,self.pts,self.reb,self.ast,self.stl,self.blk,self.to,self.pct_all,self.pct_3ps,self.pct_fs,self.eff)


# Team class
class nba_team(object):

    def __init__(self, team_bs):
        self.name = team_bs.find("table", class_ = "teamtitle").find("td", align = "left").text.strip().replace(" Profile","")
        self.total_game = int(team_bs.find("table", class_ = "statscontent").find_all("td", width ="3%")[0].text.strip())
        self.win_game = int(team_bs.find("table", class_ = "statscontent").find_all("td", width ="3%")[1].text.strip())
        self.pts = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[1].text)
        self.reb = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[2].text)
        self.ast = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[3].text)
        self.stl = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[4].text)
        self.blk = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[5].text)
        self.to = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[6].text)
        self.pct_FG = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[10].text)
        self.pct_3ps = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[11].text)
        self.pct_FS = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="4%")[12].text)
        self.eff = float(team_bs.find("table", class_ = "statscontent").find_all("td", width ="5%")[0].text)

    def __repr__(self):
        return "Team: {}\nTotal Game: {}\nWon Game: {}\nPoint: {}\nRebound: {}\nAssist: {}\nSteal: {}\nBlock: {}\nTurnover: {}\nFiled_Goals_Pct: {}\n3_Points_Pct: {}\nFree_Throws_Pct: {}\nEfficiency: {}\n".format(self.name,self.total_game,self.win_game,self.pts,self.reb,self.ast,self.stl,self.blk,self.to,self.pct_FG,self.pct_3ps,self.pct_FS,self.eff)

    def __contains__(self, attribute):
        result = attribute in self.__repr__()
        return result

    def return_for_database(self):
        return (self.name,self.total_game,self.win_game,self.pts,self.reb,self.ast,self.stl,self.blk,self.to,self.pct_FG,self.pct_3ps,self.pct_FS,self.eff)
            # )


### Database functions definition
def execute_and_fetch(query):
    cur.execute(query)
    rec = cur.fetchall()
    # print('--> Result ', rec)
    return rec

def insert_team(tuple_):   
    sql = """INSERT INTO "Teams"("Name","Number of total game","Number of won game","Point","Rebound","Assist","Steal","Block","Turnovers","Field Goal Percentage","3 Points Percentage","Free Throws Percentage","Efficiency") VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING "ID" """
    cur.execute(sql,tuple_)   
    conn.commit()
    rec = cur.fetchone()
    return rec['ID'] 

def insert_player(tuple_, team_id):

    sql = """INSERT INTO "Players"("Name","Attendance","Minute","Point","Rebound","Assist","Steal","Block","Turnovers","Field Goal Percentage","3 Points Percentage","Free Throws Percentage","Efficiency","Team") VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""    
    cur.execute(sql,tuple_+(team_id,))
    conn.commit()
    return True


### Connecting data with database


if Update == True:
    Update_data_for_one_season()

if Cache_data_and_reset_table == True:

# Main page cache
    main_page = cache_or_read_html("nba_main",basic_link, path)

# Team pages cache/read and each team data cache
    team_names, team_links = get_team_name_and_link(main_page, Select_season)
    team_list = []
    for n in range (30):
        team_data = cache_or_read_html(team_names[n],basic_link+team_links[n],path)
        team_soup = BeautifulSoup(team_data, "html.parser")
        team_list.append(nba_team(team_soup))

    player_list = []
    team_players_link_list = get_player_stats_page_in_each_team(team_names)

try:
    conn = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
    print ("Success connecting to database.")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
except:
    print ("Unable to connect to the database.")
    sys.exit(1)
# print (team_list[0].return_for_database())
if Reset_Tables == True:

    cur.execute("""DROP TABLE IF EXISTS "Players" """)   
    cur.execute("""DROP TABLE IF EXISTS "Teams" """)  

    cur.execute("""CREATE TABLE IF NOT EXISTS "Teams"(
        "ID" SERIAL PRIMARY KEY,
        "Name" VARCHAR(128) NOT NULL UNIQUE,
        "Number of total game" INTEGER,
        "Number of won game" INTEGER,
        "Point" FLOAT(4),
        "Rebound" FLOAT(4),
        "Assist" FLOAT(4),
        "Steal" FLOAT(4),
        "Block" FLOAT(4),
        "Turnovers" FLOAT(4),
        "Field Goal Percentage" FLOAT(4),
        "3 Points Percentage" FLOAT(4),  
        "Free Throws Percentage" FLOAT(4),
        "Efficiency" FLOAT(4)) """)


    cur.execute("""CREATE TABLE IF NOT EXISTS "Players"(
        "Name" VARCHAR(40) NOT NULL,
        "Attendance" INTEGER,
        "Minute" FLOAT(4),
        "Point" FLOAT(4),
        "Rebound" FLOAT(4),
        "Assist" FLOAT(4),
        "Steal" FLOAT(4),
        "Block" FLOAT(4),
        "Turnovers" FLOAT(4),
        "Field Goal Percentage" FLOAT(4),
        "3 Points Percentage" FLOAT(4),
        "Free Throws Percentage" FLOAT(4),
        "Efficiency" FLOAT(4),
        "Team" INTEGER REFERENCES "Teams"("ID"),
        PRIMARY KEY ("Name", "Team"))  """)

# Team's players pages cache/read and each player's data cache
    for n in range (len(team_list)):
        team_id = insert_team(team_list[n].return_for_database())
    # for n in range (len(team_names)):
        player_item = get_individual_player_data(team_names[n], basic_link, team_players_link_list[n], path)
        for m in range (len(player_item)-2):
            # player_list.append(nba_player(player_item[m]))
            insert_player(nba_player(player_item[m]).return_for_database(), team_id)   


### Display the result using Flask
app = Flask(__name__)

def query_player_table(Name):
    cur.execute("""
        SELECT 
        ("Players"."Name") as "Player",
        ("Players"."Attendance") as "Attandence", 
        ("Players"."Minute") as "Minute", 
        ("Players"."Point") as "Point", 
        ("Players"."Rebound") as "Rebound", 
        ("Players"."Assist") as "Assist", 
        ("Players"."Steal") as "Steal", 
        ("Players"."Block") as "Block", 
        ("Players"."Field Goal Percentage") as "Field Goal Percentage", 
        ("Players"."3 Points Percentage") as "3 Points Percentage", 
        ("Players"."Free Throws Percentage") as "Free Throws Percentage", 
        ("Players"."Efficiency") as "Efficiency",
        ("Teams"."Name") as "Player's team"
        FROM "Players" inner join "Teams" on "Players"."Team" = "Teams"."ID"  
        WHERE "Players"."Name" ILIKE '%%'||%s||'%%' """, (Name,))
    data_output = cur.fetchall()
    return data_output

def query_team_table(Name):
    cur.execute("""SELECT * FROM "Teams" WHERE "Name" ILIKE '%%'||%s||'%%'   """, (Name,))
    data_output = cur.fetchall()
    return data_output

@app.route("/")
def Welcome():
    return "<h1>Welcome to NBA database</h1>"

@app.route("/player")
def player_name():
    player_name = request.args.get('name')
    player_data = query_player_table(player_name)
    return render_template("player.html", player_output = player_data, season = Select_season)

@app.route("/team")
def team_name():
    team_name = request.args.get('name')
    team_data = query_team_table(team_name)
    return render_template("team.html",   team_output = team_data, season = Select_season)

@app.route("/mvp")
def mvp_player_in_each_team():
    MVP_Value = execute_and_fetch("""
        SELECT 
        (select "Players"."Name" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items") as "Player Name",        
        (select "Players"."Point" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items"),
        (select "Players"."Rebound" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items"),
        (select "Players"."Assist" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items"),             
        * 
        from (
            SELECT "Teams"."Name" as "Team Name", MAX("Players"."Assist"+"Players"."Point"+"Players"."Rebound") as "Sum of Three Items"
            From "Players" INNER JOIN "Teams" on "Teams"."ID" = "Players"."Team"
            GROUP BY "Teams"."Name" 
            ORDER BY MAX("Players"."Assist"+"Players"."Point"+"Players"."Rebound") DESC 
        ) as team_max
    """)

    pt = 0
    reb = 0
    ast = 0
    for n in range (len(MVP_Value)):
        pt +=  MVP_Value[n]["Point"]
        reb += MVP_Value[n]["Rebound"]
        ast += MVP_Value[n]["Assist"]
    avg_d = {"Avg_Points": str(pt/30), "Avg_Rebounds": str(reb/30), "Avg_Assists": str(ast/30)}

    return render_template("mvp.html", mvp_dict = MVP_Value, season = Select_season, dic = avg_d)

@app.route("/player/average")
def player_average():
    Player_avg = execute_and_fetch("""
        SELECT AVG("Attendance") as "Attandence", 
        AVG("Minute") as "Minute", 
        AVG("Point") as "Point", 
        AVG("Rebound") as "Rebound", 
        AVG("Assist") as "Assist", 
        AVG("Steal") as "Steal", 
        AVG("Block") as "Block", 
        AVG("Field Goal Percentage") as "Field Goal Percentage", 
        AVG("3 Points Percentage") as "3 Points Percentage", 
        AVG("Free Throws Percentage") as "Free Throws Percentage", 
        AVG("Efficiency") as "Efficiency" from "Players"
        Where "Minute" > 10.0""") 
    return render_template("player_avg.html", avg_dict = Player_avg, season = Select_season)

@app.route("/team/average")
def team_average():
    Team_avg = execute_and_fetch("""SELECT AVG("Point") as "Point", AVG("Rebound") as "Rebound", AVG("Assist") as "Assist", AVG("Steal") as "Steal", AVG("Block") as "Block", AVG("Field Goal Percentage") as "Field Goal Percentage", AVG("3 Points Percentage") as "3 Points Percentage", AVG("Free Throws Percentage") as "Free Throws Percentage", AVG("Efficiency") AS "Efficiency" FROM "Teams" """) 
    return render_template("team_avg.html", avg_dict = Team_avg, season = Select_season)

@app.route("/mvp/percentage")
def player_percentage():
    mvp_pct = execute_and_fetch("""
        SELECT
        (select "Players"."Name" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items") as "Player Name",            
        ((select "Players"."Point" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items")/(select "Point" from "Teams" where team_max."Team Name" = "Teams"."Name")) as point_pct,
        ((select "Players"."Rebound" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items")/(select "Rebound" from "Teams" where team_max."Team Name" = "Teams"."Name")) as reb_pct,
        ((select "Players"."Assist" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items")/(select "Assist" from "Teams" where team_max."Team Name" = "Teams"."Name")) as ast_pct,
        team_max."Team Name" 
        from (
            SELECT "Teams"."Name" as "Team Name", MAX("Players"."Assist"+"Players"."Point"+"Players"."Rebound") as "Sum of Three Items"
            From "Players" Inner join "Teams" on "Players"."Team" = "Teams"."ID"
            GROUP BY "Teams"."Name" 
            ORDER BY MAX("Players"."Assist"+"Players"."Point"+"Players"."Rebound") DESC 
        ) as team_max
    """)

    pt = 0
    reb = 0
    ast = 0
    for n in range (len(mvp_pct)):
        pt +=  mvp_pct[n]["point_pct"]
        reb += mvp_pct[n]["reb_pct"]
        ast += mvp_pct[n]["ast_pct"]
    avg_d = {"Avg_Pct_Points": str(pt/30), "Avg_Pct_Rebounds": str(reb/30), "Avg_Pct_Assists": str(ast/30)}

    return render_template("mvp_pct.html", avg_dict = mvp_pct, season = Select_season, dic = avg_d)     

@app.route("/mvp/average")
def mvp_average():
    MVP_Value = execute_and_fetch("""
        SELECT 
        (select "Players"."Name" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items") as "Player Name",        
        (select "Players"."Point" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items"),
        (select "Players"."Rebound" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items"),
        (select "Players"."Assist" from "Players" inner join "Teams" on "Teams"."ID" = "Players"."Team" where "Teams"."Name"=team_max."Team Name" and ("Players"."Assist"+"Players"."Point"+"Players"."Rebound") = team_max."Sum of Three Items"),             
        * 
        from (
            SELECT "Teams"."Name" as "Team Name", MAX("Players"."Assist"+"Players"."Point"+"Players"."Rebound") as "Sum of Three Items"
            From "Players" INNER JOIN "Teams" on "Teams"."ID" = "Players"."Team"
            GROUP BY "Teams"."Name" 
            ORDER BY MAX("Players"."Assist"+"Players"."Point"+"Players"."Rebound") DESC 
        ) as team_max
    """)    
    # for k,v in 
if run_app == True:
    app.run(use_reloader=True, debug=True)

#     