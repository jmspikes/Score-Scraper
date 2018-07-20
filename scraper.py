from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#function for parsing the number of games for a given league
def parseNumGames(container, amount=0, results=[], i = 0, start = 0):
	for i in range(len(container)):
		if 'a class="date-heading' in container[i]:
			#we've found the start of league section
			start = i+1
			break
	#loop until we reach the next scoreboard
	while 'a class="date-head' not in container[i]:
		print(container[i])
		#each time we find this is a new game
		if 'article class="scoreboard soccer' in container[i]:
			amount+=1
			print("amount updated %s" % amount)
		#if we reach end of blob
		if '</html>' in container[i]:
			results.append(amount)	
			return results;
		i+=1
	results.append(amount)
	amount = 0		
	if i < len(container):
		results = parseNumGames(container, amount, results, i, start)
	return results;	


"""
	NOTE: necessary as there isn't a way to find how many 
	games there are for each league, all items on page have same parent
	and league names aren't related to game cards
""" 
def parseSoup(soup):
	#parses HTML blob
	soup = soup.prettify()
	#splits each line into a list, can now find how many games between two given hrefs
	content = soup.split('\n')
	""" 
	debugging purposes
	the_file = open("output.txt", 'w')
	for item in content:
		the_file.write("%s \n" % item)
	the_file.close()
	"""
	return content;
	
options = Options()
#used to initialize driver, for some reason cannot run headless on windows
driver = webdriver.Chrome(chrome_options=options, executable_path=r"C:\Users\Jon\Desktop\scraper\chromedriver.exe")
#maximize used to get full team name instead of abbreviation
driver.maximize_window()
#gets score page, will be scaled for all pages in the future, hardcoded for now
driver.get("http://espn.com/soccer/scoreboard/_/league/all/date/20180715")
#gets names of teams
nameContainer = driver.find_elements_by_class_name("short-name")
#gets scores
scoreContainer = driver.find_elements_by_class_name("score")
#gets leagues
leagueContainer = driver.find_elements_by_class_name("date-heading")
#gets segment of page with scores on it
scoreBoard = driver.find_element_by_id("events")
#takes segment of page and sends it to beautifulsoup
soup = BeautifulSoup(scoreBoard.get_attribute("innerHTML"), "lxml")
soup = parseSoup(soup)
gamesPerLeague = parseNumGames(soup)
for i in gamesPerLeague:
	print(gamesPerLeague[i])
#gets team logos
pictures = driver.find_elements_by_xpath("//div[@class='logo']//img[@src]")
#below adds those items to lists
leagueNames = list()
teamNames = list()
scores = list()
flags = list()
for element in nameContainer:
	teamNames.append(element.text)
for element in scoreContainer:
	scores.append(element.text)
for element in leagueContainer:
	leagueNames.append(element.text)
for element in pictures:
	flags.append(element.get_attribute("src"))

driver.quit()
