import datetime
import math
import scipy
from scipy import optimize
import sys

TOL = .01
NUM_CALLED = 0

def loadRawGames(filename):
	fh = open(filename)
	header = "Rk,Wk,Date,Time,Day,Winner/Tie,PtsWinner,At,Loser/Tie,PtsLoser,Notes"
	headerFields = header.split(',')

	outputObj = []

	lines = [l for l in fh]
	for lineBad in lines:
		line = lineBad.strip()
		if not (len(line) == 0 or line == header):
			lineFields = line.split(',')
			toAdd = {}
			for i in range(len(headerFields)):
				toAdd[headerFields[i]] = lineFields[i]
			outputObj.append(toAdd)
	return outputObj

def cleanName(s):
	if s[0] != "(":
		return s
	else:
		return " ".join(s.split(" ")[1:])

def cleanNames(rawGames):
	for game in rawGames:
		game["Winner/Tie"] = cleanName(game["Winner/Tie"])
		game["Loser/Tie"] = cleanName(game["Loser/Tie"])

def normalizeGames(games):
	s = set()
	for g in games:
		s.add(g["Winner/Tie"])
		s.add(g["Loser/Tie"])

	teams = list(s)

	for g in games:
		g["Winner/Tie"] = teams.index(g["Winner/Tie"])
		g["Loser/Tie"] = teams.index(g["Loser/Tie"])

	return games, teams

def loadGames(filename):
	games = loadRawGames(filename)
	cleanNames(games)
	return normalizeGames(games)

def scoreGamesWithPowers(games, powers):
	score = 0

	GAME_SCALE = 1e1
	POWER_SCALE = 1
	for g in games:
		unitDiff = (powers[g["Winner/Tie"]] - powers[g["Loser/Tie"]])/2
		ss = (GAME_SCALE*unitDiff) + .5

		happiness = None
		if ss >= 1.0:
			happiness = 0
		elif ss <= 0.01:
			happiness = -10**9
		else:
			happiness = math.log(ss)

		score += - (happiness)

	for power in powers:
		score += POWER_SCALE * power # don't give excess power

	global NUM_CALLED
	NUM_CALLED += 1
	if NUM_CALLED % 1000 == 0:
		print("Num called is %d" % NUM_CALLED)

	return score

def assignPowers(scoreFunc, numberTeams):
	powers = [.5 for i in range(numberTeams)]
	bounds = [(0,1) for i in range(numberTeams)]
	results = scipy.optimize.minimize(scoreFunc, powers, bounds = bounds, method = "SLSQP", tol = TOL)
	return results.x

def prettyPrint(chosenPowers, teams, outputFile):
	fh = open(outputFile,'w')
	rows  = []
	for i in range(len(teams)):
		rows.append( (chosenPowers[i],teams[i]))

	rows.sort(reverse = True)

	for i in range(len(rows)):
		row = rows[i]
		fh.write("[%d] %s (%.3f)\n" % (i+1, row[1], row[0]+1e-8))

def main():
	games, teams = loadGames(sys.argv[1])
	scorePowersFunc = lambda powers : scoreGamesWithPowers(games, powers)
	chosenPowers = assignPowers(scorePowersFunc, len(teams))
	prettyPrint(chosenPowers, teams,sys.argv[2])

if __name__ == "__main__":
	main()
