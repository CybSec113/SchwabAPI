#!/Users/jnn/Documents/Trading/Devel/tosenv/bin/python3
import requests
import sys
import datetime
import time
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from dateutil.relativedelta import relativedelta
from decimal import Decimal

server="https://api.schwabapi.com/marketdata/v1"

def getHeaders():
    with open("Data/token.json", "r") as f:
        auth_text = f.read()
    auth_json = json.loads(auth_text)
    bearer_token = auth_json["access_token"]
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
    }
    return headers

def getQuote(filename, rows):
    # optional payload values: quote, fundamental, extended, reference, regular
    # omitting payload returns full response.

    security = rows[0]
    rows = rows[1:]
    symbols = [row.split(',')[0] for row in rows]

    payload = {
        "symbols": symbols,
        "fields": "quote"
    }

    response = requests.get(f"{server}/quotes", headers=getHeaders(), params=payload)
    print(response)
    quote = json.loads(response.text)
    # writes to file to learn json structure
    #filename = filename.split('.')[0]
    #with open(f"Data/{filename}.json", "w") as f:
    #   f.write(response.text)
    #f.close()

    prem = dict()      # underlying prices for options
    itmotm = 0.0        # in the money or out of the money

    if security == 'Stocks':
        print("Ticker,Mark")
        for ticker in symbols:
            mark = quote[ticker]['quote']['mark']
            print(f"{ticker},{mark}")
    elif security == 'Options':
        print(f"Ticker,Exp,Strike,Type,Position,TradePx,Mark,ITMOTM,Days,PLOpen")
        for option in rows:
            symbol = option.split(',')[0]
            position = Decimal(option.split(',')[1])
            ticker = symbol[:6].strip()
            exp = symbol[6:12]
            otype = 'PUT' if symbol[12] == 'P' else 'CALL'
            strike = Decimal(symbol[13:])/1000
            tradepx = Decimal(option.split(',')[2])
            if ticker not in prem:
                underpx = quote[symbol]['quote']['underlyingPrice']
                prem[ticker] = underpx
            itmotm = prem[ticker] - float(strike) if otype == 'CALL' else float(strike) - prem[ticker]
            if position < 0:
                itmotm *= -1
            exp = datetime.datetime.strptime(exp, '%y%m%d')
            days = (exp - datetime.datetime.now()).days + 1
            exp = datetime.datetime.strftime(exp, '%d-%b-%y')
            mark = Decimal(quote[symbol]['quote']['mark'])
            plopen = (position * 100) * (mark - tradepx)
            print(f"{ticker},{exp},{strike},{otype},{position},{tradepx:.3f},{mark:.3f},{itmotm:.3f},{days},{plopen:.2f}")
        prem = sorted(prem.items())
        prem = dict(prem)
        print("Ticker,Mark")
        for t in prem:
            print(f"{t},{prem[t]}")

def getHistory(symbol):
    start_date=datetime.date(2023,12,17)
    end_date=datetime.date(2024,12,20)
    #start_date = datetime.datetime.now() - relativedelta(years=1)
    #end_date = datetime.datetime.now()

    payload={
        "symbol": f"{symbol}",
        "periodType": "year",
        "period": 1,
        "frequencyType": "daily",
        #"frequency": 1,
        #"startDate": int(time.mktime(start_date.timetuple())*1e3),
        #"endDate": int(time.mktime(end_date.timetuple())*1e3),
        #"needExtendedHoursData": False,
        #"needPreviousClose": False,
    }

    # get data from request or from pickle file
    # request: 
    response = requests.get(f"{server}/pricehistory", headers=getHeaders(), params=payload)
    with open("Data/history.json", "w") as f:
        f.write(response.text)
    history = json.loads(response.text)
    history_df = pd.json_normalize(history["candles"])

    # pickle file:
    #history_df = pd.read_pickle('history.pkl')

    # start manipulating data
    history_df['date'] = pd.to_datetime(history_df['datetime'],unit='ms', origin='unix').dt.date
    history_df['pctchng'] = history_df['close'].pct_change()
    history_df['logpctchng'] = np.log(history_df['close']/history_df['close'].shift(1))
    #history_df.to_pickle('history.pkl')

    # standard deviation
    sd = history_df['pctchng'].std()
    logsd = history_df['logpctchng'].std()
    print(history_df[['date','close','logpctchng']].tail())
    print(f"Count: {history_df['logpctchng'].count()}")
    print(f"StdDev: {logsd:.6f}")
    print(f"Annualized StdDev: {logsd*math.sqrt(history_df['logpctchng'].count()-1):.6f}")

    # plot
    #history_df.plot(x='date', y='close', kind='line', title='History')
    #plt.show()

def getChains(symbol):
    payload = {
        "symbol": symbol,
        "contractType": "PUT",              # CALL, PUT, ALL
        #"strikeCount": 10,                  # num of strikes above/below ATM
        "includeUnderlyingQuote": False,
        "strategy": "SINGLE",               # SINGLE (default), ANALYTICAL, COVERED, VERTICAL, CALENDAR
                                            # STRANGLE, STRADDLE, BUTTERFLY, CONDOR, DIAGONAL, COLLAR, ROLL
                                            # ANALYTICAL requires additional fields not included here
        #"interval": 5.0,                    # strike interval for strategy chains
        #"strike": 115.0,
        #"range": "NTM",                     # ITM, NTM (near the money), OTM
        #"fromDate": "2024-01-01",
        #"toDate": "2024-03-01",
        #"expMonth": "JAN",                  # JAN, FEB, etc...
        #"optionType": "",                   # not documented
    }
    response = requests.get(f"{server}/chains", headers=getHeaders(), params=payload)
    with open("Data/chains.json", "w") as f:
        f.write(response.text)
    print(json.dumps(response.json(), indent=4))

def getMovers():
    return

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) < 2:
        print("Usage: python market_data.py <(Q)uote | (H)istory | (C)hains | (M)overs> <filename | symbol>")
        sys.exit(1)

    if args[0].lower() not in ['q', 'h', 'c', 'm']:
        print("Usage: python market_data.py <(Q)uote | (H)istory | (C)hains | (M)overs> <filename | symbol>")
        sys.exit(1)

    if args[0].lower() == 'q':
        filename = args[1]
        with open(filename, 'r') as f:
            rows = f.readlines()
            rows = [row.strip() for row in rows if row[0] != '#']
        f.close()
        getQuote(filename, rows)
    
    if args[0].lower() == 'h':
        symbol = args[1]
        getHistory(symbol)

    if args[0].lower() == 'c':
        print("chains not implemented, yet!")
        #getChains(symbol)

    if args[0].lower() == 'm':
        print("movers not implemented, yet!")
        #getMovers()
