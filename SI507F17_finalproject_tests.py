from SI507F17_finalproject import *

class Files_and_functions_check_part(unittest.TestCase):

	def setUp(self):
		self.hoopstats_main = open(os.path.join(path,"nba_main"+"_"+str(Select_season)+".html"),"r")
		self.folder = os.path.dirname(path)
		self.test_dir = tempfile.mkdtemp()
		self.file_inst = cache_or_read_html("Cleveland Cavaliers_player_stats_17.html")
		self.get_team_name_inst = get_team_name_and_link(cache_or_read_html("nba_main",basic_link, path),Select_season)
		self.get_player_stats_inst = self.get_team_name_inst[0]
		self.get_inividual_player_inst = get_individual_player_data(self.get_team_name_inst[0][0],basic_link, self.get_team_name_inst[1][0], path)

	def test_files_and_folder_exist(self):
		self.assertTrue(self.hoopstats_main.read())
		self.assertTrue(os.path.exists(self.folder))

	def test_ensure_dir(self):
		self.assertTrue(ensure_dir(self.test_dir))
		self.assertFalse(ensure_dir(path+"teat_folder/"))
		shutil.rmtree(path+"teat_folder/")

	def test_Update_data_for_one_season(self):
		ensure_dir(path+"test_folder0/")
		self.assertTrue(Update_data_for_one_season(path+"test_folder0/"))
		self.assertFalse(Update_data_for_one_season(path+"test_folder1/"))
		
	def test_cache_or_read_html(self):
		self.assertIsInstance(self.file_inst,str)
		self.assertNotEqual(self.file_inst, "")

	def test_get_team_name_and_link(self):
		self.assertEqual(len(self.get_team_name_inst),2)
		self.assertIsInstance(self.get_team_name_inst[0], list)
		self.assertIsInstance(self.get_team_name_inst[1], list)
		self.assertNotEqual(self.get_team_name_inst[0], [])
		self.assertNotEqual(self.get_team_name_inst[1], [])

	def test_player_stats_page(self):
		self.assertIsInstance(self.get_player_stats_inst, list)
		self.assertNotEqual(self.get_team_name_inst[0], [])

	def test_individual_player_data(self):
		self.assertIsInstance(self.get_inividual_player_inst, list)
		self.assertNotEqual(self.get_inividual_player_inst, [])

	def tearDown(self):
		self.hoopstats_main.close()
		shutil.rmtree(self.test_dir)
		if os.path.exists(path+"/test_folder1/"):
			shutil.rmtree(path+"/test_folder1/")
		if os.path.exists(path+"/test_folder0/"):
			shutil.rmtree(path+"/test_folder0/")


class Class_and_database_part(unittest.TestCase):

### Here we use the data of Cleveland Cavaliers in 2016-2017 season as input example
	
	def setUp(self):

		# Instance for player
		self.f1 = open("Cleveland Cavaliers_player_stats_17.html","r", encoding = "utf-8")
		self.soup_player = BeautifulSoup(self.f1.read(),"html.parser").find_all("table", class_="statscontent")
		self.player_inst = nba_player(self.soup_player[0]) # Should be Lebron James's data
		self.f1.close()

		# Instance for team
		self.f2 = open("Cleveland Cavaliers_17.html", "r", encoding = "utf-8")
		self.soup_team = BeautifulSoup(self.f2.read(), "html.parser")
		self.team_inst = nba_team(self.soup_team)
		self.f2.close()		

		# Instance for database
		self.conn = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))	
		self.cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
		self.query = """SELECT * FROM "Players" """

### Player part
	def test_player_constructor(self):

		self.assertIsInstance(self.player_inst.name, str)
		self.assertIsInstance(self.player_inst.att, int)
		self.assertIsInstance(self.player_inst.min, float)
		self.assertIsInstance(self.player_inst.pts, float)
		self.assertIsInstance(self.player_inst.reb, float)
		self.assertIsInstance(self.player_inst.ast, float)
		self.assertIsInstance(self.player_inst.stl, float)
		self.assertIsInstance(self.player_inst.blk, float)
		self.assertIsInstance(self.player_inst.pct_all, float)
		self.assertIsInstance(self.player_inst.pct_3ps, float)
		self.assertIsInstance(self.player_inst.pct_fs, float)
		self.assertIsInstance(self.player_inst.eff, float)


	def test_player_repr(self):
		self.assertEqual("Name: {}\nAttendance: {}\nMinute: {}\nPoint: {}\nRebound: {}\nAssist: {}\nSteal: {}\nBlock: {}\nTurnover: {}\nFiled_Goals_Made_Pct: {}\n3_Points_Pct: {}\nFree_Throws_Pct: {}\nEfficiency: {}\n".format(self.player_inst.name,self.player_inst.att,self.player_inst.min,self.player_inst.pts,self.player_inst.reb,self.player_inst.ast,self.player_inst.stl,self.player_inst.blk,self.player_inst.to,self.player_inst.pct_all,self.player_inst.pct_3ps,self.player_inst.pct_fs,self.player_inst.eff), self.player_inst.__repr__())

	def test_player_contains(self):
		self.assertTrue("Lebron" in  self.player_inst)
		self.assertFalse(self.player_inst.__contains__("Kobe"))

	def test_player_return(self):
		self.assertIsInstance(self.player_inst.return_for_database(), tuple)
		self.assertEqual(len(self.player_inst.return_for_database()),13)
		self.assertIn(self.player_inst.name, self.player_inst.return_for_database())
		self.assertIn(self.player_inst.att, self.player_inst.return_for_database())
		self.assertIn(self.player_inst.pts, self.player_inst.return_for_database())
		self.assertIn(self.player_inst.reb, self.player_inst.return_for_database())
		self.assertIn(self.player_inst.ast, self.player_inst.return_for_database())
		self.assertIn(self.player_inst.stl, self.player_inst.return_for_database())
		self.assertIn(self.player_inst.blk, self.player_inst.return_for_database())
		self.assertIn(self.player_inst.min, self.player_inst.return_for_database())	


	# Team part
	def test_team_constructor(self):
		self.assertIsInstance(self.team_inst.name, str)
		self.assertIsInstance(self.team_inst.total_game, int)
		self.assertIsInstance(self.team_inst.win_game, int)
		self.assertIsInstance(self.team_inst.pts, float)		
		self.assertIsInstance(self.team_inst.reb, float)
		self.assertIsInstance(self.team_inst.ast, float)
		self.assertIsInstance(self.team_inst.stl, float)
		self.assertIsInstance(self.team_inst.blk, float)
		self.assertIsInstance(self.team_inst.to, float)
		self.assertIsInstance(self.team_inst.pct_FG, float)
		self.assertIsInstance(self.team_inst.pct_3ps, float)
		self.assertIsInstance(self.team_inst.pct_FS, float)
		self.assertIsInstance(self.team_inst.eff, float)

	def test_team_repr(self):
		self.assertEqual(self.team_inst.__repr__(),"Team: {}\nTotal Game: {}\nWon Game: {}\nPoint: {}\nRebound: {}\nAssist: {}\nSteal: {}\nBlock: {}\nTurnover: {}\nFiled_Goals_Pct: {}\n3_Points_Pct: {}\nFree_Throws_Pct: {}\nEfficiency: {}\n".format(self.team_inst.name,self.team_inst.total_game,self.team_inst.win_game,self.team_inst.pts,self.team_inst.reb,self.team_inst.ast,self.team_inst.stl,self.team_inst.blk,self.team_inst.to,self.team_inst.pct_FG,self.team_inst.pct_3ps,self.team_inst.pct_FS,self.team_inst.eff))

	def test_team_contains(self):
		self.assertTrue("Cleveland" in self.team_inst)
		self.assertTrue("Lakers" not in self.team_inst)

	def test_team_return(self):
		self.assertTrue(self.team_inst.return_for_database(), tuple)
		self.assertEqual((self.team_inst.name,self.team_inst.total_game,self.team_inst.win_game,self.team_inst.pts,self.team_inst.reb,self.team_inst.ast,self.team_inst.stl,self.team_inst.blk,self.team_inst.to,self.team_inst.pct_FG,self.team_inst.pct_3ps,self.team_inst.pct_FS,self.team_inst.eff),self.team_inst.return_for_database())


	# Database part
	def test_execute_and_fetch(self):
		self.assertIsInstance(execute_and_fetch(self.query), list)

	if Cache_data_and_reset_table == True:
		def test_list_type(self):
			self.assertIsInstance(team_list, list)
			self.assertIsInstance(player_item, list)

		def test_list_elem(self):
			self.assertIsInstance(team_list[-1], nba_team)

	# "Flask" part		
	def test_query_player_table(self):
		self.assertIsInstance(query_player_table("james"),list)
		self.assertEqual(query_player_table('james'),query_player_table('James'))
		self.assertNotEqual(query_player_table('james'), [])

	def test_query_team_table(self):
		self.assertIsInstance(query_team_table('Cleveland'),list)
		self.assertEqual(query_team_table('Cleveland'),query_team_table('Cavaliers'))
		self.assertEqual(query_team_table('Cleveland'),query_team_table('cleve'))
		self.assertEqual(len(query_team_table('Cleveland')), 1)

			
if __name__ == '__main__':
    unittest.main(verbosity=2)





