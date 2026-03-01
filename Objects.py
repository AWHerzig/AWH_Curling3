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
    def __init__(self, name, country, value = None, controlled = False):
        self.name = name if name is not None else names.get_full_name()
        self.age = 1
        self.controlled = controlled
        self.country = country
        self.risk = random.randint(1, 100)
        # self.attributes
        if self.controlled:
            screen, joystick = startPygame('PLAYER BUILDING')
            selections = {
                'Y-ACC': 0, 'X-ACC': 0, 'SWEEP':0, 'C-ACC':0, '2-WAY': 0
            }
            startingbudget = 100
            finalized = False
            curind = 0
            DEADZONE = 0.2
            AXIS_SENS = 0.4       # movement sensitivity
            cooldown = 0
            while not finalized:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.display.quit()
                        return None
                    # A button confirms
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 0:  # A button
                            finalized = True
                left_x = joystick.get_axis(0)
                if abs(left_x) > DEADZONE and cooldown <= 0:
                    if curind == 4:
                        selections[list(selections.keys())[curind]] = 32 if left_x > 0 and 100 - sum(list(selections.values())) >= 32 else 0
                        cooldown = 50
                    else:
                        selections[list(selections.keys())[curind]] += round(left_x) if (left_x > 0 and sum(list(selections.values())) < startingbudget) or (left_x < 0 and selections[list(selections.keys())[curind]] > 0) else 0
                        cooldown = 10

                
                left_y = joystick.get_axis(1)
                if abs(left_y) > DEADZONE and cooldown <= 0:
                    curind = round(curind + 1*(left_y/abs(left_y))) % 5
                    cooldown = 50
                cooldown -= 1
                screen.fill(black)
                text(f'{self.name} INITIAL STATS', (screenWidth*.5, screenHeight*.1), 48, screen)
                text(f'REMAINING BUDGET: {startingbudget - sum(list(selections.values()))}', (screenWidth*.5, screenHeight*.2), 48, screen)
                for i in range(5):
                    text(f'{list(selections.keys())[i]}: {list(selections.values())[i]}', (screenWidth*.25, screenHeight*(.3+.1*i)), 48, screen, blue if curind == i else white, spot='midleft')
                pygame.display.update()
            self.yacc = selections['Y-ACC']
            self.xacc = selections['X-ACC']
            self.curl = selections['C-ACC']
            self.twowaycurl = selections['2-WAY'] > 0
            self.sweep = selections['SWEEP']
        else:
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
        if self.controlled:
            screen, joystick = startPygame('PLAYER UPGRADES')
            selections = {
                'Y-ACC': self.yacc, 'X-ACC': self.xacc, 'SWEEP':self.sweep, 'C-ACC':self.curl, '2-WAY': 32*self.twowaycurl
            }
            startingbudget = round(332*((3*(self.age-1))**-1)+ sum(list(selections.values())))
            finalized = False
            curind = 0
            DEADZONE = 0.2
            AXIS_SENS = 0.4       # movement sensitivity
            cooldown = 0
            while not finalized:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.display.quit()
                        return None
                    # A button confirms
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 0:  # A button
                            finalized = True
                left_x = joystick.get_axis(0)
                if abs(left_x) > DEADZONE and cooldown <= 0:
                    if curind == 4:
                        selections[list(selections.keys())[curind]] = 32 if left_x > 0 and (startingbudget - sum(list(selections.values())) >= 32 or selections[list(selections.keys())[curind]]) == 32 else 0
                        cooldown = 50
                    else:
                        selections[list(selections.keys())[curind]] += round(left_x) if (left_x > 0 and sum(list(selections.values())) < startingbudget and selections[list(selections.keys())[curind]] < 0) or (left_x < 0 and selections[list(selections.keys())[curind]] > 0) else 0
                        cooldown = 10

                
                left_y = joystick.get_axis(1)
                if abs(left_y) > DEADZONE and cooldown <= 0:
                    curind = round(curind + 1*(left_y/abs(left_y))) % 5
                    cooldown = 50
                cooldown -= 1
                screen.fill(black)
                text(f'{self.name} UPGRADE STATS', (screenWidth*.5, screenHeight*.1), 48, screen)
                text(f'REMAINING BUDGET: {startingbudget - sum(list(selections.values()))}', (screenWidth*.5, screenHeight*.2), 48, screen)
                for i in range(5):
                    text(f'{list(selections.keys())[i]}: {list(selections.values())[i]}', (screenWidth*.25, screenHeight*(.3+.1*i)), 48, screen, blue if curind == i else white, spot='midleft')
                pygame.display.update()
            self.yacc = selections['Y-ACC']
            self.xacc = selections['X-ACC']
            self.curl = selections['C-ACC']
            self.twowaycurl = selections['2-WAY'] > 0
            self.sweep = selections['SWEEP']
        else:
            if self.age <= 3:
                self.yacc += adjustDraw(15, 30)
                self.xacc += adjustDraw(15, 30)
                self.curl += adjustDraw(15, 30)
                self.sweep += adjustDraw(15, 30)
                if random.uniform(0, 100) < 10:
                    self.twowaycurl = True
            elif self.age <= 5:
                self.yacc += adjustDraw(10, 25)
                self.xacc += adjustDraw(10, 25)
                self.curl += adjustDraw(10, 25)
                self.sweep += adjustDraw(10, 25)
                if random.uniform(0, 100) < 20:
                    self.twowaycurl = True
            elif self.age <= 7:
                self.yacc += adjustDraw(0, 20)
                self.xacc += adjustDraw(0, 20)
                self.curl += adjustDraw(0, 20)
                self.sweep += adjustDraw(0, 20)
                if random.uniform(0, 100) < 40:
                    self.twowaycurl = True
            elif self.age <= 10:
                self.yacc += adjustDraw(-10, 20)
                self.xacc += adjustDraw(-10, 20)
                self.curl += adjustDraw(-10, 20)
                self.sweep += adjustDraw(-10, 20)
                if random.uniform(0, 100) < 80:
                    self.twowaycurl = True
            else:
                self.yacc += adjustDraw(-20, 20)
                self.xacc += adjustDraw(-20, 20)
                self.curl += adjustDraw(-20, 20)
                self.sweep += adjustDraw(-20, 20)
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

    def getRating(self):
        return .25*(self.lead.getRating()+self.second.getRating()+self.third.getRating()+self.skip.getRating())
    
    def anyControlled(self):
        return self.controlled or self.lead.controlled or self.second.controlled or self.third.controlled or self.skip.controlled