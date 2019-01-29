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
from collections        import defaultdict          # for dict of lists

# tokenise url about variable asset
url = [ "https://s.tradingview.com/embed-widget/technical-analysis/" + 
        "?locale=en#%7B%22width%22%3A425%2C%22height%22%3A410%2C%22" +
        "symbol%22%3A%22BINANCE%3A",
        
        "BTC%22%2C%22interval%22%3A%221m%22%2C%22" +
        "utm_source%22%3A%22www.tradingview.com%22%2C%22" +
        "utm_medium%22%3A%22widget_new%22%2C%22utm_campaign%22%3A%22" +
        "technical-analysis%22%7D" ]
        
# url = [ "https://tradingview.com/embed-widget/technical-analysis/" +
#         "?locale=en#%7B%22width%22%3A425%2C%22height%22%3A410%2C%22" + 
#         "symbol%22%3A%22BINANCE%3A",
# 
# 	"USD%22%2C%22interval%22%3A%221m%22%2C%22" + 
# 	"utm_source%22%3A%22%22%2C%22utm_medium%22%3A%22" + 
# 	"widget_new%22%2C%22utm_campaign%22%3A%22technical-analysis%22%7D"]

	
def getHTML(assets):
    """
        will get the raw HTML with JavaScript speedometer and return a
        dictionary of format asset, HTML
    """

    # create options object so we can render Firefox invisible
    options = web.FirefoxOptions()
    options.add_argument('-headless')
	
    htmls = dict()

    for asset in assets:
        # establish headless webdriver using Firefox
        driver = web.Firefox(firefox_options=options)

        # get the speedometer JS straight from its source
        driver.get(url[0] + asset + url[1])

        # give the webpage time to load
        time.sleep(5)

        # this will get the html after on-load javascript
        html = driver.execute_script("return document.documentElement.innerHTML;")

        # store html
        htmls[asset] = html

        ### write html to a log
        # f = open("logs/" + asset + ".html", "w")
        # f.write(html)
        # f.close()

        driver.close()

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

    price = defaultdict(list)

    # initialise binance client
    client = bin(keys.APIKey, keys.SecretKey)

    for asset in assets:
        sym = asset + "BTC"

        # store price as a list, ask price and bid price
        price[asset].append(client.get_order_book(symbol=sym)["bids"][0][0])
        price[asset].append(client.get_order_book(symbol=sym)["asks"][0][0])
    

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
    print(BLD + asset + ": " + CLR + "{:-<23}".format(""), end='')

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
        f.write(WHT + time.strftime("%H:%M:%S:  "))

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

        # print "Strong Buy 0.123456  | "
        print("{0:14s}{1}{2:.10s}  | ".format(arrows[asset], CLR, price[asset][ASK]), end='')

        # write to log "06:00:00: Strong Buy  Ask: 0.123456  Bid: 0.123456"
        f.write("{0:14s}{1} Ask: {2:.10s} Bid: {3:.10s}\n".format(arrows[asset], CLR,
            price[asset][ASK], price[asset][BID]))
        f.close()
