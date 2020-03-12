# i want to analyze the variability of the DJIA over the past year...

# https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average
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


elmtAttrs = {'id':'constituents'}
url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'

resp = requests.get(url)
soup = BeautifulSoup(resp.content,'lxml')
table = soup.find('table',elmtAttrs)
df = pd.read_html(str(table))[0]
symbols = list(df['Symbol'])

# Extract the ticker sybols
for index, symbol in enumerate(symbols):

    # cut out the unicode: https://stackoverflow.com/questions/10993612/python-removing-xa0-from-string
    symbols[index] = symbol.replace(u'\xa0', u'') # what does u indicate in the string???

    # ..
    strList = symbol.split(':')
    if len(strList) > 1:
        symbols[index] = strList[-1].strip()

companyList = symbols

api = tradeapi.REST()
barset = api.get_barset(companyList, 'day', 194, '2020-03-06')

# Retrieve needed data
dFrameList = []
for tickerSymbol in companyList:
    dFrame = barset[tickerSymbol].df
    dFrame['Ticker Symbol'] = tickerSymbol
    dFrameList.append(dFrame)
dFrame = pd.concat(dFrameList)
print(dFrame)

# convert index into col
dFrame.reset_index(inplace=True)

dowDivisor =  0.14744568353097
x = dFrame.groupby('time')['close'].sum()/dowDivisor

df = pd.DataFrame(x)
df.reset_index(inplace=True)
df = df.sort_values('time', ascending = False)
df['change'] = df.close.diff(-1)
df['time'] = df['time'].apply(lambda x: x.date())
df.to_excel('output.xlsx')

plt.bar(df.time.values, df.change.values)
plt.show()

print('done')