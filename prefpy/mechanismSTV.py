import math
import io
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

		if (len(droppedOut) == len(profile.candMap) - 1):
			return

		rankMaps, counts = [], []
		for preference in profile.preferences:
			rankMaps.append(preference.getReverseRankMap())
			counts.append(preference.count)

		if (len(rankMaps) != len(counts)):
			print("Something is wrong")

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

		voteTotals = totals.values()
		minVotes = sys.maxsize

		for vote in voteTotals:
			if (vote < minVotes):
				minVotes = vote

		losers = [key for key, value in totals.items() if value == minVotes]
		return losers

	def getSTVRankings(self, profile):
		"""
		Computes the winners (and losers) for STV voting

		Returns a list of lists of all candidates in winning order:
			[[winner, 2nd winner, ... , loser], [winner, 2nd winner, ... , loser] ... ]
		"""
		#create 2-D list of losers and dropouts for possibility of ties
		losers = [[]]
		dropouts = [[]]

		for i in range(profile.numCands - 1):
			j = 0
			while j < len(losers):
				dropouts[j] = self.computeRoundLoser(profile, losers[j])
				if (dropouts[j]):
					losers[j].append(dropouts[j][0])
					for k in range(1, len(dropouts[j])):
						losers.append(list(losers[j]))
						losers[-1].pop()
						losers[-1].append(dropouts[j][k])
						dropouts.append([])
				j += 1

		# Now we should have a list of lists called 'losers' which contains all losers for different tiebreaks
		cands = profile.preferences[0].getRankMap().keys()
		for loser in losers:
			winner = set(cands) - set(loser)
			loser.append(list(winner)[0])
			loser.reverse()

		#returns a list of lists with full rankings of candidates in STV
		return losers
