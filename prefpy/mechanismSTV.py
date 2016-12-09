import sys
from .mechanism import Mechanism
from .preference import Preference
from .profile import Profile

class MechanismSTV(Mechanism):
	"""
	Goal is to return the winner of STV Voting (plurality each round, where loser
	drops out every round until there is a winner).
	Inherits from the general scoring mechanism.
	"""

	def computeRoundLoser(self, profile, droppedOut):
		"""
		Computes who should drop out on a round

		profile - voting profile given
		droppedOut - list of candidates who have already dropped out
		"""

		# Return if all the candidates have already dropped out of the election
		if (len(droppedOut) == len(profile.candMap) - 1):
			return

		rankMaps, counts = [], []
		for preference in profile.preferences:
			rankMaps.append(preference.getReverseRankMap())
			counts.append(preference.count)

		# Make sure the lists are same size
		if (len(rankMaps) != len(counts)):
			print("Something is wrong")

		# Compute vote totals for each candidate that hasn't dropped out
		totals = dict()
		for k in range(len(rankMaps)):
			flag = False
            #  Ranks are listed starting from 1
			rank = rankMaps[k]
			for i in range(1, len(rank) + 1):
				for j in range(0, len(rank[i])):
					if (rank[i][j] not in droppedOut):
						new_rank = rank[i][j]
						if (rank[i][j] in totals):
							totals[rank[i][j]] += counts[k]
						else:
							totals[rank[i][j]] = counts[k]
						flag = True
				if flag:
					break

		voteTotals = list(totals.values())
		allVotes = 0
		minVotes = sys.maxsize
		maxVotes, maxIndex, majKey = -1, -1, -1

		# Compute largest # of a votes received by any candidate
		for i in range (len(voteTotals)):
			allVotes += voteTotals[i]
			if (voteTotals[i] > maxVotes):
				maxVotes = voteTotals[i]
				maxIndex = i
			if (voteTotals[i] < minVotes):
				minVotes = voteTotals[i]

		# Find the candidate with more than majority of votes
		for key, value in totals.items():
			if value == maxVotes:
				if (maxVotes > (allVotes/2)):
					majKey = key

		# Return a list candidates whose votes are equal to lowest # of votes
		losers = [key for key, value in totals.items() if value == minVotes]
		return (losers, majKey)

	def getSTVWinners(self, profile):
		"""
		Computes all unique winners for the election
			(considers all possible tie breaks)

		profile - voting profile given
		"""
		winners = set()
		rankings = [[]]
		losers = [[]]

		# Calculate eah round loser
		for i in range(profile.numCands - 1):
			j = 0
			while j < len(rankings):
				majKey = -1
				# Compute a winner of election
				losers[j], majKey = self.computeRoundLoser(profile, rankings[j])
				# Add it to the set of winners
				if majKey != -1:
					winners.add(majKey)
					break

				# Compute the rest of the election otherwise
				if (losers[j]):
					rankings[j].append(losers[j][0])
					# Custom Tie Breaking would be here
					for k in range(1, len(losers[j])):
						rankings.append(list(rankings[j]))
						rankings[-1].pop()
						rankings[-1].append(losers[j][k])
						losers.append([])
				j += 1

		# Return all unique winners
		return list(winners)

	def getSTVRankings(self, profile):
		"""
		Computes all poaasible full rankings for STV voting

		Returns a list of lists of all candidates in winning order:
			[[winner, 2nd winner, ... , loser], [winner, 2nd winner, ... , loser] ... ]
		"""

		# Create 2-D list of rankings and losers for possibility of ties
		rankings = [[]]
		losers = [[]]
		for i in range(profile.numCands - 1):
			j = 0
			while j < len(rankings):
				roundLoser = self.computeRoundLoser(profile, rankings[j])
				if (roundLoser):
					losers[j] = roundLoser[0]
					rankings[j].append(losers[j][0])
					for k in range(1, len(losers[j])):
						rankings.append(list(rankings[j]))
						rankings[-1].pop()
						rankings[-1].append(losers[j][k])
						losers.append([])
				j += 1

		# Now we should have a list of lists called 'rankings' which contains all rankings for different tiebreaks
		cands = profile.candMap.keys()
		for ranking in rankings:
			winner = set(cands) - set(ranking)
			ranking.append(list(winner)[0])
			ranking.reverse()

		# Returns a list of lists with full rankings of candidates in STV
		return rankings
