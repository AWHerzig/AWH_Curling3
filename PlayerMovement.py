from NewGame import *

BASECSV = pd.read_csv('teamsToUse.csv')
TotalSpots = 4*20*64
FreshmanClassProp = .25*.5
OriginProps = [.3, .225, .3, .125, .05]
OriginAbsolutes = dict(zip(['TIERA', 'TIERB', 'TIERC', 'TIERD', 'TIERE'], 
                           [TotalSpots*FreshmanClassProp*prop/8 for prop in OriginProps[:2]]+[TotalSpots*FreshmanClassProp*prop/16 for prop in OriginProps[2:]]))
OriginAbsolutes = {'TIERA': 35.0, 'TIERB': 15.0, 'TIERC': 6.0, 'TIERD': 2.0, 'TIERE': 1.0}
COUNTRYDF = BASECSV.groupby(['Country', 'CountryABR', 'TIER', 'Region']).agg(X = ('Team', 'count')).reset_index().set_index('Country')
COUNTRYDF['TEAM'] = [Team(COUNTRYDF.loc[cnty].name, COUNTRYDF.loc[cnty].CountryABR) for cnty in COUNTRYDF.index]
ALLROSTERED = pd.DataFrame(columns = ['League', 'Team', 'Country', 'Rating', 'Age', 'Years', 'AAV'])
TEAMSDF = pd.DataFrame(columns = ['Country', 'Region', 'TIER', 'LeaguePrestige', 'TeamPrestige', 'TotalBudget'])
for teamrownum in range(len(BASECSV)):
    build = Team(BASECSV.loc[teamrownum, 'Team'], BASECSV.loc[teamrownum, 'TeamABR'])
    TEAMSDF.loc[build] = [BASECSV.loc[teamrownum, 'Country'], BASECSV.loc[teamrownum, 'Region'], BASECSV.loc[teamrownum, 'TIER'], BASECSV.loc[teamrownum, 'LeaguePrestige'], 50, max(BASECSV.loc[teamrownum, 'Budget'], 1)]
TEAMSDF = TEAMSDF.sort_values(['TotalBudget'], ascending=False)
def Offseason(RosterDF, handle = None, numloops = 1, newUserPlayer = None): # nUP = ['Name', 'Country', 'Value']
    for _ in range(numloops):
        print(_)
        if handle is not None:
            TEAMSDF.TeamPrestige = [100*(handle.CL['Europe'].teamIn(tm) or handle.CL['Asia'].teamIn(tm) or handle.CL['Americas'].teamIn(tm) or handle.CL['MEA'].teamIn(tm)) for tm in TEAMSDF.index]
        for plyr in RosterDF.index:
            plyr.ageup()
            RosterDF.loc[plyr, 'Rating'] = plyr.getRating()
        RosterDF.Age += 1
        RosterDF.Years -= 1
        # Generate Rookies
        ROOKIEDF = pd.DataFrame(columns = ['Rating', 'Age', 'Country', 'League'])
        for country in TEAMSDF.Country.unique():
            NumberToMake = OriginAbsolutes[COUNTRYDF.loc[country, 'TIER']]
            for ______ in range(int(NumberToMake)):
                build = Player(name=None, country=country)
                ROOKIEDF.loc[build] = [build.getRating(), build.age, build.country, build.country]
        if newUserPlayer is not None:
            build = Player(newUserPlayer[0], newUserPlayer[1], newUserPlayer[2], controlled=True)
            ROOKIEDF.loc[build] = [build.getRating(), build.age, build.country, build.country]
        # Get Expiring Contracts
        EXPIREDF = RosterDF[RosterDF.Years==0][['Rating', 'Age', 'Country', 'League']]
        FADF = pd.concat([ROOKIEDF, EXPIREDF]).sort_values(['Rating', 'Age'], ascending=[False, True])
        RosterDF = RosterDF[RosterDF.Years!=0]
        NEEDSDF = TEAMSDF.merge(RosterDF.groupby(['Team'], sort = False).agg(Spent = ('AAV', 'sum'), NR = ('AAV', 'count')), how = 'left', left_index=True, right_index=True).fillna(0)
        NEEDSDF['PlayersNeeded'] = 4 - NEEDSDF.NR
        NEEDSDF['AvailableBudget'] = NEEDSDF.TotalBudget - NEEDSDF.Spent
        NEEDSDF = NEEDSDF[NEEDSDF.PlayersNeeded > 0][['Country', 'LeaguePrestige', 'TeamPrestige', 'PlayersNeeded', 'AvailableBudget']]
        AAAAA = 0
        while (len(NEEDSDF) != 0) and (len(FADF) != 0):
            AAAAA += 1
            CurPlayer = FADF.iloc[0]
            TFCP = NEEDSDF.copy()
            if CurPlayer.name.controlled:
                TFCP['YearsOffer'] = 1
            else:
                TFCP['YearsOffer'] = np.random.choice([2, 3], len(NEEDSDF))
            TFCP['AAVOffer'] = TFCP.AvailableBudget*2/(TFCP.PlayersNeeded+1)
            TFCP['ContractScore'] = TFCP.AAVOffer**2*TFCP.YearsOffer
            TFCP.ContractScore = 100*TFCP.ContractScore/np.max(TFCP.ContractScore)
            TFCP['Score'] = CurPlayer.name.values['Contract']*TFCP.ContractScore + \
                CurPlayer.name.values['League Prestige']*TFCP.LeaguePrestige + \
                CurPlayer.name.values['Team Prestige']*TFCP.TeamPrestige + \
                CurPlayer.name.values['Home Nation']*100*(TFCP.Country == CurPlayer.Country) + \
                CurPlayer.name.values['Consistent Location']*100*(TFCP.Country == CurPlayer.League)
            TFCP = TFCP.sort_values('Score', ascending=False)
            if CurPlayer.name.controlled:
                ToShow = TFCP[['Country', 'LeaguePrestige', 'TeamPrestige', 'YearsOffer', 'AAVOffer', 'Score']].copy()
                ToShow['Home Nation'] = ToShow.Country == CurPlayer.Country
                ToShow['Consistent Location'] = ToShow.Country == CurPlayer.League
                ToShow.to_csv('Output/UserFAOptions')
                confirm = False
                ind = 0
                while not confirm:
                    ind = int(input('INPUT ROW NUMBER OF TEAM YOUD LIKE TO SIGN WITH'))
                    confirm = bool(input(f'You have selected offer from {TFCP.iloc[ind].name}, is this correct? (1-yes, 0-choose again)'))
                Contract = TFCP.iloc[ind]
            else:
                Contract = TFCP.iloc[0]
                #Salary = Contract.AAVOffer #if len(TFCP) == 1 else min(Contract.AAVOffer, TFCP.iloc[1].AAVOffer + .1)
                
            RosterDF.loc[CurPlayer.name] = Contract.Country, Contract.name, CurPlayer.Country, CurPlayer.Rating, CurPlayer.Age, Contract.YearsOffer, Contract.AAVOffer
            FADF.drop(CurPlayer.name, inplace = True)
            NEEDSDF.loc[Contract.name, 'PlayersNeeded'] -= 1
            NEEDSDF.loc[Contract.name, 'AvailableBudget'] -= Contract.AAVOffer
            NEEDSDF = NEEDSDF[NEEDSDF.PlayersNeeded > 0]
    for tm in TEAMSDF.index:
        tm.setRoster(RosterDF[RosterDF.Team == tm].index)
    for cnty in COUNTRYDF.index:
        COUNTRYDF.loc[cnty, 'TEAM'].setRoster(RosterDF[RosterDF.Country == cnty].sort_values('Rating', ascending = False).index[:4])
    return RosterDF.sort_values('Rating', ascending = False)

