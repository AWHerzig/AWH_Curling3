from Formats import *
import pickle

class CL_Europe:
    def __init__(self, handle):
        self.AutoSwiss = []
        self.Qualifiers = []
        self.handle = handle
        self.slate = 1
        self.winner = None
        self.QualfyingTs = None
        self.Swiss = None
        self.Playoffs = None
        TIERA = list(COUNTRYDF[(COUNTRYDF.Region == 'Europe') & (COUNTRYDF.TIER == 'TIERA')].index)
        TIERB = list(COUNTRYDF[(COUNTRYDF.Region == 'Europe') & (COUNTRYDF.TIER == 'TIERB')].index)
        TIERC = list(COUNTRYDF[(COUNTRYDF.Region == 'Europe') & (COUNTRYDF.TIER == 'TIERC')].index)
        TIERD = list(COUNTRYDF[(COUNTRYDF.Region == 'Europe') & (COUNTRYDF.TIER == 'TIERD')].index)
        TIERE = list(COUNTRYDF[(COUNTRYDF.Region == 'Europe') & (COUNTRYDF.TIER == 'TIERE')].index)
        random.shuffle(TIERD) # Needed cuz one will get bye
        for cnty in TIERA:
            self.AutoSwiss.append(self.handle.LEAGUES[cnty].tWinner)
            self.AutoSwiss.append(self.handle.LEAGUES[cnty].popqual())
            self.AutoSwiss.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERB:
            self.AutoSwiss.append(self.handle.LEAGUES[cnty].tWinner)
            self.AutoSwiss.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERC:
            self.AutoSwiss.append(self.handle.LEAGUES[cnty].tWinner)
        for cnty in TIERD+TIERE:
            self.Qualifiers.append(self.handle.LEAGUES[cnty].tWinner)
        for cnty in TIERA+TIERC+TIERD:
            self.Qualifiers.append(self.handle.LEAGUES[cnty].popqual())
        self.Qualifiers.append(None)
        self.QualifyingTs = [Bracket(f'Europe CL Quals Path {num+1}', [self.Qualifiers[num], self.Qualifiers[13-num], self.Qualifiers[14+num], self.Qualifiers[27-num]]) for num in range(7)]

    def playNextSlate(self):
        if self.slate <= 2:
            for brkt in self.QualifyingTs:
                brkt.playNextSlate(self.handle)
            if self.slate == 2:
                self.Swiss = Swiss('Europe CL Swiss', self.AutoSwiss+[brkt.winner for brkt in self.QualifyingTs])
        elif self.slate <= 7:
            self.Swiss.playNextSlate(self.handle)
            if self.slate == 7:
                advanced = self.Swiss.getAdvanced()
                random.shuffle(advanced)
                self.Playoffs = Bracket('Europe CL Knockouts', advanced)
        elif self.slate <= 11:
            self.Playoffs.playNextSlate(self.handle)
            if self.slate == 11:
                self.winner = self.Playoffs.winner
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 2:
            for brkt in self.QualifyingTs:
                brkt.displayNextSlate()
        elif self.slate <= 7:
            self.Swiss.displayNextSlate()
        elif self.slate <= 11:
            self.Playoffs.displayNextSlate()
        else:
            print('Season Over')

    def teamIn(self, tm):
        return tm in self.AutoSwiss+self.Qualifiers
    
class CL_Asia:
    def __init__(self, handle):
        self.handle = handle
        self.AutoDE = []
        self.Qualifiers = []
        self.slate = 1
        self.winner = None
        self.QualfyingTs = None
        self.DE = None
        TIERA = list(COUNTRYDF[(COUNTRYDF.Region == 'Asia') & (COUNTRYDF.TIER == 'TIERA')].index)
        TIERB = list(COUNTRYDF[(COUNTRYDF.Region == 'Asia') & (COUNTRYDF.TIER == 'TIERB')].index)
        TIERC = list(COUNTRYDF[(COUNTRYDF.Region == 'Asia') & (COUNTRYDF.TIER == 'TIERC')].index)
        TIERD = list(COUNTRYDF[(COUNTRYDF.Region == 'Asia') & (COUNTRYDF.TIER == 'TIERD')].index)
        TIERE = list(COUNTRYDF[(COUNTRYDF.Region == 'Asia') & (COUNTRYDF.TIER == 'TIERE')].index)
        for cnty in TIERA+TIERB+TIERC+TIERD+TIERE:
            self.AutoDE.append(self.handle.LEAGUES[cnty].tWinner)
        for cnty in TIERA+TIERB+TIERC:
            self.AutoDE.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERA+TIERB+TIERD:
            self.Qualifiers.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERA:
            self.Qualifiers.append(self.handle.LEAGUES[cnty].popqual())
        self.QualifyingTs = [Bracket(f'Asia CL Quals Path {num+1}', [self.Qualifiers[num], self.Qualifiers[15-num]]) for num in range(8)]

    def playNextSlate(self):
        if self.slate <= 1:
            for brkt in self.QualifyingTs:
                brkt.playNextSlate(self.handle)
            if self.slate == 1:
                self.DE = DubElim32('Asia CL', self.AutoDE+[brkt.winner for brkt in self.QualifyingTs])
        elif self.slate <= 11:
            self.DE.playNextSlate(self.handle)
            if self.slate == 11:
                self.winner = self.DE.winner
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 1:
            for brkt in self.QualifyingTs:
                brkt.displayNextSlate()
        elif self.slate <= 11:
            self.DE.displayNextSlate()
        else:
            print('Season Over')

    def teamIn(self, tm):
        return tm in self.AutoDE+self.Qualifiers

class CL_Americas:
    def __init__(self, handle):
        self.handle = handle
        self.ToStage2 = []
        self.ToStage1 = []
        self.slate = 1
        self.winner = None
        self.Stage1s = None
        self.Stage2s = None
        self.Stage3s = None
        self.Finals = None
        TIERA = list(COUNTRYDF[(COUNTRYDF.Region == 'Americas') & (COUNTRYDF.TIER == 'TIERA')].index)
        TIERB = list(COUNTRYDF[(COUNTRYDF.Region == 'Americas') & (COUNTRYDF.TIER == 'TIERB')].index)
        TIERC = list(COUNTRYDF[(COUNTRYDF.Region == 'Americas') & (COUNTRYDF.TIER == 'TIERC')].index)
        TIERD = list(COUNTRYDF[(COUNTRYDF.Region == 'Americas') & (COUNTRYDF.TIER == 'TIERD')].index)
        TIERE = list(COUNTRYDF[(COUNTRYDF.Region == 'Americas') & (COUNTRYDF.TIER == 'TIERE')].index)
        for cnty in TIERA+TIERB+TIERC:
            self.ToStage2.append(self.handle.LEAGUES[cnty].tWinner)
        for cnty in TIERA:
            self.ToStage2.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERD+TIERE:
            self.ToStage1.append(self.handle.LEAGUES[cnty].tWinner)
        for cnty in TIERA+TIERB+TIERC+TIERD:
            self.ToStage1.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERA+TIERB+TIERC:
            self.ToStage1.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERA+TIERB:
            self.ToStage1.append(self.handle.LEAGUES[cnty].popqual())
        random.shuffle(self.ToStage1)
        self.Stage1s = [MiniSwiss(f'Americas CL Stage 1 Path {num//4+1}', self.ToStage1[num:(num+4)]) for num in range(0, 20, 4)]

    def playNextSlate(self):
        if self.slate <= 3:
            for brkt in self.Stage1s:
                brkt.playNextSlate(self.handle)
            if self.slate == 3:
                s2t = self.ToStage2
                for brkt in self.Stage1s:
                    s2t = s2t + brkt.getAdvanced()
                random.shuffle(s2t)
                self.Stage2s = [MiniSwiss(f'Americas CL Stage 2 Path {num//4+1}', s2t[num:(num+4)]) for num in range(0, 16, 4)]
        elif self.slate <= 6:
            for brkt in self.Stage2s:
                brkt.playNextSlate(self.handle)
            if self.slate == 6:
                s3t = []
                for brkt in self.Stage2s:
                    s3t = s3t + brkt.getAdvanced()
                random.shuffle(s3t)
                self.Stage3s = [MiniSwiss(f'Americas CL Stage 3 Path {num//4+1}', s3t[num:(num+4)]) for num in range(0, 8, 4)]
        elif self.slate <= 9:
            for brkt in self.Stage3s:
                brkt.playNextSlate(self.handle)
            if self.slate == 9:
                pt = []
                for brkt in self.Stage3s:
                    pt = pt + brkt.getAdvanced()
                random.shuffle(pt)
                self.Finals = Bracket(f'Americas CL Finals', pt)
        elif self.slate <= 11:
            self.Finals.playNextSlate(self.handle)
            if self.slate == 11:
                self.winner = self.Finals.winner
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 3:
            for brkt in self.Stage1s:
                brkt.displayNextSlate()
        elif self.slate <= 6:
            for brkt in self.Stage2s:
                brkt.displayNextSlate()
        elif self.slate <= 9:
            for brkt in self.Stage3s:
                brkt.displayNextSlate()
        elif self.slate <= 11:
            self.Finals.displayNextSlate()
        else:
            print('Season Over')

    def teamIn(self, tm):
        return tm in self.ToStage1+self.ToStage2

class CL_MEA:
    def __init__(self, handle):
        self.handle = handle
        self.GroupStage = []
        self.slate = 1
        self.winner = None
        self.Finals = None
        # They dont have A or B
        TIERC = list(COUNTRYDF[(COUNTRYDF.Region == 'MEA') & (COUNTRYDF.TIER == 'TIERC')].index)
        TIERD = list(COUNTRYDF[(COUNTRYDF.Region == 'MEA') & (COUNTRYDF.TIER == 'TIERD')].index)
        TIERE = list(COUNTRYDF[(COUNTRYDF.Region == 'MEA') & (COUNTRYDF.TIER == 'TIERE')].index)
        for cnty in TIERC+TIERD+TIERE:
            self.GroupStage.append(self.handle.LEAGUES[cnty].tWinner)
        for cnty in TIERC+TIERD+TIERE:
            self.GroupStage.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERC+TIERD:
            self.GroupStage.append(self.handle.LEAGUES[cnty].popqual())
        for cnty in TIERC:
            self.GroupStage.append(self.handle.LEAGUES[cnty].popqual())
        random.shuffle(self.GroupStage)
        self.Groups = [GROUP(f'MEA CL GROUP {num//10+1}', self.GroupStage[num:(num+10)]) for num in range(0, 40, 10)]

    def playNextSlate(self):
        if self.slate <= 9:
            for grp in self.Groups:
                grp.playNextSlate(self.handle)
            if self.slate == 9:
                finalsteams = [grp.getFinishers(1, 1)[0] for grp in self.Groups]
                random.shuffle(finalsteams)
                self.Finals = Bracket('MEA CL Finals', finalsteams)
        elif self.slate <= 11:
            self.Finals.playNextSlate(self.handle)
            if self.slate == 11:
                self.winner = self.Finals.winner
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 9:
            for grp in self.Groups:
                grp.displayNextSlate()
        elif self.slate <= 11:
            self.Finals.displayNextSlate()
        else:
            print('Season Over')

    def teamIn(self, tm):
        return tm in self.GroupStage


class WCQ_Americas:
    def __init__(self, handle):
        self.handle = handle
        self.slate = 1
        self.quals = []
        teams = list(COUNTRYDF[(COUNTRYDF.Region == 'Americas')].TEAM)
        random.shuffle(teams)
        self.RR = GROUP('WCQ Americas', teams)
        self.Playoffs = None

    def playNextSlate(self):
        if self.slate <= 9:
            self.RR.playNextSlate(self.handle)
            if self.slate == 9:
                self.Playoffs = Bracket('WCQ Americas Playoffs', self.RR.getFinishers(3, 5))
        elif self.slate <= 11:
            self.Playoffs.playNextSlate(self.handle)
            if self.slate == 11:
                self.quals = self.RR.getFinishers(1, 2)+[self.Playoffs.winner]
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 9:
            self.RR.displayNextSlate()
        elif self.slate <= 11:
            self.Playoffs.displayNextSlate()
        else:
            print('Season Over')

    def getQualified(self):
        if self.slate < 11:
            return 'Not Done Yet'
        return self.quals

class WCQ_MEA:
    def __init__(self, handle):
        self.handle = handle
        self.slate = 1
        self.winner = None
        teams = list(COUNTRYDF[(COUNTRYDF.Region == 'MEA')].TEAM)
        random.shuffle(teams)
        self.R1Groups = [GROUP(f'WCQ MEA STAGE 1 GROUP {num//5+1}', teams[num:(num+5)]) for num in range(0, 15, 5)]
        self.R2Group = None
        self.Final = None

    def playNextSlate(self):
        if self.slate <= 5:
            for grp in self.R1Groups:
                grp.playNextSlate(self.handle)
            if self.slate == 5:
                quals = []
                for grp in self.R1Groups:
                    quals = quals + grp.getFinishers(1, 2)
                self.R2Group = GROUP('WCQ MEA STAGE 2', quals)
        elif self.slate <= 10:
            self.R2Group.playNextSlate(self.handle)
            if self.slate == 10:
                self.Final = Bracket('WCQ MEA FINAL', self.R2Group.getFinishers(1, 2))
        elif self.slate <= 11:
            self.Final.playNextSlate(self.handle)
            if self.slate == 11:
                self.winner = self.Final.winner
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 5:
            for grp in self.R1Groups:
                grp.displayNextSlate()
        elif self.slate <= 10:
            self.R2Group.displayNextSlate()
        elif self.slate <= 11:
            self.Final.displayNextSlate()
        else:
            print('Season Over')

    def getQualified(self):
        if self.slate < 11:
            return 'Not Done Yet'
        return [self.winner]
    
class WCQ_Europe:
    def __init__(self, handle):
        self.handle = handle
        self.slate = 1
        self.quals = []
        teams = list(COUNTRYDF[(COUNTRYDF.Region == 'Europe')].TEAM)
        random.shuffle(teams)
        self.R1Groups = [GROUP(f'WCQ Europe STAGE 1 GROUP {num//6+1}', teams[num:(num+6)]) for num in range(0, 24, 6)]
        self.R2Groups = None
        self.Playin = None

    def playNextSlate(self):
        if self.slate <= 5:
            for grp in self.R1Groups:
                grp.playNextSlate(self.handle)
            if self.slate == 5:
                quals = []
                for grp in self.R1Groups:
                    quals = quals + grp.getFinishers(1, 3)
                random.shuffle(quals)
                self.R2Groups = [GROUP(f'WCQ Europe STAGE 2 GROUP {num//6+1}', quals[num:(num+6)]) for num in range(0, 12, 6)]
        elif self.slate <= 10:
            for grp in self.R2Groups:
                grp.playNextSlate(self.handle)
            if self.slate == 10:
                self.quals = self.R2Groups[0].getFinishers(1, 3) + self.R2Groups[1].getFinishers(1, 3)
                self.Playin = Bracket('WCQ Europe PLAY-IN', [self.R2Groups[0].getFinishers(4, 4)[0], self.R2Groups[1].getFinishers(4, 4)[0]])
        elif self.slate <= 11:
            self.Playin.playNextSlate(self.handle)
            if self.slate == 11:
                self.quals = self.quals+[self.Playin.winner]
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 5:
            for grp in self.R1Groups:
                grp.displayNextSlate()
        elif self.slate <= 10:
            for grp in self.R2Groups:
                grp.displayNextSlate()
        elif self.slate <= 11:
            self.Playin.displayNextSlate()
        else:
            print('Season Over')

    def getQualified(self):
        if self.slate < 11:
            return 'Not Done Yet'
        return self.quals

class WCQ_Asia:
    def __init__(self, handle):
        self.handle = handle
        self.slate = 1
        self.quals = []
        teams = list(COUNTRYDF[(COUNTRYDF.Region == 'Asia')].TEAM)
        self.Round1 = MiniSwiss(f'WCQ Asia Stage 1', teams)
        self.Round2 = None
        self.Playin = None

    def playNextSlate(self):
        if self.slate <= 3:
            self.Round1.playNextSlate(self.handle)
            if self.slate == 3:
                self.Round2 = GROUP(f'WCQ Asia STAGE 2', self.Round1.getAdvanced())
        elif self.slate <= 10:
            self.Round2.playNextSlate(self.handle)
            if self.slate == 10:
                self.quals = self.Round2.getFinishers(1, 4)
                self.Playin = Bracket('WCQ Asia PLAY-IN', self.Round2.getFinishers(5, 6))
        elif self.slate <= 11:
            self.Playin.playNextSlate(self.handle)
            if self.slate == 11:
                self.quals = self.quals+[self.Playin.winner]
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 3:
            self.Round1.displayNextSlate()
        elif self.slate <= 10:
            self.Round2.displayNextSlate()
        elif self.slate <= 11:
            self.Playin.displayNextSlate()
        else:
            print('Season Over')

    def getQualified(self):
        if self.slate < 11:
            return 'Not Done Yet'
        return self.quals
    

class CWC:
    def __init__(self, handle):
        self.handle = handle
        self.GROUP = GROUP('CWC GROUP STAGE', [cl.winner for cl in handle.CL.values()])
        self.FINAL = None
        self.slate = 1
        self.winner = None

    def playNextSlate(self):
        if self.slate <= 3:
            self.GROUP.playNextSlate(self.handle)
            if self.slate == 3:
                self.FINAL = Bracket('CWC FINAL', self.GROUP.getFinishers(1, 2))
        elif self.slate <= 4:
            self.FINAL.playNextSlate(self.handle)
            if self.slate == 4:
                self.winner = self.FINAL.winner
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 3:
            self.GROUP.displayNextSlate()
        elif self.slate <= 4:
            self.FINAL.displayNextSlate()
        else:
            print('Season Over')

class WorldCup:
    def __init__(self, handle):
        self.handle = handle
        self.SWISS = Swiss('WORLD CUP GROUP STAGE', self.handle.WCQ['Europe'].getQualified()+self.handle.WCQ['Asia'].getQualified()+self.handle.WCQ['Americas'].getQualified()+self.handle.WCQ['MEA'].getQualified())
        self.FINALS = None
        self.slate = 1
        self.winner = None

    def playNextSlate(self):
        if self.slate <= 5:
            self.SWISS.playNextSlate(self.handle)
            if self.slate == 5:
                self.FINALS = Bracket('WORLD CUP KNOCKOUTS', self.SWISS.getAdvanced())
        elif self.slate <= 8:
            self.FINALS.playNextSlate(self.handle)
            if self.slate == 8:
                self.winner = self.FINALS.winner
        else:
            print('Season Over')
        self.slate += 1

    def displayNextSlate(self):
        if self.slate <= 5:
            self.SWISS.displayNextSlate()
        elif self.slate <= 8:
            self.FINALS.displayNextSlate()
        else:
            print('Season Over')

class HANDLER:
    def __init__(self):
        self.YEAR = 1
        self.slate = 1
        self.RESULTS = pd.DataFrame(columns = ['YEAR', 'COMPETITION', 'STAGE', 'Home', 'HomeScore', 'AwayScore', 'Away', 'ExtraEnd'])
        self.WINNERS = pd.DataFrame(columns = ['YEAR', 'COMPETITION', 'WINNER'])
        self.WorldCup = None
        self.CWC = None
        self.WCQ = {
            'Europe': WCQ_Europe(self),
            'Asia': WCQ_Asia(self),
            'Americas': WCQ_Americas(self),
            'MEA': WCQ_MEA(self)
        }
        self.LEAGUES = {cnty: LEAGUE(cnty, TEAMSDF[TEAMSDF.Country == cnty].index) for cnty in COUNTRYDF.index}
        for _ in range(23):
            for cnty in self.LEAGUES.keys():
                self.LEAGUES[cnty].playNextSlate(self)
        self.CL = {
            'Europe': CL_Europe(self),
            'Asia': CL_Asia(self),
            'Americas': CL_Americas(self),
            'MEA': CL_MEA(self)
        }
        self.LEAGUES = {cnty: LEAGUE(cnty, TEAMSDF[TEAMSDF.Country == cnty].index) for cnty in COUNTRYDF.index}
        self.RESULTS = pd.DataFrame(columns = ['YEAR', 'COMPETITION', 'STAGE', 'Home', 'HomeScore', 'AwayScore', 'Away', 'ExtraEnd'])
        self.WINNERS = pd.DataFrame(columns = ['YEAR', 'COMPETITION', 'WINNER'])

    def displayNextSlate(self):
        if self.slate < 46 and self.slate % 2 == 1:
            for cnty in self.LEAGUES.keys():
                self.LEAGUES[cnty].displayNextSlate()
        elif self.slate < 46 and self.slate % 4 == 0:
            for cnty in self.CL.keys():
                self.CL[cnty].displayNextSlate()
        elif self.slate < 46 and self.slate % 4 == 2:
            for cnty in self.WCQ.keys():
                self.WCQ[cnty].displayNextSlate()
        elif self.slate < 50:
            self.CWC.displayNextSlate()
        else:
            self.WorldCup.displayNextSlate()

    def playNextSlate(self):
        if self.slate < 46 and self.slate % 2 == 1:
            #print('League')
            for cnty in self.LEAGUES.keys():
                self.LEAGUES[cnty].playNextSlate(self)
        elif self.slate < 46 and self.slate % 4 == 0:
            #print('CL')
            for cnty in self.CL.keys():
                self.CL[cnty].playNextSlate()
        elif self.slate < 46 and self.slate % 4 == 2:
            #print('WCQ')
            for cnty in self.WCQ.keys():
                self.WCQ[cnty].playNextSlate()
        elif self.slate < 50:
            #print('CWC')
            self.CWC.playNextSlate()
        else:
            #print('WC')
            self.WorldCup.playNextSlate()
        if self.slate == 44:
            self.CWC = CWC(self)
            self.WorldCup = WorldCup(self)
        self.slate += 1

    def reset(self, rosterdf):
        self.YEAR += 1
        self.slate = 1
        self.WorldCup = None
        self.CWC = None
        self.WCQ = {
            'Europe': WCQ_Europe(self),
            'Asia': WCQ_Asia(self),
            'Americas': WCQ_Americas(self),
            'MEA': WCQ_MEA(self)
        }
        self.CL = {
            'Europe': CL_Europe(self),
            'Asia': CL_Asia(self),
            'Americas': CL_Americas(self),
            'MEA': CL_MEA(self)
        }
        self.LEAGUES = {cnty: LEAGUE(cnty, TEAMSDF[TEAMSDF.Country == cnty].index) for cnty in COUNTRYDF.index}
        rosterdf = Offseason(rosterdf, self, numloops=1)
        return rosterdf

PickleFile = 'REAL2_8Mar26_3'
if PickleFile is not None:
    with open(f'Pickles/{PickleFile}.pkl', 'rb') as f:
        data = pickle.load(f)
        ALLROSTERED, GLOBALHANDLER = data['Roster'], data['handle']
        ALLROSTERED['TMNAME'] = [tm.name for tm in ALLROSTERED.Team]
        for ind in range(len(TEAMSDF)):
            TM, CNT = TEAMSDF.index[ind], TEAMSDF.Country.iloc[ind]
            plyrs = ALLROSTERED.loc[(ALLROSTERED.TMNAME == TM.name) & (ALLROSTERED.League == CNT)].index
            ALLROSTERED.loc[plyrs, 'Team'] = TM
            TM.setRoster(plyrs)
        for cnty in COUNTRYDF.index:
            COUNTRYDF.loc[cnty, 'TEAM'].setRoster(ALLROSTERED[ALLROSTERED.Country == cnty].sort_values('Rating', ascending = False).index[:4])
        ALLROSTERED.drop('TMNAME', inplace = True, axis = 1)
else:
    ALLROSTERED = Offseason(ALLROSTERED, numloops=20)
    GLOBALHANDLER = HANDLER()
    ALLROSTERED = Offseason(ALLROSTERED, GLOBALHANDLER, 1, ['Aidan Herzig',  'United States', 'Team Prestige'])