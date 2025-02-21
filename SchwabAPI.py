#!/Users/jnn/Documents/Trading/Devel/tosenv/bin/python3
import logging
import os
import sys
import json
import requests
import datetime
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from dateutil.relativedelta import relativedelta
from decimal import Decimal

# Setup logging
# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
def setup_logging(logfile="schwab_api.log"):
    logger = logging.getLogger("SchwabAPI")
    logger.setLevel(logging.INFO)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)

    # File Handler with Rotation (5MB max, keep 1 backup)
    file_handler = RotatingFileHandler(logfile, maxBytes=5 * 1024 * 1024, backupCount=1)
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_format)

    # Adding Handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

logger = setup_logging()

class SchwabAPI:
    def __init__(self, token_file, acct_file, base_acct_url, base_data_url):
        logger.debug("Initializing SchwabAPI.")
        self.token_file = token_file
        self.acct_file = acct_file
        self.base_acct_url = base_acct_url
        self.base_data_url = base_data_url
        self.acct_numbers = None
        self.headers = None
        self.positions = None
        self.trades = None
        self.__get_headers()
        logger.info("SchwabAPI initialized.")

    def __get_headers(self):
        if self.headers != None:
            return self.headers

        if os.path.exists(self.token_file):
            logger.debug(f"Loading token from file.")
            with open(f"{self.token_file}", "r") as f:
                token_json = json.load(f)
            bearer_token = token_json['access_token']
            self.headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {bearer_token}",
            }
        else:
            logger.error("Token file not found. Reauthenticate.")
            raise Exception("Token file not found. Reauthenticate.")

    # must call this fn before account queries
    # BUT only need to call it ONCE
    def __get_acct_numbers(self):
        if self.acct_numbers != None:
            return self.acct_numbers

        if os.path.exists(self.acct_file):
            logger.debug(f"Loading account numbers from file.")
            with open(self.acct_file, "r") as f:
                acct_text = f.read()
            self.acct_numbers = json.loads(acct_text)
        else:
            logger.debug(f"Getting new account numbers from API ONCE!")
            response = self.__request("GET", self.base_acct_url, "accounts/accountNumbers")
            logger.debug(f"Writing new account numbers to file.")
            with open(self.acct_file, "w") as f:
                f.write(response.text)
            self.acct_numbers = json.loads(response.text)

    def __request(self, verb, base, path, params=None, data=None):
        # params for GET, data for POST
        url =f"{base}/{path}"
        logger.debug(f"Request URL: {verb} {url}")
        if verb == "GET":
            response = requests.get(f"{url}", headers=self.__get_headers(), params=params)
        elif verb == "POST":
            response = requests.post(f"{url}", headers=self.__get_headers(), data=data)

        if response.status_code != 200:
            logger.error(f"API Error: {response.status_code}: {response.text}")
            raise Exception(f"API Error: {response.status_code}: {response.text}")
        
        return response

    # positions are returned from API for ALL accounts approved 
    # during token authentication. Need to iterate over accounts
    # to get positions by account.
    def get_positions(self):
        self.__get_acct_numbers()
        params = {
            "fields": "positions", #optional, to get positions with balances
        }
        response = self.__request("GET", self.base_acct_url, "accounts", params=params)
        self.positions = json.loads(response.text)
        logger.info("Got balances with positions from API.")

    def parse_symbol(self, symbol):
        ticker = symbol[:6].strip()
        exp = symbol[6:12]
        exp = datetime.datetime.strptime(exp, '%y%m%d')
        exp = datetime.datetime.strftime(exp, '%d-%b-%y')
        otype = "PUT" if symbol[12] == "P" else "CALL"
        strike = Decimal(symbol[13:])/1000
        return {"ticker": ticker,"exp":exp,"otype":otype,"strike":strike}

    def print_positions(self):
        # get updated positions
        self.get_positions()
        symbols = dict() 

        # API returns position information for each account
        for acct in self.positions:
            logger.info(f"Positions for account {acct['securitiesAccount']['accountNumber']}")
            positions = acct['securitiesAccount']['positions']

            # get a dict of option symbols from all position items (input for get_quote)
            for posn in positions:
                if posn['instrument']['assetType'] == "OPTION":
                    symbols[posn['instrument']['symbol']] = [] 
            symbols,underlyings = self.get_quote(symbols)

            # add mark/position data to symbols dict
            # symbols[key=symbol,mark,qty,avg_px,itmotm,days,plopen]
            logger.info("===>>  OPTION positions.")
            print("Ticker,Exp,Strike,Type,Position,AvgPx,Mark,ITMOTM,PLOpen")
            for posn in positions:
                if posn['instrument']['assetType'] != "OPTION":
                    continue
                # parse option API symbol
                symbol = posn['instrument']['symbol']
                parsed_symb = self.parse_symbol(posn['instrument']['symbol'])
                ticker = parsed_symb['ticker']
                strike = parsed_symb['strike']
                exp = parsed_symb['exp']
                otype = parsed_symb['otype']

                # calculate additional information
                upx = underlyings[ticker] # underlying mark
                days = (datetime.datetime.strptime(exp, '%d-%b-%y') - datetime.datetime.today()).days + 1
                itmotm = upx - float(strike) if otype == "CALL" else float(strike) - upx
                qty = posn['longQuantity'] - posn['shortQuantity']
                if qty < 0:
                    itmotm *= -1
                plopen = (qty * 100) * (symbols[symbol][0] - posn['averagePrice'])

                # combine positions with market data
                symbols[symbol].append(qty)
                symbols[symbol].append(posn['averagePrice'])
                symbols[symbol].append(itmotm)
                symbols[symbol].append(days)
                symbols[symbol].append(plopen)
                result = f"{ticker},"
                result += f"{exp},"
                result += f"{strike},"
                result += f"{otype},"
                result += f"{symbols[symbol][1]},"      # qty
                result += f"{symbols[symbol][2]:.3f},"  # avg px
                result += f"{symbols[symbol][0]:.3f},"  # mark
                result += f"{symbols[symbol][3]:.1f},"  # itmotm
                result += f"{symbols[symbol][4]},"      # days
                result += f"{symbols[symbol][5]:.2f}"   # PL Open
                print(result)

            # print underlying quotes
            logger.info("===>>  UNDERLYING positions.")
            print("Ticker,Mark")
            for underlying in underlyings:
                print(f"{underlying},{underlyings[underlying]}")


    def get_quote(self, symbols):
        params = {
            "symbols": symbols,
            "fields": "quote",
        }
        response = self.__request("GET", self.base_data_url, "quotes", params=params)
        quotes = json.loads(response.text)
        underlyings = dict()
        for symbol in symbols:
            symbols[symbol].append(quotes[symbol]['quote']['mark'])
            ticker = symbol[:6].strip()
            if ticker not in underlyings:
                underlyings[ticker] = quotes[symbol]['quote']['underlyingPrice']
        return [symbols,underlyings]

    def get_trades(self, days, account):
        # get the date range for getting transactions
        end = datetime.datetime.today()
        start = end - relativedelta(days=int(days))
        
        # initialize the request parameters
        params = {
            "startDate": f"{start.isoformat()}Z",
            "endDate": f"{end.isoformat()}Z",
            "types": "TRADE",
        }

        path = f"accounts/{account}/transactions"
        response = self.__request("GET", self.base_acct_url, path, params=params)
        self.trades = json.loads(response.text)

    def print_trades(self, days=1):
        self.__get_acct_numbers()

        for acct in self.acct_numbers:
            logger.info(f"Getting trades for account {acct['accountNumber']}")
            self.get_trades(days, acct['hashValue'])
            for tran in self.trades:
                try:
                    xfer_items = tran['transferItems']
                except:
                    logger.error(f"Error with transaction {tran} in account {acct['accountNumber']}")
                    continue
                else:
                    for items in xfer_items:
                        inst = items['instrument']
                        if inst['assetType'] == "OPTION":
                            trd_dt = tran['tradeDate']
                            trd_dt = datetime.datetime.strptime(trd_dt, '%Y-%m-%dT%H:%M:%S%z')
                            result = datetime.datetime.strftime(trd_dt, '%-m/%-d/%y %H:%M')
                            result += f",{items['positionEffect']},"
                            result += f"{self.parse_symbol(inst['symbol'])['ticker']},"
                            result += f"{self.parse_symbol(inst['symbol'])['exp']},"
                            result += f"{self.parse_symbol(inst['symbol'])['strike']},"
                            result += f"{self.parse_symbol(inst['symbol'])['otype']},"
                            result += f"{items['amount']},"
                            result += f"{items['price']:.3f}"
                            print(result)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 1:
        logger.error("Usage: SchwabAPI.py <p,t>")
        sys.exit(-1)

    if args[0].lower() not in ['p','t']:
        logger.error("Usage: SchwabAPI.py <p,t>")
        sys.exit(-1)

    load_dotenv()
    TOKEN_FILE = os.getenv("SCHWAB_TOKEN_FILE")
    ACCT_FILE = os.getenv("SCHWAB_ACCT_FILE")
    BASE_ACCT_URL = "https://api.schwabapi.com/trader/v1"
    BASE_DATA_URL = "https://api.schwabapi.com/marketdata/v1"

    api = SchwabAPI(TOKEN_FILE, ACCT_FILE, BASE_ACCT_URL, BASE_DATA_URL)

    if args[0] == 'p':
        api.print_positions()

    elif args[0] == 't':
        if len(args) > 1:
            api.print_trades(args[1])
        else:
            api.print_trades()

