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

def Game_HiRes(Home, Away):
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
        return [Home, rezzy[0], rezzy[1], Away]
    