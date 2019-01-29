# messages and escape sequences ==============================================#

GRN = '\033[00;92m'
BLU = '\033[00;94m'
ORG = '\033[00;38;5;215m'
RED = '\033[00;91m'
WHT = '\033[00;01m'
CLR = '\033[00;00m'
YEL = '\033[00;38;5;226m'
LIM = '\033[00;38;5;190m'
TEL = '\033[00;38;5;30m'
UND = '\033[4m'
BLD = '\033[1m'

INTRO_MSG   =   ("\n{0}OsirisCube: {1}Prints TradingView recommendation " +
                 "for pairs through HTML fetching{2}\n").format(WHT, YEL, CLR)

CHOICE_MSG  =   ("Enter the name of the desired assets, i.e. ETH, BTC, LTC \n" +
                 "and confirm selection using CTRL+D twice:")
