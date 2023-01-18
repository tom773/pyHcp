import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time
import glob
import sys
import unidecode
import math
import numpy

sys.setrecursionlimit(10000)

headers = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
current_track = ""

# Below Functions are for Scraping Data

def getAllTrackLinks(meetURL):

	page = requests.get(meetURL, headers={"User-Agent": headers})
	pageContent = page.content
	soupedPage = BeautifulSoup(pageContent, features="html.parser")

	with open("trackList.txt", "a") as outfile:
		divs = soupedPage.find_all("div", class_="list")
		for div in divs:
			links = div.find_all("a")
			for link in links:
				outfile.write(link['href']+"\n")

def getLinks(meetURL):

	meetLinks = []

	page = requests.get(meetURL, headers={"User-Agent": headers})
	pageContent = page.content
	soupedPage = BeautifulSoup(pageContent, features="html.parser")

	links = soupedPage.find_all("li", class_="latest-result")
	for link in links:
		link = link.find("a")
		meetLinks.append("https://punters.com.au{}".format(link['href']))

	return meetLinks

def getRest(meetURL):

	rawTimes = []
	cleanTimes = []
	distances = []
	conditions = []
	page = requests.get(meetURL, headers={"User-Agent": headers})
	pageContent = page.content
	soupedPage = BeautifulSoup(pageContent, features="html.parser")
	tr = soupedPage.find_all("tr",  class_="isFirst results-table__isPlaced")
	for trs in tr:
		matchedTags = trs.find_all(lambda tag: len(tag.find_all())==0 and "L" not in tag.text and "$" not in tag.text)
		for matchedTag in matchedTags:
			if "<td>" in str(matchedTag):
				rawTimes.append(str(matchedTag))
			else:
				pass
	for time in rawTimes:
		cleanTime = time.strip("<td></")
		if ":" in cleanTime:
			cleanTimeTMP = cleanTime.split(":")
			cleanTime = float(float(cleanTimeTMP[0])*60)+float(cleanTimeTMP[1])
		else:
			pass
		try:
			if cleanTime != cleanTimes[-1]:
				try:
					cleanTimes.append(float(cleanTime))
				except ValueError:
					cleanTimes.append(-0.01)
			else:
				pass
		except IndexError:
			try:
				cleanTimes.append(float(cleanTime))
			except ValueError:
				cleanTimes.append(-0.01)

	condDist = soupedPage.find_all("abbr", {"data-type": "distance"})
	for dist in condDist:
		distances.append(dist.text)

	condCond = soupedPage.find_all("span", class_="results-table__capital")
	for condConds in condCond:

		if "Soft" in condConds.text:
			conditions.append(condConds.text.strip())
		elif "Heavy" in condConds.text:
			conditions.append(condConds.text.strip())
		elif "Good" in condConds.text:
			conditions.append(condConds.text.strip())
		elif "Firm" in condConds.text:
			conditions.append("Good")
		else:
			pass

	print(conditions)
	print(cleanTimes)

	if len(cleanTimes) == len(distances):
		pass
	else:
		cleanTimes = []
		distances = []
		conditions = []

	print(len(cleanTimes))
	print(len(distances))
	print(len(conditions))
	tdcDict = {"Times": cleanTimes, "Distances": distances, "Conditions": conditions}
	print(meetURL)
	tdcFrame = pd.DataFrame(tdcDict)
	tdcFrame.to_csv("trackTimes/allTimes{}.csv".format(current_track), mode="a", header=False)

	print("Done")

def getLatest(meetURL):

	print(meetURL)

	rawTimes = []
	cleanTimes = []
	distances = []
	conditions = []
	page = requests.get(meetURL, headers={"User-Agent": headers})
	pageContent = page.content
	soupedPage = BeautifulSoup(pageContent, features="html.parser")
	tr = soupedPage.find_all("tr", {"class": "isPlaced"})
	for trs in tr:
		matchedTags = trs.find_all(lambda tag: len(tag.find_all())==0 and "L" not in tag.text and "$" not in tag.text)
		for matchedTag in matchedTags:
			if "<td>" in str(matchedTag):
				rawTimes.append(str(matchedTag))
			else:
				pass
	for time in rawTimes:
		cleanTime = time.strip("<td></")
		if ":" in cleanTime:
			cleanTimeTMP = cleanTime.split(":")
			cleanTime = float(float(cleanTimeTMP[0])*60)+float(cleanTimeTMP[1])
		else:
			pass
		try:
			print(cleanTimes[-1])
			if cleanTime != cleanTimes[-1]:
				try:
					cleanTimes.append(float(cleanTime))
				except ValueError:
					cleanTimes.append(-0.01)
			else:
				pass
		except IndexError:
			try:
				cleanTimes.append(float(cleanTime))
			except ValueError:
				cleanTimes.append(-0.01)

	condDist = soupedPage.find_all("abbr", {"data-type": "distance"})
	for dist in condDist:
		distances.append(dist.text)

	condCond = soupedPage.find_all("span", class_="capitalize")
	for condConds in condCond:
		if "SOFT" in condConds.text.upper():
			conditions.append(condConds.text.strip())
		elif "HEAVY" in condConds.text.upper():
			conditions.append(condConds.text.strip())
		elif "GOOD" in condConds.text.upper():
			conditions.append(condConds.text.strip())
		elif "FIRM" in condConds.text.upper():
			conditions.append("Good 2")
		else:
			pass

	if len(cleanTimes) < len(distances):
		toRmv = len(cleanTimes)-len(distances)
		distances = distances[:toRmv]
		conditions = conditions[:toRmv]
	else:
		pass
	print(len(cleanTimes))
	print(len(distances))
	print(len(conditions))
	tdcDict = {"Times": cleanTimes, "Distances": distances, "Conditions": conditions}
	tdcFrame = pd.DataFrame(tdcDict)
	tdcFrame.to_csv("trackTimes/allTimes{}.csv".format(current_track), mode="a", header=True)

	print("Done")

def cleanTrackList():

	links_ = []
	cleanedList = []

	with open("trackList.txt", "r+") as trackFile:

		trackList = trackFile.read().split("\n")
		for track in trackList:
			links_.append("https://punters.com.au{}results".format(track))
		links_ = links_[:-1]
		
	for link_ in links_:

		page = requests.get(link_, headers={"User-Agent": headers})
		pageContent = page.content
		soupedPage = BeautifulSoup(pageContent, "html.parser")

		links = soupedPage.find_all("li", class_="latest-result")
		print("{}: {} Past Results".format(link_, len(links)))
		if len(links) < 10:
			print("!!! Removing !!!\n")
		else:
			print("*** Keeping ***\n")
			cleanedList.append(link_)

	with open("trackList.txt", "w") as trackFile:
		for link__ in cleanedList:
			trackFile.write("{}\n".format(link__))


# Scrape Data and Insert Into Track CSV's
"""
with open("trackList.txt", "r") as trackFile:

	trackLinks = []

	readFile = trackFile.read()
	for trackLink in readFile.split("\n"):
		trackLinks.append(trackLink)

	for trackLink in trackLinks:

		current_track = re.split(r'/|_', trackLink)[4]
		meetLinks = getLinks(trackLink)
		if "pakenham" not in str(trackLink):
			getLatest(trackLink)
		else:
			pass
		for link_ in meetLinks:
			getRest(link_)
"""

# Below Functions are for Organising Data

def organiseData(trackCSV):

	outFrame = pd.DataFrame(columns=['Track', 'Distance', 'Condish', 'Par Time'])
	track = re.split(r'allTimes|.csv', trackCSV)[1]

	trackFrame = pd.read_csv(trackCSV)
	trackFrame = trackFrame.drop("Unnamed: 0", axis=1)
	trackFrame = trackFrame[trackFrame.Distances != "Distances"]
	trackFrame['Distances'] = trackFrame['Distances'].map(lambda x: x.rstrip("m"))
	trackFrame['Conditions'] = trackFrame['Conditions'].map(lambda x: x.rstrip("123456789"))
	trackFrame['Distances'] = pd.to_numeric(trackFrame['Distances'])
	trackFrame['TImes'] = pd.to_numeric(trackFrame['Times'])
	trackFrame['Conditions'] = trackFrame['Conditions'].str.lower()
	trackFrame['Conditions'] = trackFrame['Conditions'].str.strip()

	distances = trackFrame['Distances'].to_list()
	distances = list(dict.fromkeys(distances))
	conditions = ['good', 'soft', 'heavy']
	print(trackCSV)
	counter=0
	for distance in distances:
		for condition in conditions:

			data = []
			avgTime = None

			times = trackFrame.loc[(trackFrame['Distances'] == distance) & (trackFrame['Conditions']==condition), "Times"].to_list()
			try:
				avgTime = (sum(times)/len(times))
				data.append(track)
				data.append(distance)
				data.append(condition)
				data.append(avgTime)

			except ZeroDivisionError:
				data.append(track)
				data.append(distance)
				data.append(condition)
				data.append(avgTime)

			counter += 1
			outFrame.loc[counter] = data	
			
	outFrame.to_csv("allParTimes.csv", mode='a')

	"""
	distRows = trackFrame.loc[(trackFrame['Distances'] == 1100) & (trackFrame['Conditions'] == "good"), "Times"].to_list()
	print(len(distRows), "\n")
	print(sum(distRows)/len(distRows))
	"""

def getPar(track, distance, conditions):

	if conditions == "firm":
		conditions = "good"
	else:
		pass

	if int(distance) > 3200:
		return 294.69

	parTable = pd.read_csv("allParTimes.csv", index_col=0)
	parTime = parTable.loc[(parTable['Distance']==distance)&(parTable['Track']==track)&(parTable['Condish']==conditions), "Par Time"].to_list()
	if len(parTime) != 0:
		parTime = round(float(parTime[0]), 3)
	else:
		distance = str(numpy.round(int(distance), -2))
#		print("No Par Found for {}, at {}, in {}, using average value".format(track, distance, conditions))
		if "synthetic" in conditions:
			conditions = "good"
		else:
			pass
		parTime = parTable.loc[(parTable['Distance']==distance)&(parTable['Condish']==conditions), "Par Time"].to_list()
		parTime = [float(x) for x in parTime]
		parTime = [x for x in parTime if str(x) != "nan"]
		parTime = (sum(parTime)/len(parTime))

	return parTime

# Functions for returning the 3 past performances of each runner in a race

def getListOfMeetings(baseMeetURL, maidensEnd):

	page = requests.get(baseMeetURL, headers={"User-Agent": headers})
	pageContent = page.content
	soupedPage = BeautifulSoup(pageContent, features="html.parser")

	meetings_ = []
	meetings = soupedPage.find_all("a", {"class": "form-overview__full-form-link"})

	for meeting in meetings:
		meetings_.append("https://punters.com.au{}".format(meeting['href']))

	meetings_ = meetings_[int(maidensEnd):]
	for meeting in meetings_:

		getRunners(meeting)

def getRunners(raceURL):

	page = requests.get(raceURL, headers={"User-Agent": headers})
	pageContent = page.content
	soupedPage = BeautifulSoup(pageContent, features="html.parser")

	runners_ = []
	runners = soupedPage.find_all("a", {"class": "form-guide-overview__horse-link"})
	for runner in runners:
		runners_.append("https://punters.com.au{}".format(runner['href']))
	for runner_ in runners_:
		print(runner_)
		getPast3ParsForRunner(runner_)

# Returns all real races in past 10, dataframe w/ parTime, winTime, and lenBtn
def getPast3ParsForRunner(horseURL):

	page = requests.get(horseURL, headers={"User-Agent": headers})
	pageContent = page.content
	soupedPage = BeautifulSoup(pageContent, features="html.parser")

	conditions = []
	tracks = []
	distances = []

	discs = soupedPage.find_all("li", {"class": 'timeline-disc'})
	# Get List of Conditions
	for disc in discs:
		if "TRIAL" in disc.text:
			pass
		else:
			condish = disc.find("span", {'class': "badge"})
			try:
				condition = condish.text.strip()
				conditions.append((unidecode.unidecode(re.sub(r"[0-9]| ", "", condition))).strip().lower())
			except AttributeError:
				pass
	# Get List of Distances
	for disc in discs:
		if "TRIAL" in disc.text:
			pass
		else:
			dist = disc.find("span", {'class': "dist simlight"})
			try:
				distance = dist.text.strip()
				distance = re.sub(r"[m]", "", distance)
				distances.append(distance)
			except AttributeError:
				pass
	# Get Track Name
	for disc in discs:
		if "TRIAL" in disc.text:
			pass
		else:
			trackName = disc.find("b")
			try:
				trackNdate = trackName.text
				if "bet365" in trackNdate:
					trackNdate = re.sub(r'bet365 ', '', trackNdate)
				elif "Apiam" in trackNdate:
					trackNdate = re.sub(r'Apiam', '', trackNdate)
				elif "TAB Park" in trackNdate:
					trackNdate = re.sub(r"TAB Park ", "", trackNdate)
				elif "Royal" in trackNdate:
					trackNdate = re.sub(r'Royal ', '', trackNdate)
				elif "Rosehill At" in trackNdate:
					trackNdate = re.sub(r"Rosehill At ", "", trackNdate)
				track = re.split(r"[0-9]", trackNdate)
				if re.sub(r" ", "-", (track[0].strip().lower())) != "the-valley":
					tracks.append(re.sub(r" ", "-", (track[0].strip().lower()))) 
				else:
					theV = re.sub(r" ", "-", (track[0].strip().lower()))
					moonV = re.sub(r"the", "moonee", theV)
					tracks.append(moonV)
			except AttributeError:
				pass

	horsePast3 = pd.DataFrame(columns=['track', 'distance', 'condition'])
	horsePast3['condition'] = conditions
	horsePast3['track'] = tracks
	horsePast3['distance'] = distances

	parTimesPast3 = []
	for index, row in horsePast3.iterrows():
		par = getPar(row['track'], str(row['distance']), row['condition'])
		parTimesPast3.append(par)

	pastPerformanceTable = pd.DataFrame(columns=['parTime', 'winTime', 'lenBtn'])
	winLenTable = getWinningTimes(horseURL, soupedPage)

	winTime = winLenTable['winTime'].to_list()
	lenBtn = winLenTable['lenBtn'].to_list()

	pastPerformanceTable['winTime']=winTime
	pastPerformanceTable['parTime']=parTimesPast3[:3]
	pastPerformanceTable['lenBtn']=lenBtn

	makeCalcs(pastPerformanceTable, horseURL)

def makeCalcs(pastPerformanceTable, horseURL):

	ratings = []
	if len(pastPerformanceTable) == 0:
		ratings.append(0)
	else:
		for x in range(3):
			try:
				values = pastPerformanceTable.iloc[x].to_list()
			except IndexError:
				pass
			try:
				adjSec = values[2]/6
			except ZeroDivisionError:
				adjSec = 0

			values = [float(x) for x in values]
			finalTime = values[1] + adjSec
			finalRating = numpy.round((100+((values[0]-finalTime)*10)), 2)

			ratings.append(numpy.round(finalRating, 2))
	
	horsey = re.split(r"/", horseURL)[4]
	horsey = re.sub(r"-", " ", horsey)
	horsey = re.sub(r"_", "", horsey)
	horsey = re.sub(r"[0-9]", "", horsey)

	finalOutPut = pd.DataFrame(columns=['Horse Name', "Final Rating"])
	finalOutPut['Horse Name']=[(horsey)]
	finalOutPut['Final Rating']=numpy.round((sum(ratings)/len(ratings)), 2)

	finalOutPut.to_csv("flemington/Race2.csv", mode='a', header=False)

# Returns Non Trial Runs
def returnNonTrials(runs):

	tgtLength = 4
	counter = 0
	realRuns = []
	for elem in runs:
		if len(elem) >= 4:
			realRuns.append(counter)
		else:
			pass
		counter += 1

	return realRuns

# Gets Past 3 Winning Times and Lens Beaten
def getWinningTimes(horseURL, soupy):

	winningTimes = []
	lengthsOff = []
	horseName = re.split(r"/|_", horseURL)[4]
	ppTable = pd.DataFrame(columns=['winTime', 'lenBtn'])

	blockText = soupy.find_all("li", {"class": "timeline-disc"})
	for blockText_ in blockText:
		form = blockText_.find("span", class_=None)
		try:
			if "TRL" in form.text:
				pass
			elif "TRIAL" in blockText_.text:
				pass
			else:
				if "France" in blockText_.text:
					pass
				else:

					winningTime = (re.split(r"Winning Time: |, SP:|In-running:", form.text)[1].strip())
					if ":" in winningTime:
						winningTime = winningTime.split(":")
						winningTime = round(float(int(winningTime[0])*60)+float(winningTime[1]), 2)
						winningTimes.append(winningTime)
					else:
						winningTimes.append(winningTime)
		except AttributeError:
			pass
	"""
	winners = []
	for psd in soupy.find_all("ul", {"class": "timeline"}):
		ntpd = psd.find_all("p", {"class": "inner-box__full-result"})
		if len(ntpd) != 0:
			fps = psd.find_all("span", {"class": "timeline-right"})
			winningHorse = []
			for fp in fps:
				horsesInRace = fp.find_all("a", {"class": 'simlight'})
				for x in horsesInRace:
					winningHorse.append(re.split(r"\n", x.text))
			winners.append(winningHorse[0])
		else:
			pass
	"""
	lengthsBeaten = []
	tmpCleanRuns = []
	runs = []
	for resultsSet in soupy.find_all("span", {"class": "timeline-right placed"}):
		results = list((x.text for x in resultsSet.findChildren()))
		tmpCleanRuns.append(results)
		strings = re.sub(r" |\n", "", resultsSet.text)
		strings = re.split(r"\)", strings)
		runs.append(re.sub("L", "", strings[1]))
	
	for i in range(len(runs)):
		if runs[i] == "":
			runs[i] = 0
		else:
			pass
		runs[i] = float(runs[i])

	realRuns = returnNonTrials(tmpCleanRuns)
	finalLenBtnList = []
	for run in realRuns:
		finalLenBtnList.append(runs[run])

	finalLenBtnList = finalLenBtnList[:3]
	winningTimes = winningTimes[:3]
	ppTable['lenBtn'] = finalLenBtnList	
	ppTable['winTime'] = winningTimes
	
	return ppTable

getListOfMeetings("https://www.punters.com.au/form-guide/newcastle_236489/", "6")


#getPast3ParsForRunner("https://punters.com.au/horses/cannon-hill_892856/")



