from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import sys
import arrow

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
"""
	NOTE: function provides the URLS needed for scraping functions
	amount of days to scrape will be provided in command line
	takes current date then generates url for each day going back to n number of days
	"http://espn.com/soccer/scoreboard/_/league/all/date/YYYYMMDD
"""
def getDate(offset):
	#gets current time
	now = arrow.now()
	#sets offset
	offset = offset*-1
	#shifts days
	fNow = now.shift(days=offset).date()
	#converts to string to be replaced
	fNow = str(fNow)
	#gets rid of hyphens 
	fNow = fNow.replace("-", "")
	#builds string
	return fNow;

def daysToParse(number):
	listOfUrls = []

	for i in range(int(number)):
		date = getDate(i)
		listOfUrls.append("http://espn.com/soccer/scoreboard/_/league/all/date/"+date)
		listOfDates.append(date)
	return listOfUrls;

def init():
	options = Options()
	#used to initialize driver, for some reason cannot run headless on windows
	driver = webdriver.Chrome(chrome_options=options,executable_path=r"C:\Users\Jon\Desktop\scraper\chromedriver.exe")
	#maximize used to get full team name instead of abbreviation
	driver.maximize_window()
	return driver

def dataForDays(url, driver):	
	#gets score page
	driver.get(url)
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
	#gets team logos
	pictures = driver.find_elements_by_xpath("//div[@class='logo']//img[@src]")
	#parse into JSON, have to do this workaround instead of zipping
	#because for no reason the last 15 elements of the team name list would return blank elements
	jsonTeamBlob = []
	jsonBlobLeagues = []
	for i in range(len(nameContainer)-1):
		team = {nameContainer[i].text : [scoreContainer[i].text, pictures[i].get_attribute("src")]}
		jsonTeamBlob.append(team)
	for i in range(len(leagueContainer)-1):
		league = {leagueContainer[i].text : gamesPerLeague[i]}
		jsonBlobLeagues.append(league)

	return(jsonBlobLeagues, jsonTeamBlob)

def main():
	serverData = []
	#argv will always have script as first element, if that's the only item then nothing has been provided for scraping
	if len(sys.argv) == 1:
		print("Value not provided for amount to parse, exiting.")
		return;
	else: 
		urls = daysToParse(sys.argv[1])
		driver = init()
		i = 0
		for url in urls:
			serverData.append(listOfDates[i])
			serverData.append(dataForDays(url,driver))
			i+=1
			with open("data.json", 'w') as outfile:
				json.dump(serverData,outfile)
		driver.quit()
	
listOfDates = []
main()

