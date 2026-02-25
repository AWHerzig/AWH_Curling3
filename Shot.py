from Objects import *



def simulate_shot(start_x, init_yv, spin, target_y, max_steps=2000):

    x = start_x
    y = 0.0
    xv = 0.0
    yv = init_yv

    for _ in range(max_steps):

        speed = math.hypot(xv, yv)
        if speed <= STOP_EPS:
            return None  # did not reach target_y

        # --- friction ---
        angle = math.atan2(yv, xv)
        xv -= FRICTION * math.cos(angle)
        yv -= FRICTION * math.sin(angle)

        speed = math.hypot(xv, yv)

        # --- curl ---
        if speed > 0:
            perp_x = -yv / speed
            perp_y =  xv / speed

            late_factor = 1 + LATE_CURL_BOOST * (1 - speed / 1.2)
            curl_accel = CURL_K * -spin * speed * late_factor

            xv += curl_accel * perp_x
            yv += curl_accel * perp_y

        prev_x, prev_y = x, y

        x += xv
        y += yv

        # --- interpolate exact crossing ---
        if y >= target_y:
            t = (target_y - prev_y) / (y - prev_y)
            x_at_target = prev_x + t * (x - prev_x)
            speed_at_target = math.hypot(xv, yv)
            return x_at_target, speed_at_target

    return None

def solve_start_x(target_x, target_y, init_yv, spin):

    low = target_x - 15
    high = target_x + 15

    for _ in range(30):

        mid = (low + high) / 2
        result = simulate_shot(mid, init_yv, spin, target_y)

        if result is None:
            # not enough weight to reach
            return None

        final_x, _ = result

        if final_x < target_x:
            low = mid
        else:
            high = mid

    return (low + high) / 2

SHOT_WEIGHTS = {
    'front': .5,
    'guard': .6,
    'top8': .78,
    'top4': .87,
    'pocket': .92,
    'teeline': .95, 
    'back4': 1.03,
    'back8': 1.1,
    'back12': 1.17,
    'firm': 1.35,
    'hard': 2
}

def getShooter(SHEET):
    ShotTeam = SHEET.hammer if SHEET.shotsleft%2 else SHEET.leadteam
    ShotPos = ['skip', 'third', 'second', 'lead'][(SHEET.shotsleft-1)//4]
    if ShotPos == 'lead':
        sweepers = .5*(eval(f'SHEET.{ShotTeam}.second.sweep')+eval(f'SHEET.{ShotTeam}.third.sweep'))
    elif ShotPos == 'second':
        sweepers = .5*(eval(f'SHEET.{ShotTeam}.lead.sweep')+eval(f'SHEET.{ShotTeam}.third.sweep'))
    elif ShotPos == 'second':
        sweepers = .5*(eval(f'SHEET.{ShotTeam}.lead.sweep')+eval(f'SHEET.{ShotTeam}.second.sweep'))
    else: # skip
        sweepers = .5*(eval(f'SHEET.{ShotTeam}.lead.sweep')+eval(f'SHEET.{ShotTeam}.second.sweep'))
    return ShotTeam, ShotPos, eval(f'SHEET.{ShotTeam}.{ShotPos}'), sweepers

def set_shot(target_x, shot_type, spin, target_y=0.1):

    if shot_type not in SHOT_WEIGHTS:
        raise ValueError("Unknown shot type")

    init_yv = SHOT_WEIGHTS[shot_type]
    start_x = None
    while start_x is None:
        start_x = solve_start_x(target_x, target_y, init_yv, spin)
        target_y -= 1

    return start_x, init_yv, spin
    """
    return {
        "start_x": start_x, #- (2.7*spin)*((init_yv/.95)**.5)),
        #"start_y": 0.0,
        #"xv": 0.0,
        "yv": init_yv,
        "spin": spin
    }
    """

def path_is_blocked(start_x, init_yv, spin, stones_df, ignore_id=None):

    x = start_x
    y = 0.0
    xv = 0.0
    yv = init_yv

    for _ in range(3000):

        speed = math.hypot(xv, yv)
        if speed <= STOP_EPS:
            return False  # reached resting point without hitting anything

        # friction
        angle = math.atan2(yv, xv)
        xv -= FRICTION * math.cos(angle)
        yv -= FRICTION * math.sin(angle)

        speed = math.hypot(xv, yv)

        # curl
        if speed > 0:
            perp_x = -yv / speed
            perp_y =  xv / speed

            late_factor = 1 + LATE_CURL_BOOST * (1 - speed / 1.2)
            curl_accel = CURL_K * -spin * speed * late_factor

            xv += curl_accel * perp_x
            yv += curl_accel * perp_y

        x += xv
        y += yv

        # --- collision check ---
        for idx, row in stones_df.iterrows():

            if idx == ignore_id:
                continue

            dx = row["x"] - x
            dy = row["y"] - y

            if dx*dx + dy*dy <= (2*1)**2:
                #print('Spin:', spin)
                #print("Path blocked by stone at", row["x"], row["y"])
                return True  # path blocked

    return False


def movementstep(SHEET, dt=1.0):

    to_remove = []

    for stoneid in SHEET.df.index:

        xv = SHEET.df.loc[stoneid, 'xv']
        yv = SHEET.df.loc[stoneid, 'yv']
        spin = SHEET.df.loc[stoneid, 'curve']

        speed = math.hypot(xv, yv)

        if speed > 0:

            # -------------------
            # 1️⃣ Apply friction (scaled by dt)
            # -------------------
            angle = math.atan2(yv, xv)

            xv -= FRICTION * math.cos(angle) * dt
            yv -= FRICTION * math.sin(angle) * dt

            # prevent reversing direction
            new_speed = math.hypot(xv, yv)
            if FRICTION * dt > speed:
                xv = 0
                yv = 0

            # -------------------
            # 2️⃣ Apply curl acceleration (scaled by dt)
            # -------------------
            speed = math.hypot(xv, yv)

            if speed > 0:

                perp_x = -yv / speed
                perp_y =  xv / speed

                late_factor = 1 + LATE_CURL_BOOST * (1 - speed / 1.2)
                curl_accel = CURL_K * -spin * speed * late_factor

                xv += curl_accel * perp_x * dt
                yv += curl_accel * perp_y * dt

        # -------------------
        # Stop condition
        # -------------------
        speed = math.hypot(xv, yv)

        if speed < STOP_EPS:
            xv = 0
            yv = 0
            SHEET.df.loc[stoneid, 'curve'] = 0

        # -------------------
        # Update position (scaled by dt)
        # -------------------
        SHEET.df.loc[stoneid, 'x'] += xv * dt
        SHEET.df.loc[stoneid, 'y'] += yv * dt

        SHEET.df.loc[stoneid, 'xv'] = xv
        SHEET.df.loc[stoneid, 'yv'] = yv

        # -------------------
        # Remove out-of-bounds
        # -------------------
        if (
            SHEET.df.loc[stoneid, 'y'] > 50
            or abs(SHEET.df.loc[stoneid, 'x']) > 17
        ):
            to_remove.append(stoneid)

    # Remove outside loop to avoid mutation during iteration
    if to_remove:
        SHEET.df.drop(to_remove, inplace=True)
def displayStones(SHEET, screen):
    for stoneid in SHEET.df.index:
        #print(SHEET.df.loc[stoneid])
        pygame.draw.circle(screen, red if SHEET.df.loc[stoneid, 'team'] == 'Home' else yellow, center=SheetToScreen(SHEET.df.loc[stoneid, 'x'], SHEET.df.loc[stoneid, 'y']), radius=25)
        #print(SHEET.df.loc[stoneid, 'x'])
        #print(SHEET.df.loc[stoneid, 'y'])
        #text(f'{round(SHEET.df.loc[stoneid, 'x'], 1)} {round(SHEET.df.loc[stoneid, 'y'], 1)}', (500, 900), 48, screen)

def check_collision(SHEET, stone1, stone2):

    dx = SHEET.df.loc[stone2, 'x'] - SHEET.df.loc[stone1, 'x']
    dy = SHEET.df.loc[stone2, 'y'] - SHEET.df.loc[stone1, 'y']

    dist_sq = dx*dx + dy*dy
    min_dist = 2 * 1 # STONE RADIUS HERE IS 1, cuz its in sheet units not the 25 of screen units

    return dist_sq <= min_dist * min_dist

def resolve_collision(SHEET, stone1, stone2):

    x1, y1 = SHEET.df.loc[stone1, 'x'], SHEET.df.loc[stone1, 'y']
    x2, y2 = SHEET.df.loc[stone2, 'x'], SHEET.df.loc[stone2, 'y']

    vx1, vy1 = SHEET.df.loc[stone1, 'xv'], SHEET.df.loc[stone1, 'yv']
    vx2, vy2 = SHEET.df.loc[stone2, 'xv'], SHEET.df.loc[stone2, 'yv']

    # --- compute normal vector ---
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)

    if dist == 0:
        return  # avoid division by zero

    nx = dx / dist
    ny = dy / dist

    # --- tangential vector ---
    tx = -ny
    ty = nx

    # --- project velocities ---
    v1n = vx1 * nx + vy1 * ny
    v1t = vx1 * tx + vy1 * ty

    v2n = vx2 * nx + vy2 * ny
    v2t = vx2 * tx + vy2 * ty

    # --- swap normal components (equal mass elastic) ---
    v1n_new = v2n
    v2n_new = v1n

    # --- convert back to x/y ---
    SHEET.df.loc[stone1, 'xv'] = v1n_new * nx + v1t * tx
    SHEET.df.loc[stone1, 'yv'] = v1n_new * ny + v1t * ty

    SHEET.df.loc[stone2, 'xv'] = v2n_new * nx + v2t * tx
    SHEET.df.loc[stone2, 'yv'] = v2n_new * ny + v2t * ty

def separate_stones(SHEET, stone1, stone2):

    dx = SHEET.df.loc[stone2, 'x'] - SHEET.df.loc[stone1, 'x']
    dy = SHEET.df.loc[stone2, 'y'] - SHEET.df.loc[stone1, 'y']
    dist = math.hypot(dx, dy)

    overlap = 2 * 1 - dist  # STONE RADIUS HERE IS 1, cuz its in sheet units not the 25 of screen units


    if overlap > 0 and dist > 0:

        nx = dx / dist
        ny = dy / dist

        correction = overlap / 2

        SHEET.df.loc[stone1, 'x'] -= nx * correction
        SHEET.df.loc[stone1, 'y'] -= ny * correction

        SHEET.df.loc[stone2, 'x'] += nx * correction
        SHEET.df.loc[stone2, 'y'] += ny * correction

def collisionstep(SHEET):
    for i in range(len(SHEET.df)):
        stoneI = SHEET.df.index[i]
        for j in range(i+1, len(SHEET.df)):
            stoneJ = SHEET.df.index[j]
            if check_collision(SHEET, stoneI, stoneJ):
                resolve_collision(SHEET, stoneI, stoneJ)
                separate_stones(SHEET, stoneI, stoneJ)


def amIScoring(scoreDF, stoneid):
    if stoneid not in scoreDF.index:
        print('not scoring because not in index')
        return False
    Ranked = scoreDF.sort_values('Distance')
    return Ranked.loc[stoneid, 'Distance'] < 16 and len(Ranked.iloc[:(Ranked.index.to_list().index(stoneid)+1), 2].unique()) == 1
def amIGuarded(scoreDF, stoneid):
    if scoreDF.loc[stoneid, 'Distance'] > 16:
        return 0
    return len(scoreDF[np.isclose(scoreDF.x, scoreDF.loc[stoneid, 'x'], rtol = 0, atol = 2) & (scoreDF.y < scoreDF.loc[stoneid, 'y'])])
def amIGuarding(scoreDF, stoneid):
    scoreDF2 = scoreDF[scoreDF.Distance < 16]
    return len(scoreDF2[np.isclose(scoreDF2.x, scoreDF.loc[stoneid, 'x'], rtol = 0, atol = 2) & (scoreDF2.y > scoreDF.loc[stoneid, 'y'])])
def countGuardsX(scoreDF, x, y = BUTTON[1]):
    if(len(scoreDF) == 0):
        return 0
    return len(scoreDF[np.isclose(x, scoreDF.x, rtol = 0, atol = 2) & (scoreDF.y < y)])
def ShotScoring(SCORINGDF, stonesleft, ShotTeam, returnDF = False):
    SCORINGDF['Distance'] = [distanceFormula(0, BUTTON[1], SCORINGDF.loc[i, 'x'], SCORINGDF.loc[i, 'y']) for i in SCORINGDF.index]
    SCORINGDF['MyTeam'] = SCORINGDF.team.apply(lambda x: 1 if x == ShotTeam else -1)
    # Scoring
    SCORINGDF['Showing'] = [amIScoring(SCORINGDF, x) for x in SCORINGDF.index]
    SCORINGDF['InHouseNotShowing'] = [not amIScoring(SCORINGDF, x) and SCORINGDF.loc[x, 'Distance'] < 16 for x in SCORINGDF.index]
    SCORINGDF['Guarded'] = [amIGuarded(SCORINGDF, x) for x in SCORINGDF.index]
    SCORINGDF['Guarding'] = [amIGuarding(SCORINGDF, x) for x in SCORINGDF.index]
    SCORINGDF['Score'] = SCORINGDF.MyTeam*((SCORINGDF.Showing+.5*SCORINGDF.InHouseNotShowing)*(SCORINGDF.Guarded+1)+(.5*SCORINGDF.Guarding) if stonesleft > 1 else SCORINGDF.Showing)
    if returnDF:
        return SCORINGDF
    return SCORINGDF.Score.sum()
def testShotDF(SHEET, tarx, tary, Team, removals=[]):
    X = SHEET.df[['x', 'y', 'team']].copy()
    X = X.drop(removals)
    X.loc['TEST'] = tarx, tary, Team
    return X


def getShotSpecs(SHEET, ShotTeam, Shooter, returnDF = False): # tar x, type, spin
    #return random.randrange(-10, 10), random.choice(list(SHOT_WEIGHTS.keys())), random.randrange(-2, 2)
    #return 0, 'firm', 0 # random.randrange(-3, 3)
    if SHEET.shotsleft == 16 and random.uniform(0, 1) < .75: # Leads often throw guards
        return 0, .1, 'guard', 0, None
    elif SHEET.shotsleft == 15 and random.uniform(0, 1) < .75: # Leads often throw guards, corner bc they have hammer
        return random.choice([-10, 10]), .1, 'guard', 0, None
    options = pd.DataFrame(columns=['TargetX', 'TargetY', 'Weight', 'Value', 'Risk', 'TargetID'])
    # burn
    options.loc['burn'] = 50, 50, 'hard', ShotScoring(SHEET.df[['x', 'y', 'team']].copy(), SHEET.shotsleft, ShotTeam), 0, None
    # DRAW BUTTON
    options.loc['Draw_Button'] = 0, BUTTON[1], 'teeline', ShotScoring(testShotDF(SHEET, 0, BUTTON[1], ShotTeam), SHEET.shotsleft, ShotTeam), countGuardsX(SHEET.df, 0), None
    # GUARD ANY OF YOURS
    GuardOptions = SHEET.df.copy()
    GuardOptions['Distance'] = [distanceFormula(0, BUTTON[1], GuardOptions.loc[i, 'x'], GuardOptions.loc[i, 'y']) for i in GuardOptions.index]
    GuardOptions = GuardOptions[(GuardOptions.team == ShotTeam) & (GuardOptions.Distance < 16)]
    for gOP in GuardOptions.index:
        options.loc[f'Guard_{gOP}'] =  GuardOptions.loc[gOP, 'x'], .1, 'guard', ShotScoring(testShotDF(SHEET, GuardOptions.loc[gOP, 'x'], 5, ShotTeam), SHEET.shotsleft, ShotTeam), 0, None # countGuardsX(SHEET.df, GuardOptions.loc[gOP, 'x'])
    # HIT ANY OF THEIRS
    HitOptions = SHEET.df.copy()
    HitOptions['Distance'] = [distanceFormula(0, BUTTON[1], HitOptions.loc[i, 'x'], HitOptions.loc[i, 'y']) for i in HitOptions.index]
    HitOptions = HitOptions[(HitOptions.team != ShotTeam) & (HitOptions.Distance < 16)]
    for hOP in HitOptions.index:
        ## Hit and stay
        options.loc[f'Hit_{hOP}'] = HitOptions.loc[hOP, 'x'], HitOptions.loc[hOP, 'y']-1, 'firm', ShotScoring(testShotDF(SHEET, HitOptions.loc[hOP, 'x'], HitOptions.loc[hOP, 'y']-1, ShotTeam, hOP), SHEET.shotsleft, ShotTeam), \
            countGuardsX(SHEET.df, HitOptions.loc[hOP, 'x'], y = HitOptions.loc[hOP, 'y']), hOP
        ## Pure Peel
        options.loc[f'Peel_{hOP}'] = HitOptions.loc[hOP, 'x']+.5, HitOptions.loc[hOP, 'y'], 'hard', ShotScoring(testShotDF(SHEET, -20, 50, ShotTeam, hOP), SHEET.shotsleft, ShotTeam), \
            countGuardsX(SHEET.df, HitOptions.loc[hOP, 'x'], y = HitOptions.loc[hOP, 'y']), hOP
        
    # DOUBLE
    Hit2Options = SHEET.df.copy()
    Hit2Options = Hit2Options[(Hit2Options.team != ShotTeam)][['x', 'y']].reset_index(names = 'stoneid')
    Combos = Hit2Options.merge(Hit2Options, how = 'cross').query('stoneid_x != stoneid_y').query('y_y > y_x')
    Combos.y_y = Combos.y_y - math.sqrt(2)
    Combos.x_y = Combos.x_y - np.where(Combos.x_y > Combos.x_x, 1, -1)*math.sqrt(2)
    Combos['Angle'] = Combos.apply(lambda row: math.atan2(row['y_y'] - row['y_x'], row['x_y'] - row['x_x']), axis=1)
    Combos = Combos[(Combos.Angle >= math.pi/4) & (Combos.Angle <= 3*math.pi/4)]
    Combos['x'] = Combos.x_x + 2*np.where(Combos.x_y > Combos.x_x, 1, -1)*np.cos(Combos.Angle)
    Combos['y'] = Combos.y_x - 2*np.sin(Combos.Angle)
    Combos = Combos[['stoneid_x', 'stoneid_y', 'x', 'y']]
    for cOP in Combos.index:
        options.loc[f'Double_{Combos.loc[cOP, "stoneid_x"]}_{Combos.loc[cOP, "stoneid_y"]}'] = Combos.loc[cOP, 'x'], Combos.loc[cOP, 'y'], 'hard', ShotScoring(testShotDF(SHEET, Combos.loc[cOP, 'x'], Combos.loc[cOP, 'y'], ShotTeam, [Combos.loc[cOP, 'stoneid_x'], Combos.loc[cOP, 'stoneid_y']]), SHEET.shotsleft, ShotTeam), \
            countGuardsX(SHEET.df, Combos.loc[cOP, 'x'], y = Combos.loc[cOP, 'y']), Combos.loc[cOP, 'stoneid_x'] # assumes the shot rock leaves
    # Draw top 4 left middle or right
    for DP in [-10, 0, 10]:
        options.loc[f'Draw_{DP}'] = DP, BUTTON[1]-5, 'top4', ShotScoring(testShotDF(SHEET, DP, BUTTON[1]-5, ShotTeam), SHEET.shotsleft, ShotTeam), countGuardsX(SHEET.df, DP, y = BUTTON[1]-5), None

    options['Score'] = options.Value - (0 if -2*SHEET.getLead(ShotTeam) > (SHEET.numends-SHEET.end-1) else .5)*options.Risk
    if returnDF:
        return options.sort_values('Score', ascending=False)
    Choice = options.sort_values('Score', ascending=False).iloc[0]
    #print(options.sort_values('Score', ascending=False))
    return Choice.TargetX, Choice.TargetY, Choice.Weight, True if Choice.Risk != 0 else False, Choice.TargetID

def Shot(SHEET, screen, Team, SweeperScore, Pos, Shooter, start_x, init_yv, spin):
    dicerolltop = 100-.1*SweeperScore
    BlendedAccuracy = (Shooter.xacc+Shooter.yacc+Shooter.curl)/3
    if random.uniform(0, dicerolltop) < .5*BlendedAccuracy:
        pass # shot goes to intended target
    else:
        diceroll_x, diceroll_y, diceroll_curl = random.uniform(0, dicerolltop), random.uniform(0, dicerolltop), random.uniform(0, dicerolltop)
        if diceroll_x > Shooter.xacc:
            difference = diceroll_x - Shooter.xacc
            miss = difference/10*random.choice([-1, 1]) # max miss of 10 units
            start_x += miss
        if diceroll_y > Shooter.yacc:
            difference = diceroll_y - Shooter.yacc
            miss = difference/200*random.choice([-1, 1]) # max miss of .5 units
            init_yv += miss
        if diceroll_curl > Shooter.curl:
            difference = diceroll_curl - Shooter.curl
            miss = difference/50*random.choice([-1, 1]) # max miss of 2 units
            spin += miss
    SHEET.df.loc[f'{eval(f"SHEET.{Team}.ABR")}-{SHEET.shotsleft}'] = [start_x, 0.0, 0, init_yv, spin, Team]
    while not SHEET.DoneMoving():
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    break
        pygame.time.delay(5)
        for _ in range(4):
            movementstep(SHEET, dt=1/4)
            collisionstep(SHEET)
        # Output
        screen.fill(black)
        #pygame.draw.line(screen, white, (screenWidth*.57, screenHeight*.01), (screenWidth*.93, screenHeight*.01))
        drawSheet(screen)
        drawScoreboard(screen, SHEET, Team, Pos, Shooter, SweeperScore)
        displayStones(SHEET, screen)
        
        pygame.display.update()
    SHEET.shotsleft -= 1

def getCPUSpin(SHEET, Shooter, needspin, tar_X, tar_Y, shot_type, TargetID):
    if needspin:
        if Shooter.twowaycurl:
            possible_spins = [-.5, .5, -1, 1, -1.5, 1.5, -2, 2, -2.5, 2.5, -3, 3, -3.5, 3.5, -4, 4, -4.5, 4.5, -5, 5]
        else:
            possible_spins = [-.5, -1, -1.5, -2, -2.5, -3, -3.5, -4, -4.5, -5]
        for spin in possible_spins:
            ShotTargets = set_shot(
            target_x=tar_X,
            target_y=tar_Y,
            shot_type=shot_type,
            spin=spin
        ) # start_x, init_yv, spin
            if ShotTargets is None:
                continue
            blocked = path_is_blocked(
                ShotTargets[0],
                ShotTargets[1],
                ShotTargets[2],
                SHEET.df,
                ignore_id=TargetID
            )
            if not blocked:
                break  # valid path
    else:
        ShotTargets = None
    if ShotTargets is None:
        ShotTargets = set_shot(
            target_x=tar_X,
            target_y=tar_Y,
            shot_type=shot_type,
            spin=0
        )
    return ShotTargets

def getShotSpecs_USER(screen, joystick, SHEET, ShotTeam, Pos, Shooter, SweeperScore):
    chosen = False
    xstart = 0
    typeshotind = 0
    spin = 0
    shotoptions = list(SHOT_WEIGHTS.keys())

    DEADZONE = 0.2
    AXIS_SENS = 0.4       # movement sensitivity
    TRIGGER_THRESH = 0.6  # how far trigger must be pressed

    trigger_cooldown = 0  # prevents rapid cycling

    while not chosen:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                return None

            # A button confirms
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button
                    chosen = True

        # -------- AXIS READING --------
        # Left stick X → xstart
        left_x = joystick.get_axis(0)

        if abs(left_x) > DEADZONE:
            xstart += left_x * AXIS_SENS

        # Right stick X → spin
        right_x = joystick.get_axis(2)  # may be 3 on some systems

        if abs(right_x) > DEADZONE:
            spin += right_x * AXIS_SENS

        # Triggers → shot type
        left_trigger = (joystick.get_axis(4) + 1)
        right_trigger = (joystick.get_axis(5) + 1)

        if trigger_cooldown <= 0:
            if left_trigger > TRIGGER_THRESH:
                typeshotind = (typeshotind - 1) % len(shotoptions)
                trigger_cooldown = 5  # frames delay
            elif right_trigger > TRIGGER_THRESH:
                typeshotind = (typeshotind + 1) % len(shotoptions)
                trigger_cooldown = 5

        trigger_cooldown -= 1

        # -------- CLAMP VALUES --------
        xstart = max(-18, min(18, xstart))

        if Shooter.twowaycurl:
            spin = max(-5, min(5, spin))
        else:
            spin = max(-5, min(0, spin))

        # -------- DRAW SCREEN --------
        screen.fill(black)
        drawSheet(screen)
        drawScoreboard(screen, SHEET, ShotTeam, Pos, Shooter, SweeperScore)
        displayStones(SHEET, screen)

        text(f'CHOOSE SHOT: {shotoptions[typeshotind]}',
             (screenWidth*.33, screenHeight*.85), 48, screen, spot='midleft')
        text(f'START X-POSITION: {round(xstart,2)}',
             (screenWidth*.33, screenHeight*.9), 48, screen, spot='midleft')
        text(f'SPIN: {round(spin,2)}',
             (screenWidth*.33, screenHeight*.95), 48, screen, spot='midleft')

        pygame.display.update()

    return xstart, SHOT_WEIGHTS[shotoptions[typeshotind]], spin