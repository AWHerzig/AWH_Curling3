from PlayerMovement import *

class HANDLER:
    def __init__(self):
        self.YEAR = 1
        self.RESULTS = pd.DataFrame(columns = ['YEAR', 'COMPETITION', 'STAGE', 'Home', 'HomeScore', 'AwayScore', 'Away', 'ExtraEnd'])
        self.WorldCup = None
        self.WCQ = {
            'Europe': None,
            'Asia': None,
            'Americas': None,
            'MEA': None
        }
        self.CL = {
            'Europe': None,
            'Asia': None,
            'Americas': None,
            'MEA': None
        }