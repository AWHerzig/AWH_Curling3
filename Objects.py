from DirectoryWide import *

class Sheet:
    def __init__(self, home, away, numends = 8):
        self.Home = home
        self.Away = away
        self.numends = numends
        self.end = 0
        self.HomeScore, self.AwayScore = [None]*numends, [None]*numends
        self.hammer = 'Home'
        self.leadteam = 'Away'
        self.shotsleft = 16
        self.df = pd.DataFrame(columns=['x', 'y', 'xv', 'yv', 'curve', 'team'])

    def DoneMoving(self):
        return np.isclose(self.df.xv.sum()+self.df.yv.sum(), 0)
    
    def getScoring(self):
        DISTS = self.df[['x', 'y', 'team']].copy()
        DISTS['Distance'] = [distanceFormula(0, BUTTON[1], DISTS.loc[i, 'x'], DISTS.loc[i, 'y']) for i in DISTS.index]
        DISTS = DISTS[DISTS.Distance < 16]
        if len(DISTS) == 0:
            return 'BLANK', 0
        if len(DISTS.team.unique()) == 1:
            return DISTS.team.iloc[0], len(DISTS)
        else:
            DISTS = DISTS.sort_values('Distance')
            DISTS['Rank'] = [i+1 for i in range(len(DISTS))]
            DISTS = DISTS.groupby('team').min().sort_values('Rank')
            return DISTS.index[0], max(DISTS.Rank)-1
    
    def reset(self, EE = False):
        ScoreTeam, Score = self.getScoring()
        if not EE:
            if ScoreTeam == 'BLANK':
                self.HomeScore[self.end] = 0
                self.AwayScore[self.end] = 0
            elif ScoreTeam == 'Home':
                self.HomeScore[self.end] = Score
                self.AwayScore[self.end] = 0
                self.hammer = 'Away'
                self.leadteam = 'Home'
            elif ScoreTeam == 'Away':
                self.HomeScore[self.end] = 0
                self.AwayScore[self.end] = Score
                self.hammer = 'Home'
                self.leadteam = 'Away'
            else:
                ValueError('BAD SCORETEAM')
            self.shotsleft = 16
            self.df = pd.DataFrame(columns=['x', 'y', 'xv', 'yv', 'curve', 'team'])
            self.end += 1
            return None
        else:
            if Score == 0:
                return None
            elif ScoreTeam == 'Home':
                return sum(trim_all_none(self.HomeScore))+Score, sum(trim_all_none(self.AwayScore))
            elif ScoreTeam == 'Away':
                return sum(trim_all_none(self.HomeScore)), sum(trim_all_none(self.AwayScore))+Score




    def getLead(self, team):
        if team == 'Home':
            return sum(trim_all_none(self.HomeScore)) - sum(trim_all_none(self.AwayScore))
        else:
            return sum(trim_all_none(self.AwayScore)) - sum(trim_all_none(self.HomeScore))

class Player:
    def __init__(self, name, country, value = None):
        self.name = name if name is not None else names.get_full_name()
        self.age = 1
        self.controlled = False
        self.country = country
        self.risk = random.randint(1, 100)
        # self.attributes
        self.yacc = adjustDraw(20, 30)
        self.xacc = adjustDraw(20, 30)
        self.curl = adjustDraw(20, 30)
        self.twowaycurl = np.random.choice([True, False], p=[.1, .9])
        self.sweep = adjustDraw(20, 30)
        # Values
        self.values = {
            'Contract': .4,
            'League Prestige': .2,
            'Team Prestige': .1,
            'Home Nation': .1,
            'Consistent Location': .1
        }
        if value is None:
            value = random.choice(list(self.values.keys()))
        self.values[value] += .1
        
    def getRating(self):
        return .23*(self.yacc+self.xacc+self.curl+self.sweep) + .08*self.twowaycurl

    def __str__(self):
        return self.name
    
    def ageup(self):
        self.age += 1
        if self.age <= 3:
            self.yacc += adjustDraw(15, 20)
            self.xacc += adjustDraw(15, 20)
            self.curl += adjustDraw(15, 20)
            self.sweep += adjustDraw(15, 20)
            if random.uniform(0, 100) < 10:
                self.twowaycurl = True
        elif self.age <= 5:
            self.yacc += adjustDraw(10, 15)
            self.xacc += adjustDraw(10, 15)
            self.curl += adjustDraw(10, 15)
            self.sweep += adjustDraw(10, 15)
            if random.uniform(0, 100) < 20:
                self.twowaycurl = True
        elif self.age <= 7:
            self.yacc += adjustDraw(0, 15)
            self.xacc += adjustDraw(0, 15)
            self.curl += adjustDraw(0, 15)
            self.sweep += adjustDraw(0, 15)
            if random.uniform(0, 100) < 40:
                self.twowaycurl = True
        elif self.age <= 10:
            self.yacc += adjustDraw(-10, 15)
            self.xacc += adjustDraw(-10, 15)
            self.curl += adjustDraw(-10, 15)
            self.sweep += adjustDraw(-10, 15)
            if random.uniform(0, 100) < 80:
                self.twowaycurl = True
        else:
            self.yacc += adjustDraw(-20, 15)
            self.xacc += adjustDraw(-20, 15)
            self.curl += adjustDraw(-20, 15)
            self.sweep += adjustDraw(-20, 15)
            if random.uniform(0, 100) < 105:
                self.twowaycurl = True
        self.yacc = clamp(self.yacc, 0, 100)
        self.xacc = clamp(self.xacc, 0, 100)
        self.curl = clamp(self.curl, 0, 100)
        self.sweep = clamp(self.sweep, 0, 100)

class Team:
    def __init__(self, name, ABR):
        self.name = name
        self.ABR = ABR
        self.controlled = False
        # Players
        self.lead = None
        self.second = None
        self.third = None
        self.skip = None

    def __str__(self):
        return self.name

    def setRoster(self, InputPlayers):
        x = pd.DataFrame(index = InputPlayers)
        x['ShooterRating'] = [.33*(plyr.yacc+plyr.xacc+plyr.curl)+5*plyr.twowaycurl for plyr in x.index]
        x['sweep'] = [plyr.sweep for plyr in x.index]
        x['DIFF'] = x.ShooterRating - x.sweep
        x['Composite'] = x.DIFF+.5*x.ShooterRating
        x.sort_values('Composite', inplace = True)
        x['Help'] = [0, 0, 1, 2]
        x.sort_values(['Help', 'ShooterRating'], inplace=True)
        self.lead = x.index[0]
        self.second = x.index[1]
        self.third = x.index[2]
        self.skip = x.index[3]
