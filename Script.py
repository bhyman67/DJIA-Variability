# i want to analyze the variability of the DJIA over the past year...

# https://www.investopedia.com/investing/what-moves-the-djia/

# include percentages
# go back further but filter out the bad data... why is it bad???
 
import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import sys
import os


def right(x,num):

    return x[-num:]

# ******************************************************************************
# Retrieve all constituents (companies) that make up the DOW from this website:
#   -> https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average
# ******************************************************************************

# Scrape table from web
elmtAttrs = {'id':'constituents'}
url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
resp = requests.get(url)
soup = BeautifulSoup(resp.content,'lxml')
table = soup.find('table',elmtAttrs)
df = pd.read_html(str(table))[0]
symbols = list(df['Symbol'])

# Extract the ticker symbols
for index, symbol in enumerate(symbols):

    # cut out the unicode: https://stackoverflow.com/questions/10993612/python-removing-xa0-from-string
    symbols[index] = symbol.replace(u'\xa0', u'') # what does u indicate in the string???

    # ..
    strList = symbol.split(':')
    if len(strList) > 1:
        symbols[index] = strList[-1].strip()

companyList = symbols

# ***********************************
# API call to alpaca for market data
# ***********************************

# Retrieve needed data
api = tradeapi.REST()
barset = api.get_barset(companyList, 'day', 194, '2020-03-06')
dFrameList = []
for tickerSymbol in companyList:
    dFrame = barset[tickerSymbol].df
    dFrame['Ticker Symbol'] = tickerSymbol
    dFrameList.append(dFrame)
dFrame = pd.concat(dFrameList)

# convert index into col
dFrame.reset_index(inplace=True)

# aggregate data
dowDivisor =  0.14744568353097
x = dFrame.groupby('time')['close'].sum()/dowDivisor

# calculate the change over time
df = pd.DataFrame(x)
df.reset_index(inplace=True)
df = df.sort_values('time', ascending = False)
df['change'] = df.close.diff(-1)
df['time'] = df['time'].apply(lambda x: x.date())
df.to_excel('output.xlsx')

# ***************************************
# Build the plot and save it off the plot
# ***************************************

# need to find a way to set the dimensions...

# https://uproer.com/articles/image-size-calculator-px-in/
plt.figure(
    figsize=(34.133,12.65),
    dpi=75
)
plt.bar(df.time.values, df.change.values)
plt.savefig("DJIA_Variability_Plot.png")

print('done')