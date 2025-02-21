#!/Users/jnn/Documents/Trading/Devel/tosenv/bin/python3
import sys
import datetime
from decimal import Decimal

def toAPITickers(options):
    print("Options")
    for option in options:
        if len(option) == 0:
            continue
        ticker = option.split('\t')[0]
        exp = option.split('\t')[1]
        strike = option.split('\t')[2]
        otype = option.split('\t')[3]
        day = exp.split('-')[0]
        month = exp.split('-')[1]
        year = exp.split('-')[2]
        position = option.split('\t')[4]
        tradepx = option.split('\t')[5]
        exp = datetime.datetime.strptime(exp, '%d-%b-%y')
        exp = datetime.datetime.strftime(exp, '%y%m%d')
        oticker = f"{ticker:<6}{exp}{otype[0]}{Decimal(strike):09.3f},{position},{tradepx}"
        oticker = oticker.replace('.', '', 1)
        print(oticker)

def fromAPITickers(oticker):
    result = ""
    ticker = oticker[:6].strip()
    exp = oticker[6:12]
    otype = 'PUT' if oticker[12] == 'P' else 'CALL'
    strike = Decimal(oticker[13:])/1000
    exp = datetime.datetime.strptime(exp, '%y%m%d')
    exp = datetime.datetime.strftime(exp, '%d-%b-%y')
    result = f"{ticker},{exp},{strike},{otype}"
    return result

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python option_tickers.py <(T)o API | (F)rom API> <filename>")
        sys.exit(1)

    if args[0].lower() not in ['t', 'f']:
        print("Usage: python option_tickers.py <(T)o API | (F)rom API> <filename>")
        sys.exit(1)

    if args[0].lower() == 't':
        filename = args[1]
        with open(filename, 'r') as f:
            options = f.readlines()
        f.close()
        options = [option.strip() for option in options if option[0] != '#']
        toAPITickers(options)

    if args[0].lower() == 'f':
        filename = args[1]
        with open(filename, 'r') as f:
            otickers = f.readlines()
        f.close()
        otickers = [oticker.strip() for oticker in otickers if oticker[0] != '#']
        for ticker in otickers:
            print(fromAPITickers(ticker))