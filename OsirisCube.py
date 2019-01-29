# Agenda: =====================================================================#
# x fetch HTML data 'inspect element' style from the trading view speedometer
# x implement interface to choose trading pair
# / implement comprehensive logs including coloured feedback
# / "backtests" to determine profitability
# / implement API buying/selling

# library headers ============================================================#

import keys             # abstract away our keys so we improve security
import datetime;        import time                 # for system clock time
from formatting         import *                    # abstract away esc seqs
from selenium           import webdriver  as web    # for 'inspect element'
import os;              import sys
from binance.client     import Client     as bin    # from python-binance pip

# tokenise url about variable asset
url = [ "https://tradingview.com/embed-widget/technical-analysis/" +
        "?locale=en#%7B%22width%22%3A425%2C%22height%22%3A410%2C%22" + 
        "symbol%22%3A%22COINBASE%3A",

	"USD%22%2C%22interval%22%3A%221m%22%2C%22" + 
	"utm_source%22%3A%22%22%2C%22utm_medium%22%3A%22" + 
	"widget_new%22%2C%22utm_campaign%22%3A%22technical-analysis%22%7D"]

	
def getHTML(assets):
    """
        will get the raw HTML with JavaScript speedometer and return a
        dictionary of format asset, HTML
    """

    # create options object so we can render Firefox invisible
    options = web.FirefoxOptions()
    options.add_argument('-headless')
	
    # establish headless webdriver using Firefox
    driver = web.Firefox(firefox_options=options)

    htmls = dict()
    for asset in assets:
        # Get the speedometer JS straight from its source
        driver.get(url[0] + asset + url[1])

        # Give the webpage time to load
        time.sleep(5)

        # This will get the html after on-load javascript
        html = driver.execute_script("return document.documentElement.innerHTML;")

        htmls[asset] = html

    os.system("TASKKILL /F /IM firefox.exe > /dev/null")

    return htmls


def determineArrow(assets, htmls):
    """
        will search the HTML for keywords and determine the recommendation,
        returning a dictionary of format asset, recommendation
    """

    arrows = dict()

    for asset in assets:
        if "arrowToStrongSell" in htmls[asset]:
            arrows[asset] = "Strong Sell" 
        elif "arrowToSell" in htmls[asset]:
            arrows[asset] = "Sell"
        elif "arrowToNeutral" in htmls[asset]:
            arrows[asset] = "Neutral" 
        elif "arrowToBuy" in htmls[asset]:
            arrows[asset] = "Buy"
        elif "arrowToStrongBuy" in htmls[asset]:
            arrows[asset] = "Strong Buy"
        else:
            arrows[asset] = "Failed"

    return arrows


def getPrice(assets):
    """
        will retrieve the current price of every asset and return a dictionary
        in the form asset, price, using binance API
    """

    price = dict()

    # initialise binance client
    client = bin(keys.APIKey, keys.SecretKey)

    for asset in assets:
        sym = asset + "USDT"
        price[asset] = client.get_order_book(symbol=sym)["bids"][0][0]
    

    return price

# main ========================================================================$

print(INTRO_MSG)

# establish all desired assets
print(CHOICE_MSG + '\n')
assets = []

while True:
    asset = sys.stdin.read()

    if asset == '':
        break
    else:
        if len(asset) == 3:
            print(GRN + " ✓" + CLR)
            assets.append(asset)
        else:
            print(RED + " X" + CLR)

print("\nReading JavaScript...\n") 

# generate table for assets at a time
print("{:-<11}".format(""), end='')
for asset in assets:
    print(BLD + asset + ": " + CLR + "{:-<21}".format(""), end='')

# print live updates on asset recommendations
while True:
    htmls = getHTML(assets)
    arrows = determineArrow(assets, htmls)
    price = getPrice(assets)
    
    # print the time 
    print("\n" + time.strftime("%H:%M:%S | "), end='')

    # print the recommendation for each asset
    for asset in assets:

        # open log file for writing
        f = open("logs/" + asset, "a")

        # colour outputs
        if   "Strong Sell" in arrows[asset]:
            print(RED, end='')
            f.write(RED)
        elif "Strong Buy" in arrows[asset]:
            print(BLU, end='')
            f.write(BLU)
        elif "Sell" in arrows[asset]:
            print(ORG, end='')
            f.write(ORG)
        elif "Buy" in arrows[asset]:
            print(GRN, end='')
            f.write(GRN)
        elif "Neutral" in arrows[asset]:
            print(YEL, end='')
            f.write(YEL)
        else:
            print(WHT, end='')

        print("{0:14s}{1}{2:.8s}  | ".format(arrows[asset], CLR,  price[asset]), end='')
        print(CLR, end='')

        f.write(time.strftime("%H:%M:%S: ") +
                "{0:14s}{1}{2:.8s}\n".format(arrows[asset], CLR, price[asset]))
        
        f.close()
