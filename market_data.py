import requests
import sys
import datetime
import time
import json
import pandas as pd
import matplotlib.pyplot as plt
import math
from dateutil.relativedelta import relativedelta
from decimal import Decimal

server="https://api.schwabapi.com/marketdata/v1"

def getHeaders():
    with open("token.json", "r") as f:
        auth_text = f.read()
    auth_json = json.loads(auth_text)
    bearer_token = auth_json["access_token"]
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
    }
    return headers

def getQuote(filename, symbols):
    # optional payload values: quote, fundamental, extended, reference, regular
    # omitting payload returns full response.

    security = symbols[0]
    symbols = symbols[1:]

    payload = {
        "symbols": symbols,
        "fields": "quote"
    }

    response = requests.get(f"{server}/quotes", headers=getHeaders(), params=payload)
    print(response)
    quote = json.loads(response.text)
    filename = filename.split('.')[0]
    with open(f"{filename}.json", "w") as f:
       f.write(response.text)
    f.close()

    if security == 'Stocks':
        for ticker in symbols:
            print(f"{ticker}: {quote[ticker]['quote']['mark']}")
    elif security == 'Options':
        for oticker in symbols:
            ticker = oticker[:6].strip()
            exp = oticker[6:12]
            otype = 'PUT' if oticker[12] == 'P' else 'CALL'
            strike = Decimal(oticker[13:])/1000
            exp = datetime.datetime.strptime(exp, '%y%m%d')
            exp = datetime.datetime.strftime(exp, '%d-%b-%y')
            print(f"{ticker},{exp},{strike},{otype},{quote[oticker]['quote']['mark']}")

def getHistory(symbol):
    #start_date=datetime.date(2024,10,1)
    #end_date=datetime.date(2024,10,31)
    lookback = 1 #year
    start_date = datetime.datetime.now() - relativedelta(years=lookback)
    end_date = datetime.datetime.now()

    payload={
        "symbol": f"{symbol}",
        "periodType": "year",
        "period": lookback,
        "frequencyType": "daily",
        "frequency": 1,
        "startDate": int(time.mktime(start_date.timetuple())*1e3),
        "endDate": int(time.mktime(end_date.timetuple())*1e3),
        "needExtendedHoursData": False,
        "needPreviousClose": False,
    }

    # get data from request or from pickle file
    # request: 
    #response = requests.get(f"{server}/pricehistory", headers=getHeaders(), params=payload)
    #with open("history.json", "w") as f:
    #    f.write(response.text)
    #history = json.loads(response.text)
    #history_df = pd.json_normalize(history["candles"])

    # pickle file:
    history_df = pd.read_pickle('history.pkl')

    # start manipulating data
    history_df['date'] = pd.to_datetime(history_df['datetime'],unit='ms', origin='unix').dt.date
    history_df['pctchng'] = history_df['close'].pct_change()
    #history_df.to_pickle('history.pkl')

    # standard deviation
    print(history_df['close'].tail())
    stddev = history_df['pctchng'].std()
    print(f"Count: {history_df['pctchng'].count()}")
    print(f"Annualized StdDev: {stddev*math.sqrt(history_df['pctchng'].count()):.4f}")

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
    with open("chains.json", "w") as f:
        f.write(response.text)
    print(json.dumps(response.json(), indent=4))

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) < 2:
        print("Usage: python market_data.py <(Q)uote | (H)istory | (C)hains> <filename | symbol>")
        sys.exit(1)

    if args[0].lower() not in ['q', 'h', 'c']:
        print("Usage: python market_data.py <(Q)uote | (H)istory | (C)hains> <filename | symbol>")
        sys.exit(1)

    if args[0].lower() == 'q':
        filename = args[1]
        with open(filename, 'r') as f:
            symbols = f.readlines()
            symbols = [symbol.strip() for symbol in symbols if symbol[0] != '#']
        f.close()
        getQuote(filename, symbols)
    
    if args[0].lower() == 'h':
        symbol = args[1]
        getHistory(symbol)

    if args[0].lower() == 'c':
        print("chains not implemented, yet!")
        #getChains(symbol)