# SI 507 Final Project

## Part 0. Outline of the code.

The python file `SI507_Final_code.py` contains codes to do the following:
	
  1. Use defined functions to cache the nba players' and teams' data for **a specific season** from hoops stats http://www.hoopsstats.com/.
  2. Processing players' and teams' data by two classes named `nba_player` and 'nba_team' respectively and return the data of every player or team as a tuple using a method named `return_for_database` in each class. 
  3. Create a database with tables named "Players" and "Teams". Then input tuples created before to a appropriate table in terms of the information in tuple (about player or team).
  4. Use `Flask` to show results.
 
  Note: Users can only use this database to check players or teams performance in a specific season. If users are like to see a player's performance year to year, this code would not be able to provide such a result.

## Part 1. Class definition

* Class `nba_player` methods:
  
  1. Constructor: Use a `Beautifulsoup instance` and a NBA `team name` as input. This constructor builds 14 attributes for this class, including: 
	  	1) Player's name; 
	  	2) Attendance; 
	  	3) Minute; 
	  	4) Point; 
	  	5) Rebound; 
	  	6) Assist; 
	  	7) Steal; 
	  	8) Block; 
	  	9) Turnover; 
	  	10) Field goal made percentage; 
	  	11) 3-point made percentage; 
	  	12) Free throws makde percentage; 
	  	13) Efficiency; 
	  	14) Player's team

  2. repr: Return a string including all informtion built in the constructor.

  3. contains: Input a player's and a team's name and check if they are both included in the `repr` method.

  4. return_for_database: return a tuple including all information built in the constructor.

  Note: 1) All data here is game-average.

* Class `nba_team` methods:

  1. Constructor: Use a `Beautifulsoup instance` as input. This constructor builds 13 attributes for this class, including: 
	    1) Team's name;
	    2) Total game;
	    3) Win game;
	    4) Point;
	  	5) Rebound; 
	  	6) Assist; 
	  	7) Steal; 
	  	8) Block; 
	  	9) Turnover; 
	  	10) Field goal made percentage; 
	  	11) 3-point made percentage; 
	  	12) Free throws makde percentage; 
	  	13) Efficiency; 

  2. repr: Return a string including all informtion built in the constructor.

  3. return_for_database: return a tuple including all information built in the constructor.

  Note: All data here is game-average except Team's name, Total game, Win game.

## Part 2. Steps to run the code

*  **1. Prepare the environment**: Before running this code, User should make sure that the code will be runned by **Python 3** and all packages in **requirements.txt** have been installed correctly (you may create a virtual environment to do this).

* **2. Build database**: Create a local database and fill in the value of variables in `Secret.py` according to the database's name, user's name and user's password.

* **3. Control variables**: There are several control variables have to be set before running the code:

  1) `Cache_data_and_reset_tale`: 
    a) Value: True/False.
    b) **How to use**: If it is true, the code will cache player's and team's data from htmls (or read them if they have been cached before) and rebuild two tables filled with data cached (or readed) before.
  2) `Selection_season`:
    a) Value: a number in string format, eg. "18", "09".
    b) **How to use**: Choose a season you want to check, the lastest one is "18". Here, "18" means season 2017-2018, "06" means season 2005-2006, etc.
    The supporting scope should be `"98"` to `"18"`.
  3) `Upadate`:
    a) Value: True/False
    b) **How to use**: It should be used combing with `Selection_season`. If it is true, the code will run to delete all files in a specific folder which includes all teams' and players' data for a specific NBA season.

    Note: Basiclly we only use `Update` when `Select_season = "18"`, since new games happen everyday.

  4) `run_app`: 
    a) Value: True/False
    b) **How to use**: If it is true, the code will run the `Flask` part to show results.

  5) `hard_path`: User should input a path which is the place to store all data cached by this code.


* **4. Use `localhost:5000` to see result**
	

  3. Several local links you can use to get data:


	  	1) `localhost:5000/player`: **Show any player's data.** 
	  	**Instruction**: This link will show a textbox. You can type any word in it, even parts of a name and click `Send`, then you will see all players' data whose name (first name and last name) includes the word you typed before. The data is from the "Players" table.
	  	**Example**: Type "james" (or "ame") into textbox and click "Send", you will see several players whose name includes "james" ("ame"). If you type "lebron james", only one result will be showed. If no player's name includes the word you type, you will see "there is no result!" in the page. 

        Note: 
        Input is case insensitive, so do not worry about capitalization of first letter. So does the search for team!
        There may be several players have same name but in different team, which means one player was traded during the season.


	  	2) `localhost:5000/team`: **Show any team's data.**
	  	**Instruction**: Same as checking player's data, but you should type team's name this time. The data is from the "Teams" table.
	  	**Example**: Type "hawks" in the textbox and "send", you will see the data of team Atlanta Hawks. 

	  	3) `localhost:5000/mvp`: **Show the best player of each team.**
	  	**Instruction**: The  There is no input. You should be able to see 30 players' name, points, rebounds, assists and team in the page. The "Best player" is defined as the player who gets the largest number of the sum of "Point", "Rebound", and "Assist". 30 players should be different if the season is different. The data is from the "Players" table.

	  	4) `localhost:5000/player/average`: **Show the average data for all nba players**.
	  	**Instruction**: There is no input. You should be able to see the average data which is for all NBA players. One thing need to be declared is that "all players" only includes players whose "Minute" is larger than 10.0 in order to filter out players who only playe in "garbage time".

	  	5) `localhost:5000/mvp/percentage`: **Show the best players in each team contribute how much in team's points, rebounds and assists (in percentage).**
	  	**Instruction**: There is no input. You can see the 30 player's name, player's point to team's point in percentage, player's rebound to team's rebound in percentage, player's assist to team's assist in percentage and team's name. The result is calculated by the data from table "Players" and table "Teams"

* **5. Whole process of running the code**: Assume `Cache_data_and_reset_table = True`, and there is no data cached before. 

  0) In Git, run `python3 SI507_Final_code runserver`.
  1) The code will access and cache the hoops stats website http://www.hoopsstats.com/ to get each team's page (eg. Atlanta Hawks in season 2017-2018: http://www.hoopsstats.com/basketball/fantasy/nba/atlanta-hawks/team/profile/18/1) and team's player's page (eg. Atlanta Hawks in season 2017-2018: http://www.hoopsstats.com/basketball/fantasy/nba/atlanta-hawks/team/playerstats/18/1/1). Therefore, in the folder you choose to store data, there should be 30 html files for teams, 30 html files for teams' players, and 1 html file for hoops stats main page. 
  2) Pass the teams' and players' data collected from these pages to two classes we set up before and we will get two list named "team_list" and "player_list" respectively. The elements of the former one are all instance of "nba_team" class and the elements of the latter one are all instance of "nba_player" class.
  3) Use these two lists to input data into database to build `Players` and 'Teams' tables.
  4) Finally, we are able to open the web browser, input `localhost:5000` in address bar. We should be able to see "Welcome to NBA databse" on the screen if everything goes right.
