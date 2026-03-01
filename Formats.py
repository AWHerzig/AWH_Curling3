from PlayerMovement import *

class LEAGUE:
    def __init__(self, name, teams):
        self.name = name
        self.slate = 0
        self.STANDINGS = pd.DataFrame(index = teams, columns = ['Wins', 'Losses', 'EEWins', 'PD'], data=0)
        self.SCHEDULE = round_robin(teams)
        self.BRACKET = None
        self.tWinner = None
        self.prequal = []

    def amIDone(self):
        return self.slate > 22
    
    def playNextSlate(self, handle):
        if self.slate < 19:
            for match in self.SCHEDULE[self.slate]:
                Result = gameWrapper(match[0], match[1])
                handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name} League Play', self.slate + 1] + Result
                self.STANDINGS.loc[Result[0], 'PD'] += Result[1]-Result[2]
                self.STANDINGS.loc[Result[3], 'PD'] += Result[2]-Result[1]
                if Result[1] > Result[2]:
                    self.STANDINGS.loc[Result[0], 'Wins'] += 1
                    if Result[4]:
                        self.STANDINGS.loc[Result[0], 'EEWins'] += 1
                    self.STANDINGS.loc[Result[3], 'Losses'] += 1
                else:
                    self.STANDINGS.loc[Result[3], 'Wins'] += 1
                    if Result[4]:
                        self.STANDINGS.loc[Result[3], 'EEWins'] += 1
                    self.STANDINGS.loc[Result[0], 'Losses'] += 1
            self.STANDINGS = self.STANDINGS.sort_values(['Wins', 'EEWins', 'PD'], ascending=[False, True, False])
            if self.slate == 18:
                handle.WINNERS.loc[len(handle.WINNERS)] = [handle.YEAR, f'{self.name} League Play', self.STANDINGS.index[0]]
                self.BRACKET = Bracket(f'{self.name} Playoffs', list(self.STANDINGS.index[:7]) + [None, None] + list(self.STANDINGS.index[7:10]))
        elif self.slate < 23:
            self.BRACKET.playNextSlate(handle)
            if self.slate == 22:
                self.tWinner = self.BRACKET.winner
                self.prequal.append(self.BRACKET.winner)
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate < 19:
            print(self.name)
            for match in self.SCHEDULE[self.slate]:
                print(f'{match[0]} ({self.STANDINGS.loc[match[0], "Wins"]}-{self.STANDINGS.loc[match[0], "Losses"]}) vs. {match[1]} ({self.STANDINGS.loc[match[1], "Wins"]}-{self.STANDINGS.loc[match[1], "Losses"]})')
        elif self.slate < 23:
            self.BRACKET.displayNextSlate()
        else:
            print('Season Over')
    
    def popqual(self):
        Next = self.STANDINGS.drop(self.prequal).index[0]
        self.prequal.append(Next)
        return Next
        
class Bracket:
    def __init__(self, name, teams, seeded = True):
        self.name = name
        self.teams = teams
        self.seeded = seeded
        self.blist = list(teams)
        self.ogblist = self.blist.copy()
        self.depth = int(np.ceil(np.log2(len(self.blist))))
        self.winner = None

    def pygameDisplay(self):
        bracket(self.blist, self.ogblist, caption=self.name, seeded=self.seeded)

    def displayNextSlate(self):
        if self.depth == 0:
            print("Bracket complete.")
            return
        print(self.name)
        diffTarget = 2**self.depth+1
        for i in range(diffTarget//2):
            if self.blist[i] is not None:
                tarind = diffTarget - i - 2
                if len(self.blist) > tarind and self.blist[tarind] is not None:
                    if self.seeded:
                        print(f'#{index_ignore_none(self.ogblist, self.blist[i])+1} {self.blist[i]} vs #{index_ignore_none(self.ogblist, self.blist[tarind])+1} {self.blist[tarind]}')
                    else:
                        print(f'{self.blist[i]} vs {self.blist[tarind]}')

    def playNextSlate(self, handle):
        if self.depth == 0:
            print("Bracket complete.")
            return
        diffTarget = 2**self.depth+1
        for i in range(diffTarget//2):
            if self.blist[i] is not None:
                tarind = diffTarget - i - 2
                if len(self.blist) > tarind and self.blist[tarind] is not None:
                    result = gameWrapper(self.blist[i], self.blist[tarind])
                    handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name}', [None, 'Final', 'SF', 'QF', 'R1'][self.depth]] + result
                    winner = result[0] if result[1] > result[2] else result[3]
                    self.blist[i] = winner
                    self.blist[tarind] = None
        self.depth -= 1
        self.blist = trim_trailing_none(self.blist)
        if self.depth == 0:
            self.winner = self.blist[0]
            handle.WINNERS.loc[len(handle.WINNERS)] = [handle.YEAR, f'{self.name}', self.blist[0]]

            

class Swiss:
    def __init__(self, name, teams):
        self.name = name
        self.teams = teams
        self.tiers = [teams, [], [], []]
        random.shuffle(self.tiers[0])
        self.stage = 1

    def getAdvanced(self):
        if self.stage < 6:
            print('Not Done Yet')
        return self.tiers[3]

    def displayNextSlate(self):
        if self.stage > 5:
            print('Over')
            return
        for tier in range(3):
            if tier < self.stage - 3:
                continue
            if len(self.tiers[tier]) == 0:
                continue
            print(self.name, 'Tier', tier)
            for i in range(0, len(self.tiers[tier]), 2):
                print(f'{self.tiers[tier][i]} vs. {self.tiers[tier][i+1]}')

    def playNextSlate(self, handle):
        if self.stage > 5:
            print('Over')
            return
        curtiers = self.tiers.copy()
        self.tiers = [[], [], [], self.tiers[3]]
        for tier in range(3):
            if tier < self.stage - 3:
                continue
            if len(curtiers[tier]) == 0:
                continue
            for i in range(0, len(curtiers[tier]), 2):
                result = gameWrapper(curtiers[tier][i], curtiers[tier][i+1])
                handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name}', self.stage] + result
                winner, loser = (result[0], result[3]) if result[1] > result[2] else (result[3], result[0])
                self.tiers[tier].append(loser)
                self.tiers[tier+1].append(winner)
        for grp in self.tiers:
            random.shuffle(grp)
        self.stage += 1

    
class MiniSwiss: # Basically a mini swiss lol
    def __init__(self, name, teams):
        self.name = name
        self.teams = teams
        self.tiers = [teams, [], []]
        random.shuffle(self.tiers[0])
        self.stage = 1

    def getAdvanced(self):
        if self.stage < 4:
            print('Not Done Yet')
        return self.tiers[2]

    def displayNextSlate(self):
        if self.stage > 3:
            print('Over')
            return
        for tier in range(2):
            if tier < self.stage - 2:
                continue
            if len(self.tiers[tier]) == 0:
                continue
            print(self.name, 'Tier', tier)
            for i in range(0, len(self.tiers[tier]), 2):
                print(f'{self.tiers[tier][i]} vs. {self.tiers[tier][i+1]}')

    def playNextSlate(self, handle):
        if self.stage > 3:
            print('Over')
            return
        curtiers = self.tiers.copy()
        self.tiers = [[], [], self.tiers[2]]
        for tier in range(2):
            if tier < self.stage - 2:
                continue
            if len(curtiers[tier]) == 0:
                continue
            for i in range(0, len(curtiers[tier]), 2):
                result = gameWrapper(curtiers[tier][i], curtiers[tier][i+1])
                handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name}', self.stage] + result
                winner, loser = (result[0], result[3]) if result[1] > result[2] else (result[3], result[0])
                self.tiers[tier].append(loser)
                self.tiers[tier+1].append(winner)
        for grp in self.tiers:
            random.shuffle(grp)
        self.stage += 1

class DubElim32:
    def __init__(self, name, teams):
        self.name = name
        self.teams = teams
        self.upper = teams 
        random.shuffle(self.upper)
        self.lower = []
        self.hold = []
        self.winner = None
        self.stage = 1

    def displayNextSlate(self):
        if self.stage >= 11:
            return 
        print(self.name)
        if self.stage == 10:
            print(self.upper[0], 'vs', self.lower[0])
        elif self.stage == 1 or self.stage % 2 == 0:
            print('UPPER')
            for i in range(0, len(self.upper), 2):
                print(self.upper[i], 'vs', self.upper[i+1])
        if 1 < self.stage < 10:
            print('LOWER')
            for i in range(0, len(self.lower), 2):
                print(self.lower[i], 'vs', self.lower[i+1])

    def playNextSlate(self, handle):
        self.hold = []
        if self.stage >= 11:
            return 
        elif self.stage == 10:
            result = gameWrapper(self.upper[0], self.lower[0])
            handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name}', f'GRAND FINAL'] + result
            winner, loser = (result[0], result[3]) if result[1] > result[2] else (result[3], result[0])
            if self.upper[0] == winner:
                self.winner = self.upper[0]
                handle.WINNERS.loc[len(handle.WINNERS)] = [handle.YEAR, f'{self.name}', self.winner]
            else:
                result = gameWrapper(self.lower[0], self.upper[0])
                handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name}', f'GRAND FINAL - BRACKET RESET'] + result
                winner, loser = (result[0], result[3]) if result[1] > result[2] else (result[3], result[0])
                self.winner = winner
                handle.WINNERS.loc[len(handle.WINNERS)] = [handle.YEAR, f'{self.name}', self.winner]
        elif self.stage == 1 or self.stage % 2 == 0:
            uppers = self.upper.copy()
            self.upper = []
            for i in range(0, len(uppers), 2):
                result = gameWrapper(uppers[i], uppers[i+1])
                handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name}', f'UPPER-{len(uppers)}'] + result
                winner, loser = (result[0], result[3]) if result[1] > result[2] else (result[3], result[0])
                self.upper.append(winner)
                self.hold.append(loser)
        if 1 < self.stage < 10:
            lowers = self.lower.copy()
            self.lower = []
            for i in range(0, len(lowers), 2):
                result = gameWrapper(lowers[i], lowers[i+1])
                handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name}', f'LOWER-{10-self.stage}'] + result
                winner, loser = (result[0], result[3]) if result[1] > result[2] else (result[3], result[0])
                self.lower.append(winner)
        self.lower = self.lower + self.hold
        self.hold = []
        random.shuffle(self.lower)
        random.shuffle(self.upper)
        self.stage += 1


class GROUP:
    def __init__(self, name, teams):
        self.name = name
        self.slate = 0
        self.STANDINGS = pd.DataFrame(index = teams, columns = ['Wins', 'Losses', 'EEWins', 'PD'], data=0)
        self.SCHEDULE = round_robin(teams)
        self.BRACKET = None
        self.tWinner = None
        self.prequal = []

    def amIDone(self):
        return self.slate > 22
    
    def playNextSlate(self, handle):
        if self.slate < len(self.SCHEDULE):
            for match in self.SCHEDULE[self.slate]:
                Result = gameWrapper(match[0], match[1])
                handle.RESULTS.loc[len(handle.RESULTS)] = [handle.YEAR, f'{self.name}', self.slate + 1] + Result
                self.STANDINGS.loc[Result[0], 'PD'] += Result[1]-Result[2]
                self.STANDINGS.loc[Result[3], 'PD'] += Result[2]-Result[1]
                if Result[1] > Result[2]:
                    self.STANDINGS.loc[Result[0], 'Wins'] += 1
                    if Result[4]:
                        self.STANDINGS.loc[Result[0], 'EEWins'] += 1
                    self.STANDINGS.loc[Result[3], 'Losses'] += 1
                else:
                    self.STANDINGS.loc[Result[3], 'Wins'] += 1
                    if Result[4]:
                        self.STANDINGS.loc[Result[3], 'EEWins'] += 1
                    self.STANDINGS.loc[Result[0], 'Losses'] += 1
            self.STANDINGS = self.STANDINGS.sort_values(['Wins', 'EEWins', 'PD'], ascending=[False, True, False])
            if self.slate == len(self.SCHEDULE)-1:
                handle.WINNERS.loc[len(handle.WINNERS)] = [handle.YEAR, f'{self.name}', self.STANDINGS.index[0]]
        else:
            print('Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate < len(self.SCHEDULE):
            print(self.name)
            for match in self.SCHEDULE[self.slate]:
                print(f'{match[0]} ({self.STANDINGS.loc[match[0], "Wins"]}-{self.STANDINGS.loc[match[0], "Losses"]}) vs. {match[1]} ({self.STANDINGS.loc[match[1], "Wins"]}-{self.STANDINGS.loc[match[1], "Losses"]})')
        else:
            print('Over')
    
    def getFinishers(self, start = 1, end = 1):
        return list(self.STANDINGS.index[(start-1):end])

