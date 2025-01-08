#!~/Documents/Trading/Devel/tosenv/bin/python3
import requests
import json
import os
import sys
import datetime
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

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

def getAccountBal():
    payload = {
        "fields": "positions",  # optional field, only one value
    }

    response = requests.get(f"{server}/accounts", headers=getHeaders())
    print(response)
    account_json = json.loads(response.text)
    #print(json.dumps(response.json(), indent=4))
    with open("Data/balances.json", "w") as f:
        f.write(response.text)
    f.close()

    print(f"Account,{account_json[0]['securitiesAccount']['accountNumber']}")
    print(f"Type,{account_json[0]['securitiesAccount']['type']}")
    print(f"Cash Bal,{account_json[0]['securitiesAccount']['currentBalances']['cashBalance']}")
    print(f"Liq Val,{account_json[0]['securitiesAccount']['currentBalances']['liquidationValue']}")
    print(f"Buying Power,{account_json[0]['securitiesAccount']['currentBalances']['buyingPower']}")
    print(f"Current Liq Val,{account_json[0]['aggregatedBalance']['currentLiquidationValue']}")

def getTransactions():
    with open("Data/account.json", "r") as f:
        accountNum = f.read()
    f.close()
    accountNum_json = json.loads(accountNum)

    start_date = datetime.datetime.now() - relativedelta(days=3)
    end_date = datetime.datetime.now()

    payload = {
        "startDate": f"{start_date.isoformat()}Z",
        "endDate": f"{end_date.isoformat()}Z",
        # "symbol": "AAPL", # optional
        "types": "TRADE",
    }

    response = requests.get(f"{server}/accounts/{accountNum_json[0]['hashValue']}/transactions", headers=getHeaders(), params=payload) 
    print(response)
    transaction_json = json.loads(response.text)
    with open("Data/xactions.json", "w") as f:
        f.write(response.text)
    f.close()

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python account_data.py <b | h | n | t | p>")
        sys.exit(1)

    if args[0].lower() not in ['b', 'h', 'n', 't', 'p']:
        print("Usage: python account_data.py <b | h | n | t | p>")
        sys.exit(1)

    if args[0].lower() == 'b':
        getAccountBal()
    
    if args[0].lower() == 'n':
        getAccountNumbers()

    if args[0].lower() == 't':
        getTransactions()
    
    if args[0].lower() == 'p':
        getUserPrefs()
    
    if args[0].lower() == 'h':
        print("Help:")
        print("b: Get account balances")
        print("n: Get account numbers (do this first/once. Saved to account.json)")
        print("t: Get transactions")
        print("p: Get user preferences")
        print("h: Help")
        sys.exit(0)