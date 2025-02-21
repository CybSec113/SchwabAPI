#!/Users/jnn/Documents/Trading/Devel/tosenv/bin/python3
import requests
import json
import os
import sys
import datetime
import pandas as pd
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta
from market_data import getQuote
from option_tickers import fromAPITickers

load_dotenv()
tokenfile = os.getenv("SCHWAB_TOKEN_FILE")
server="https://api.schwabapi.com/trader/v1"

def getHeaders():
    with open(tokenfile, "r") as f:
        auth_text = f.read()
    auth_json = json.loads(auth_text)
    bearer_token = auth_json["access_token"]
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
    }
    return headers

def getAccountNumbers():
    response = requests.get(f"{server}/accounts/accountNumbers", headers=getHeaders())
    print(response)
    account_json = json.loads(response.text)
    with open("Data/account.json", "w") as f:
        f.write(response.text)
    f.close()

def getUserPrefs():
    response = requests.get(f"{server}/userPreference", headers=getHeaders())
    print(response)
    prefs_json = json.loads(response.text)
    with open("Data/prefs.json", "w") as f:
        f.write(response.text)
    f.close()

def getAccountBal(get_posns=True, acct_num=""):
    payload = {
        "fields": "positions",  # optional field, only one value
    }

    if get_posns:
        response = requests.get(f"{server}/accounts", headers=getHeaders(), params=payload)
    else:
        response = requests.get(f"{server}/accounts", headers=getHeaders())
    print("balance:", response)
    account_json = json.loads(response.text)
    # helpful to see json format, but not needed to run
    #with open("Data/balances.json", "w") as f:
    #    f.write(response.text)
    #f.close()

    for acct in account_json:
        if get_posns:
            try:
                posns = acct['securitiesAccount']['positions']
            except:
                print(f"Account {acct['securitiesAccount']['accountNumber']} has no positions.")
                print("==============================")
                continue
            else:
                print(f"Type,{acct['securitiesAccount']['type']}")
                print(f"Account,{acct['securitiesAccount']['accountNumber']}")
                print(f"Liq Val,{acct['securitiesAccount']['currentBalances']['liquidationValue']}")
                print(f"Current Liq Val,{acct['aggregatedBalance']['currentLiquidationValue']}")
                print(f"Buying Power,{acct['securitiesAccount']['currentBalances']['buyingPower']}")
                print(f"Margin Bal,{acct['securitiesAccount']['currentBalances']['marginBalance']}")
                print(f"Cash Bal,{acct['securitiesAccount']['currentBalances']['cashBalance']}")
                print(f"Long Mkt Val,{acct['securitiesAccount']['currentBalances']['longMarketValue']}")
                print("OPTION POSITIONS")
                result = ["Options"]
                for position in posns:
                    if position['instrument']['assetType'] != "OPTION":
                        continue
                    pos_amnt = position['longQuantity'] - position['shortQuantity']
                    result.append(f"{position['instrument']['symbol']},{pos_amnt},{position['averagePrice']}")
                getQuote("optpos.txt", result) 
                print("==============================")


def getTransactions():
    with open("Data/account.json", "r") as f:
        acct = f.read()
    f.close()
    acct_json = json.loads(acct)

    end = datetime.datetime.today()
    start = end - relativedelta(days=1)

    payload = {
        "startDate": f"{start.isoformat()}Z",
        "endDate": f"{end.isoformat()}Z",
        # "symbol": "AAPL", # optional
        "types": "TRADE",
    }

    for acct in acct_json:
        response = requests.get(f"{server}/accounts/{acct['hashValue']}/transactions", headers=getHeaders(), params=payload) 
        print("transactions:", response)
        xaction_json = json.loads(response.text)
        #with open("Data/xactions.json", "w") as f:
        #    f.write(response.text)
        #f.close()

        print("TradeDt,PosEffect,Symbol,Exp,Strike,Type,Qty,TradePx")
        for xaction in xaction_json:
            try:
                xfer_items = xaction['transferItems']
            except:
                continue
            else:
                for items in xfer_items:
                    inst = items['instrument']
                    if inst['assetType'] == "OPTION":
                        trd_date = xaction['tradeDate']
                        trd_date = datetime.datetime.strptime(trd_date, '%Y-%m-%dT%H:%M:%S%z')
                        output = datetime.datetime.strftime(trd_date, '%-m/%-d/%y %H:%M')
                        output += f",{items['positionEffect']},"
                        output += fromAPITickers(inst['symbol'])
                        output += f",{items['amount']}"
                        output += f",{items['price']}"
                        print(output)


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python account_data.py <b | h | n | t | u>")
        sys.exit(1)

    if args[0].lower() not in ['b', 'h', 'n', 't', 'u']:
        print("Usage: python account_data.py <b | h | n | t | u>")
        sys.exit(1)

    if args[0].lower() == 'b':
        getAccountBal()
    
    if args[0].lower() == 'n':
        getAccountNumbers()

    if args[0].lower() == 't':
        getTransactions()
    
    if args[0].lower() == 'u':
        getUserPrefs()
    
    if args[0].lower() == 'h':
        print("Help:")
        print("b: Get account balances and positions for all accounts")
        print("n: Get account numbers (do this first/once. Saved to account.json)")
        print("t: Get positions")
        print("u: Get user preferences")
        print("h: Help")
        sys.exit(0)