import pygame
import numpy as np
import names
import pandas as pd
import datetime
import time
import sys
import itertools
import math
import os
import random
import subprocess
import collections
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append('c:\\users\\leojo\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\\localcache\\local-packages\\python313\\site-packages')
sys.path.append('c:\\Users\\leojo\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python313\\Scripts')
import matplotlib
from tabulate import tabulate

pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.options.mode.chained_assignment = None

#screenWidth, screenHeight = 1250, 600
screenWidth, screenHeight = 2500, 1200
yardPixels = screenHeight // 30


FRICTION = 0.015          # forward deceleration
CURL_K = 0.0025           # base curl strength
LATE_CURL_BOOST = 1.8     # how much it bends late
STOP_EPS = 0.01
BUTTON = (0, 29.76)

CCBracketPlaces = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 20, 21, 22, 23, 40, 41, 42, 43]


# COLORS
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
cyan = (0, 255, 255)
magenta = (255, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)
orange = (255, 165, 0)
purple = (128, 0, 128)
brown = (139, 69, 19)
pink = (255, 192, 203)
lime = (0, 255, 0)
navy = (0, 0, 128)


def clamp(x, lo, hi):
    if x > hi:
        return hi
    if x < lo:
        return lo
    return x
def adjustDraw(mu, rng):
    return mu + 2*rng*(np.random.beta(3, 3)-.5)

def farthest_bw(rgb):
    """
    Return either white or black (as an RGB tuple),
    whichever is farther from the input RGB color.
    """
    r, g, b = rgb

    black = (0, 0, 0)
    white = (255, 255, 255)

    # squared distances (no need for sqrt)
    dist_black = r*r + g*g + b*b
    dist_white = (255 - r)**2 + (255 - g)**2 + (255 - b)**2

    return white if dist_white > dist_black else black

def colors_too_close_rgb(col1, col2, threshold=10000):
    """
    Returns True if two RGB colors are visually too close.
    threshold ≈ 60–100 is a common range.
    """
    r1, g1, b1 = col1
    r2, g2, b2 = col2

    dist_sq = (r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2
    print(f'margin {dist_sq-threshold}')
    return dist_sq < threshold



def text(string, pos, size, surface, color=white, spot = 'center'):
    font = pygame.font.Font('freesansbold.ttf', size)
    obj = font.render(str(string), True, color)
    textRect = obj.get_rect()
    if spot == 'center':
        textRect.center = pos
    elif spot == 'midleft':
        textRect.midleft = pos
    surface.blit(obj, textRect)

def distanceFormula(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2)**.5

# Function to convert polar to Cartesian
def polar_to_cartesian(r, theta):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

# Function to convert Cartesian to polar
def cartesian_to_polar(x, y):
    r = (x**2 + y**2)**.5
    theta = np.arctan2(y, x)  # atan2 ensures correct quadrant
    return r, theta

# Function to add two vectors in polar coordinates
def vector_addition_polar(r1, theta1, r2, theta2):
    # Convert polar to Cartesian
    x1, y1 = polar_to_cartesian(r1, theta1)
    x2, y2 = polar_to_cartesian(r2, theta2)
    
    # Add the vectors in Cartesian coordinates
    x_result = x1 + x2
    y_result = y1 + y2
    
    # Convert the result back to polar coordinates
    r_result, theta_result = cartesian_to_polar(x_result, y_result)
    return r_result, theta_result

def startPygame(caption):
    pygame.init()
    pygame.joystick.init()
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption(caption)
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    return screen, joystick

def drawVBallCourt(screen):
    screen.fill(black)
    pygame.draw.line(screen, white, (screenWidth*.1, screenHeight*.15), (screenWidth*.1, screenHeight*.9))
    pygame.draw.line(screen, white, (screenWidth*.9, screenHeight*.15), (screenWidth*.9, screenHeight*.9))
    pygame.draw.line(screen, white, (screenWidth*.1, screenHeight*.15), (screenWidth*.9, screenHeight*.15))
    pygame.draw.line(screen, white, (screenWidth*.1, screenHeight*.9), (screenWidth*.9, screenHeight*.9))
    pygame.draw.line(screen, white, (screenWidth*.5, screenHeight*.15), (screenWidth*.5, screenHeight*.9), width = 1)
        
        
def fill_combinations(df, col1, col2):
    unique_col1 = df[col1].unique()
    unique_col2 = df[col2].unique()
    combinations = list(itertools.product(unique_col1, unique_col2))
    new_df = pd.DataFrame(combinations, columns=[col1, col2])
    return new_df

def bracket(teams, ogteams = None, topL = (50, 25), botR = (screenWidth-50, screenHeight-50), page = True, caption = 'BRACKET', seeded = True):  # This shit is dope, teams should be seeded. More than 32 really get squeezed.
    surf, joystick = startPygame(caption)
    if page:
        surf.fill(color=black)
    minX, minY = topL
    maxX, maxY = botR
    n = len(teams)
    R = math.ceil(math.log(n, 2)) + 1
    xpr = (maxX - minX) / R
    bracketRecursive((maxX, .5*(minY+maxY)), 1, R, xpr, minY, maxY, surf, teams, ogteams, 1, seeded=seeded)
    pygame.display.update()
    while page:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                page = False
            if event.type == pygame.JOYBUTTONDOWN and event.button == 0:  # A button on Xbox controller
                page = False
            if event.type == pygame.QUIT:
                pygame.quit()

def bracketRecursive(front, r, maxr, xpr, ceil, floor, surf, teams, ogteams, seed, seeded = True):  # ceil in minY, floor is maxY
    #print(seeded)
    back = front[0] - xpr, front[1]
    up = back[0], .5*(back[1] + ceil)
    down = back[0], .5*(floor + back[1])
    pygame.draw.line(surf, white, front, back)
    if r == maxr or 2**r + 1 - seed > len(teams) or allNone(teams[2**r - seed]):
        if seeded:
            text(f'#{index_ignore_none(ogteams, teams[seed-1])+1} {teams[seed-1]}', (.5*(front[0]+back[0]), front[1]-10), 16, surf)
        else:
            text(f'{teams[seed-1]}', (.5*(front[0]+back[0]), front[1]-10), 16, surf)
        return
    if r < maxr:
        
        pygame.draw.line(surf, white, back, up)
        pygame.draw.line(surf, white, back, down)
        bracketRecursive(up, r + 1, maxr, xpr, ceil, front[1], surf, teams, ogteams, seed, seeded=seeded)
        bracketRecursive(down, r + 1, maxr, xpr, front[1], floor, surf, teams, ogteams, 2**r + 1 - seed, seeded=seeded)

def bracketWrap(PlayoffTeams, lg, screen):
    if lg == 'NFL':
        regs = ['Northeast', 'Southeast', 'Midwest', 'Pacific']
    elif lg == 'NCAA':
        regs = None
    else:
        regs = ['Northeast', 'Southeast', 'Northwest', 'Southwest']

    bracket(PlayoffTeams[lg]['Start'], screen, PlayoffTeams[lg]['Winners'], topL = (150, 200), botR = (screenWidth-50, screenHeight-50), page = False, 
        regions = regs)
        
def allNone(x):
    if x is None:
        return True
    elif isinstance(x, tuple):
        return allNone(x[0]) and allNone(x[1])
    else:
        return False
    
def GenerateSchedule():
    subprocess.run(
        ['C:\\PROGRA~1\\R\\R-44~1.2\\bin\\x64\\Rscript.exe', 'League/ScheduleBuild.R'],
        check=True
    )

def dataframe_to_aligned_strings_with_headers_noRounding(df):
    # Determine maximum width for each column based on column headers and data
    col_widths = {
        col: max(df[col].astype(str).map(len).max(), len(col))
        for col in df.columns
    }
    
    # Prepare the header row
    header_row = ' | '.join(
        f"{col:<{col_widths[col]}}"
        for col in df.columns
    )
    
    # Prepare the data rows
    data_rows = []
    for index, row in df.iterrows():
        row_str = ' | '.join(
            f"{str(row[col]):>{col_widths[col]}}"  # Right-align each column
            for col in df.columns
        )
        data_rows.append('|'+row_str+'|')
    
    # Combine header and data rows
    aligned_strings = ['|'+header_row+'|'] + data_rows
    
    return aligned_strings

def dataframe_to_aligned_strings_with_headers(df):
    if df.empty:
        header_row = ' | '.join(df.columns)
        return ['|' + header_row + '|'] if not df.columns.empty else []

    # Determine maximum width for each column based on column headers and formatted data
    col_widths = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Format numeric values to 1 decimal place for width calculation
            formatted_values = df[col].map(lambda x: f"{x:.0f}" if pd.notnull(x) else "")
        else:
            formatted_values = df[col].astype(str)
        max_width = max(formatted_values.map(len).max(), len(col))
        col_widths[col] = max_width

    # Prepare the header row
    header_row = ' | '.join(
        f"{col:<{col_widths[col]}}"
        for col in df.columns
    )

    # Prepare the data rows
    data_rows = []
    for index, row in df.iterrows():
        row_items = []
        for col in df.columns:
            val = row[col]
            if pd.api.types.is_numeric_dtype(df[col]) and pd.notnull(val):
                val_str = f"{val:.0f}"
            else:
                val_str = str(val)
            row_items.append(f"{val_str:>{col_widths[col]}}")
        row_str = ' | '.join(row_items)
        data_rows.append('|' + row_str + '|')

    # Combine header and data rows
    aligned_strings = ['|' + header_row + '|'] + data_rows

    return aligned_strings

def round_robin(teams, games_per_team=None):
    """
    Generate a round-robin schedule with a target number of games per team.

    Returns:
        List of slates.
        Each slate is a list of (home, away) tuples.
    """
    teams = list(teams)
    n_real = len(teams)

    # Add bye if odd
    if n_real % 2 == 1:
        teams.append(None)

    n = len(teams)
    half = n // 2
    base_rounds = n - 1

    # Default: traditional round robin
    if games_per_team is None:
        games_per_team = n_real - 1

    # Generate one full round robin
    base_schedule = []
    rotation = teams[:]

    for _ in range(base_rounds):
        slate = []
        for i in range(half):
            t1 = rotation[i]
            t2 = rotation[n - 1 - i]
            if t1 is not None and t2 is not None:
                slate.append((t1, t2))
        base_schedule.append(slate)
        rotation = [rotation[0]] + rotation[-1:] + rotation[1:-1]

    # How many full RR cycles do we need?
    rr_games_per_team = n_real - 1
    full_cycles = games_per_team // rr_games_per_team
    remainder_games = games_per_team % rr_games_per_team

    schedule = []

    # Add full cycles
    for cycle in range(full_cycles):
        for slate in base_schedule:
            if cycle % 2 == 0:
                schedule.append(slate)
            else:
                schedule.append([(b, a) for a, b in slate])

    # Add partial cycle if needed
    if remainder_games > 0:
        partial = base_schedule[:remainder_games]
        if full_cycles % 2 == 1:
            partial = [[(b, a, c) for a, b, c in slate] for slate in partial]
        schedule.extend(partial)

    return schedule






def index_ignore_none(lst, item):
    filtered_index = 0
    for x in lst:
        if x is None:
            continue
        if x == item:
            return filtered_index
        filtered_index += 1
    raise ValueError(f"{item} is not in list")

def trim_trailing_none(lst):
    lst = lst.copy()
    while lst and lst[-1] is None:
        lst.pop()
    return lst

def flatten_2d_lists(*lists_2d):
    """
    Given N 2D lists of equal outer length,
    returns a 2D list where each row is the concatenation
    of the corresponding rows.
    """
    return [
        [elem for row in rows for elem in row]
        for rows in zip(*lists_2d)
    ]


def trim_all_none(lst):
    endlist = []
    for item in lst:
        if item is not None:
            endlist.append(item)
    return endlist

def SheetToScreen(x, y):
    # goes -18-18
    newx = (.75+.01*x)*screenWidth
    newy = .95*screenHeight-(25*y)
    return newx, newy

def drawSheet(screen):
    pygame.draw.line(screen, white, (screenWidth*.57, screenHeight*.95), (screenWidth*.93, screenHeight*.95)) # hog line
    pygame.draw.line(screen, white, (screenWidth*.93, screenHeight*.0), (screenWidth*.93, screenHeight*1.1))
    pygame.draw.line(screen, white, (screenWidth*.57, screenHeight*.0), (screenWidth*.57, screenHeight*1.1))
    pygame.draw.circle(screen, blue, (screenWidth*.75, screenHeight*.33), radius=screenWidth*.15)
    pygame.draw.circle(screen, black, (screenWidth*.75, screenHeight*.33), radius=screenWidth*.10)
    pygame.draw.circle(screen, blue, (screenWidth*.75, screenHeight*.33), radius=screenWidth*.05)
    pygame.draw.circle(screen, black, (screenWidth*.75, screenHeight*.33), radius=screenWidth*.02)
    pygame.draw.line(screen, gray, (screenWidth*.57, screenHeight*.33), (screenWidth*.93, screenHeight*.33))
    pygame.draw.line(screen, gray, (screenWidth*.75, screenHeight*0), (screenWidth*.75, screenHeight*.95))

def drawScoreboard(screen, SHEET, Team, Pos, Shooter, Sweeps):
    #Scoreboard
    text(SHEET.Home.ABR, (screenWidth*.1, screenHeight*.2), size = 48, surface=screen)
    pygame.draw.circle(screen, red, (screenWidth*.05, screenHeight*.2), radius=screenWidth*.015)
    text(SHEET.Away.ABR, (screenWidth*.1, screenHeight*.3), size = 48, surface=screen)
    pygame.draw.circle(screen, yellow, (screenWidth*.05, screenHeight*.3), radius=screenWidth*.015)
    pygame.draw.line(screen, white, (screenWidth*.02, screenHeight*.25), (screenWidth*.5, screenHeight*.25), width=5)
    pygame.draw.line(screen, white, (screenWidth*.02, screenHeight*.15), (screenWidth*.5, screenHeight*.15), width=5)
    for i in range(9):
        pygame.draw.line(screen, white, (screenWidth*(.14+.04*i), screenHeight*.05), (screenWidth*(.14+.04*i), screenHeight*.35), width=5)
    text('TEAM', (screenWidth*.1, screenHeight*.1), size = 48, surface=screen)
    for i in range(9):
        text(str(i+1) if i<8 else 'F', (screenWidth*(.16+.04*i), screenHeight*.1), size = 48, surface=screen)
        if i == 8:
            HS, AS = sum(trim_all_none(SHEET.HomeScore)), sum(trim_all_none(SHEET.AwayScore))
        else:
            HS = SHEET.HomeScore[i] if SHEET.HomeScore[i] is not None else '-'
            AS = SHEET.AwayScore[i] if SHEET.AwayScore[i] is not None else '-'
        text(HS, (screenWidth*(.16+.04*i), screenHeight*.2), size = 48, surface=screen)
        text(AS, (screenWidth*(.16+.04*i), screenHeight*.3), size = 48, surface=screen)
    text('H', (screenWidth*.02, screenHeight*(.2 if SHEET.hammer == 'Home' else .3)), 48, screen)
    # Shots left
    for i in range((SHEET.shotsleft-1)//2):
        pygame.draw.circle(screen, yellow if SHEET.hammer == 'Home' else red, (screenWidth*.01+(50*i), screenHeight*.4), radius=25)
    for i in range(SHEET.shotsleft//2):
        pygame.draw.circle(screen, red if SHEET.hammer == 'Home' else yellow, (screenWidth*.01+(50*i), screenHeight*.45), radius=25)
    # Current Score
    ScoreTeam, Score = SHEET.getScoring()
    ShowString = f'CURRENT SCORING: {eval(f"SHEET.{ScoreTeam}.ABR")} is showing {Score}' if ScoreTeam != 'BLANK' else 'CURRENT SCORING: BLANK END'
    text(ShowString, (screenWidth*.01, screenHeight*.5), 48, screen, spot='midleft')
    # Whos shooting
    text(f'NOW THROWING: {eval(f"SHEET.{Team}.ABR")} {Pos} {Shooter}', (screenWidth*.01, screenHeight*.6), 48, screen, spot='midleft')
    
    # Shooter attributes
    text(f'SHOOTER X-ACCURACY: {round(Shooter.xacc, 1)}', (screenWidth*.01, screenHeight*.65), 48, screen, spot='midleft')
    text(f'SHOOTER Y-ACCURACY: {round(Shooter.yacc, 1)}', (screenWidth*.01, screenHeight*.7), 48, screen, spot='midleft')
    text(f'SHOOTER CURL-ACCURACY: {round(Shooter.curl, 1)}', (screenWidth*.01, screenHeight*.75), 48, screen, spot='midleft')
    text(f'TEAMMATES SWEEP: {round(Sweeps, 1)}', (screenWidth*.01, screenHeight*.8), 48, screen, spot='midleft')
    text(f'SHOOTER TWO-WAY CURL: {"YES" if Shooter.twowaycurl else "NO"}', (screenWidth*.01, screenHeight*.85), 48, screen, spot='midleft')
    text(f'SHOOTER RISK-TAKING: {round(Shooter.risk, 1)}', (screenWidth*.01, screenHeight*.9), 48, screen, spot='midleft')

def create_scatterplot(df, x_col, y_col, color_col=None):
  """
  Generates a scatterplot from a pandas DataFrame.

  Args:
    df (pd.DataFrame): The DataFrame containing the data.
    x_col (str): The name of the column for the x-axis.
    y_col (str): The name of the column for the y-axis.
    color_col (str, optional): The name of the column to use for color encoding. 
                               Defaults to None.
  """
  plt.figure(figsize=(10, 6))
  sns.scatterplot(data=df, x=x_col, y=y_col, hue=color_col)
  plt.title(f'Scatterplot of {y_col} vs {x_col}')
  plt.xlabel(x_col)
  plt.ylabel(y_col)
  plt.ylim(0, 100)
  plt.yticks(np.arange(0, 100 + 1, 10))
  plt.grid(True)
  plt.show()