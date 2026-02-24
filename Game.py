from Objects import *


def game(home, away, out=None, view = False, ends=4, rocks=4, finish = 1):
    colors = colorchecker(home.prefs, away.prefs, req = 25)
    home.color = colors[0]
    away.color = colors[1]
    if modePick == 'Spectate' and (view or (home.top3rd() and away.top3rd()) or finish == 2 or \
                                    (home.spot() <= 2 and away.spot() <= 2 and home.division == away.division)): # finish 2 is playoffs
        gamepreview(home, away, out, ends, rocks)
        if not view:
            view = 'highlight'
    if home.controlled or away.controlled:  # See the games you play
        view = True
        gamepreview(home, away, out, ends, rocks)
    hammer = home
    lead = away
    gamesheet = Sheet(home, away, ends, rocks)
    for endnum in range(1, ends+1):
        score = end(lead, hammer, gamesheet, out, rocks, endnum, view)
        if score[0] == home:
            gamesheet.board.input(endnum, score[1], 0)
            hammer = away
            lead = home
        elif score[0] == away:
            gamesheet.board.input(endnum, 0, score[1])
            hammer = home
            lead = away
        elif score[0] == BlankTeam:
            gamesheet.board.input(endnum, 0, 0)
            hammer = hammer
            lead = lead
        else:
            raise IndexError('Scoring team was neither a team nor blank')
    while gamesheet.board.home[1] == gamesheet.board.away[1]:
        extra = end(lead, hammer, gamesheet, out, rocks, 'E', view)
        if extra[0] == home:
            gamesheet.board.input('E', extra[1], 0)
        elif extra[0] == away:
            gamesheet.board.input('E', 0, score[1])
        elif extra[0] == BlankTeam:
            pass # Just run it again
        else:
            raise IndexError('Scoring team was neither a team nor blank')
    # End of game handle wins however we handle wins
    home.games.append(gamesheet.board)
    away.games.append(gamesheet.board)
    if finish == 1:
        if gamesheet.board.home[1] > gamesheet.board.away[1]:
            home.wins += 1
            away.loss += 1
            home.PointsFor += gamesheet.board.home[1]
            home.PointsAgainst += gamesheet.board.away[1]
            away.PointsFor += gamesheet.board.away[1]
            away.PointsAgainst += gamesheet.board.home[1]
        else:
            away.wins += 1
            home.loss += 1
            home.PointsFor += gamesheet.board.home[1]
            home.PointsAgainst += gamesheet.board.away[1]
            away.PointsFor += gamesheet.board.away[1]
            away.PointsAgainst += gamesheet.board.home[1]
    elif finish == 2:
        if gamesheet.board.home[1] > gamesheet.board.away[1]:
            home.pwins += 1
        else:
            away.pwins += 1
    return gamesheet



def end(lead, hammer, sheet, out, rocks, num, view):
    sheet.clear(num, hammer)
    for i in range(rocks):
        shot(sheet, lead, out, view, hammer=False)
        shot(sheet, hammer, out, view, hammer=(i+1)==rocks)
    return sheet.scoring()
    
comShots = [
    (0, -5, 0), # Button
    (0, -5, 0), # Button, double odds
    (-.3, -5.3, 0), # Backleft
    (-.33, -4.7, 0), # Frontleft
    (.3, -5.3, 0), # Backright
    (.33, -4.7, 0), # Frontright
    (-.8, -5.3, .03), # Middleback
    (1, -4.8, -.04), # Middle-in
    (0, -4, 0) # Center Guard
]

def shot(sheet, team, out, view, hammer=False):
    newStone = Stone(team)
    sheet.addStone(newStone)
    if team.controlled:  # Will always have view on
        shotselect = False
        xv, yv, curve = 0, 0, 0
        while not shotselect:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    newStone.xv = xv
                    newStone.yv = yv
                    newStone.curve = curve
                    shotselect = True
            keys=pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                curve -= .001
            if keys[pygame.K_RIGHT]:
                curve += .001
            sheet.view(out)
            mouse = pygame.mouse.get_pos()
            pygame.draw.line(out, BlackC, start, linepoint(mouse))
            yv = -.1*clamp(mouse[1] - start[1], 0, 80)
            xv = -.1*clamp(mouse[0] - start[0], -80, 80)  
            pygame.display.update()
    else:
        newStone.xv, newStone.yv, newStone.curve = random.choice(comShots)
    newStone.xv = numpy.random.normal(newStone.xv, abs(.2 - .02*team.Xacc))
    newStone.yv = numpy.random.normal(newStone.yv, abs(.2 - .02*team.Yacc))
    newStone.curve = numpy.random.normal(newStone.curve, abs(.02 - .002*team.Cacc))
    if view == True:
        inmotion(sheet, out)
    elif view == 'highlight' and hammer:
        inmotion(sheet, out)
    else: # should include 'no'
        inmotion_blind(sheet)

def linepoint(mouse):
    yspot = start[1] - .8*clamp(mouse[1] - start[1], 0, 80)
    xspot = start[0] - .8*clamp(mouse[0] - start[0], -80, 80) 
    return xspot, yspot


def inmotion(sheet, out):
    time = 0
    while sheet.aStoneMoves():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pygame.time.delay(10)
        time += 1
        sheet.view(out)
        for stone in sheet.movers:
            res = stone.move(time % 10 == 0 and time > 0)
            if not res:
                sheet.clearStone(stone)
        pairs = [(i, j) for i in sheet.stones for j in sheet.stones]
        for a, b in pairs:
            if a != b and distanceFormula(a, b) < 2*sRad:
                if sheet.whitelist(a, b, time): # only want this called if they in range
                    s1 = collision(a, b)
                    s2 = collision(b, a)
                    a.xv, a.yv = s1
                    b.xv, b.yv = s2
                    a.curve, b.curve = 0, 0
        pygame.display.update()


def inmotion_blind(sheet):
    time = 0
    while sheet.aStoneMoves():
        if time > 10000:
            print('woop')
        time += 1
        for stone in sheet.movers:
            res = stone.move(time % 10 == 0 and time > 0)
            if not res:
                sheet.clearStone(stone)
        pairs = [(i, j) for i in sheet.stones for j in sheet.stones]
        for a, b in pairs:
            if a != b and distanceFormula(a, b) < 2*sRad:
                if sheet.whitelist(a, b, time): # only want this called if they in range
                    s1 = collision(a, b)
                    s2 = collision(b, a)
                    a.xv, a.yv = s1
                    b.xv, b.yv = s2
                    a.curve, b.curve = 0, 0
        


def collision(stone1, stone2):  # call it for both before setting v's
    v1 = [stone1.xv, stone1.yv]
    v2 = [stone2.xv, stone2.yv]
    xvec = [stone1.x - stone2.x, stone1.y - stone2.y]
    vvec = listsub(v1, v2)
    dotted = numpy.dot(vvec, xvec)
    magx = pythag(xvec[0], xvec[1]) ** 2
    diff = listmult(xvec, dotted/magx)
    final = listsub(v1, diff)
    return final


def gamepreview(home, away, out, ends, rocks):
    colors = colorchecker(home.prefs, away.prefs, req = 25)
    home.color = colors[0]
    away.color = colors[1]
    out.fill(color=WhiteC)
    text('Click to continue', (500, 50), 16, out)
    text(f'{ends}-end game', (500, 75), 24, out)
    text(f'{rocks} stones per end', (500, 100), 24, out)
    text(f'HOME', (250, 50), 16, out)
    text(f'AWAY', (750, 50), 16, out)
    pygame.draw.circle(out, home.color, (450, 225), 30)
    pygame.draw.circle(out, away.color, (550, 225), 30)
    text('VS', (500, 300), 40, out)
    sidepreview(home, out, 250)
    sidepreview(away, out, 750)
    text('*Like reading a book, down left column and then down right (if there) is getting more recent', (500, 675), 15, out)
    pygame.display.update()
    page = True
    while page:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                page = False
            if event.type == pygame.QUIT:
                pygame.quit()

def sidepreview(team, out, center):
    if team.controlled:
        text('---USER---', (center, 100), 32, out)
    text(team, (center, 150), 40, out)
    if modePick == '2-player':
        image(f'./{l1 if center == 250 else l2}/{team.name.replace(space, underscore)}.png', out, tl=(center-150, 175), size=(300, 300 * (3/4)))
    else:
        image(f'./{leaguePick}/{team.name.replace(space, underscore)}.png', out, tl=(center-150, 175), size=(300, 300 * (3/4)))
    text(f'{team.spot()}{endmatch[str(team.spot())]} in {team.division.name}', (center, 425), 24, out)
    text(f'Record: {team.wins}-{team.loss} ({team.PointsFor - team.PointsAgainst} PD)', (center, 450), 24, out)
    text(f'X-acc: {team.Xacc}, Y-acc: {team.Yacc}, C-Acc: {team.Cacc}', (center, 475), 24, out)
    text('Recent results:*', (center, 500), 16, out)
    recents = team.games[-10:]
    for game in range(len(recents)):
        recents[game].output_small(out, center-100 + (200*(game//5)), 525 + 25*(game%5))







