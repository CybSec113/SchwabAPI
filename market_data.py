import requests
import datetime
import time

server="https://api.schwabapi.com/marketdata/v1"

headers={
    "accept": "application/json",
    "Authorization": "Bearer I0.b2F1dGgyLmNkYy5zY2h3YWIuY29t.OPBdCNmLXMxsKIzfJV25SPDRiZNnexlQu5ZacdFJ3lE@",
}

def get_quote(symbol):
    response = requests.get(f"{server}/{symbol}/quotes", headers=headers)

    print(response)
    print(response.text)
    mark_index=response.text.index("mark")
    mark=f"{response.text[mark_index+6:response.text.index(",", mark_index)]}"
    print(f"Mark: {mark}")

def get_history(symbol):
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

    response = requests.get(f"{server}/pricehistory", headers=headers, params=payload)
    print(response)
    print(response.text)


if __name__ == "__main__":
    #get_quote('C')
    get_history('C')