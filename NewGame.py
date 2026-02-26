from Shot import *

def End(SHEET, screen, joystick):
    while SHEET.shotsleft > 0:
        ShotTeam, ShotPos, Shooter, SweeperScore = getShooter(SHEET)
        if Shooter.controlled:
            start_x, init_yv, spin = getShotSpecs_USER(screen, joystick, SHEET, ShotTeam, ShotPos, Shooter, SweeperScore)
        else:
            TargetX, TargetY, Type, NeedSpin, TargetID = getShotSpecs(SHEET, ShotTeam, Shooter)
            start_x, init_yv, spin = getCPUSpin(SHEET, Shooter, NeedSpin, TargetX, TargetY, Type, TargetID)
        #print(TargetX, Type, Spin)
        Shot(SHEET, screen, ShotTeam, SweeperScore, ShotPos, Shooter, start_x, init_yv, spin)
        pygame.time.delay(1000)

def game_HiRes(Home, Away):
    screen, joystick = startPygame('AAA')
    SHEET = Sheet(Home, Away)
    while SHEET.end < SHEET.numends:
        End(SHEET, screen, joystick)
        _ = SHEET.reset()
    if sum(trim_all_none(SHEET.HomeScore)) != sum(trim_all_none(SHEET.AwayScore)):
        return [Home, sum(trim_all_none(SHEET.HomeScore)), sum(trim_all_none(SHEET.AwayScore)), Away, False]
    else:
        rezzy = None
        while rezzy is None:
            End(SHEET, screen, joystick)
            rezzy = SHEET.reset(EE = True)
        return [Home, rezzy[0], rezzy[1], Away, True]
    

def game_LoRes(Home, Away):
    HomeRating = Home.getRating()
    AwayRating = Away.getRating()
    diff = .21*(HomeRating - AwayRating)
    spread = math.floor(np.random.normal(diff, 3))
    loserScore = round(12*np.random.beta(9, 4))
    if spread < 0:
        return [Home, loserScore, loserScore-spread, Away, False]
    elif spread > 0:
        return [Home, loserScore+spread, loserScore, Away, False]
    else:
        return [Home, loserScore+1, loserScore, Away, True]
    