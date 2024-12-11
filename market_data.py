import requests
import datetime
import time
import json

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

def getQuote(symbol):
    # optional payload values: quote, fundamental, extended, reference, regular
    # omitting payload returns full response.
    payload = {
        "fields": "quote"
    }
    response = requests.get(f"{server}/{symbol}/quotes", headers=getHeaders(), params=payload)
    print(response)
    with open("quote.json", "w") as f:
        f.write(response.text)
    print(json.dumps(response.json(), indent=4))

def getHistory(symbol):
    start_date=datetime.date(2024,10,1)
    end_date=datetime.date(2024,10,31)

    payload={
        "symbol": f"{symbol}",
        "periodType": "month",
        "period": 1,
        "frequencyType": "weekly",
        "frequency": 1,
        "startDate": int(time.mktime(start_date.timetuple())*1e3),
        "endDate": int(time.mktime(end_date.timetuple())*1e3),
        "needExtendedHoursData": False,
        "needPreviousClose": False,
    }

    response = requests.get(f"{server}/pricehistory", headers=getHeaders(), params=payload)
    with open("history.json", "w") as f:
        f.write(response.text)

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
    symbol = input("Symbol:")
    getQuote(symbol)
    #getHistory(symbol)
    #getChains(symbol)