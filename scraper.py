from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#function for parsing the number of games for a given league
def parseNumGames(container):
	i = 0
	startCounting = False
	amount = 0
	results=[]
	#keep looping until we've reached the end of html
	while '</html>' not in container[i]:
		#denotes we're at a league name, start counting number of games for that league
		if 'a class="date-heading' in container[i]:
			#only need to set for true for being able to tally for the first result
			startCounting = True
		#move to next line
		i+=1
		#look for games if we're in a league section
		if startCounting == True:
			#if there's a game increment for that league
			if 'article class="scoreboard soccer' in container[i]:
				amount+=1
		#if next line is a league heading and we're already searching, need to add the amount
		#of games for the previous league and reset counting
		#dont need to do this for first time through a league so startCounting is necesarry
		if 'a class="date-heading' in container[i] and startCounting == True:
			results.append(amount)
			amount = 0
	#need to add results of the final league to list
	results.append(amount)
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
	print(i)
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
