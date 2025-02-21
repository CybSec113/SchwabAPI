#!/Users/jnn/Documents/Trading/Devel/tosenv/bin/python3
import requests
import sys
import os
import base64
import pyperclip
import json
from dotenv import load_dotenv
from crontab import CronTab

load_dotenv()

# global parameters
api_key = os.getenv("SCHWAB_API_KEY")
api_secret = os.getenv("SCHWAB_API_SECRET")
tokenfile = os.getenv("SCHWAB_TOKEN_FILE")
token_url = "https://api.schwabapi.com/v1/oauth/token"
auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={api_key}&redirect_uri=https://127.0.0.1"

# headers for token POST request
headers = {
    "Authorization": f"Basic {base64.b64encode(bytes(f"{api_key}:{api_secret}", "utf-8")).decode("utf-8")}",
    "Content-Type": "application/x-www-form-urlencoded",
}

def makeRequest(url, payload, verb='post'):
    if verb == "post":
        return requests.post(url=url, headers=headers, data=payload)
    elif verb == "get":
        print("Not implemented, yet!")

def getNewToken():
    # copy url to clipboard: user must authenticate via browser with account (not dev) creds
    pyperclip.copy(auth_url)
    print(f"Authorization URL (copied to clipboard): ")

    # following authentication, browser will return a url with the code; user must copy it here
    print("Enter returned URL:")
    returned_url = input()

    # extract the authentication response code from the url
    response_code = f"{returned_url[returned_url.index('code=')+5: returned_url.index('%40')]}@"

    # payload for token POST request
    payload = {
        "grant_type": "authorization_code",
        "code": response_code,
        "redirect_uri": "https://127.0.0.1"
    }

    # the token POST request
    response = makeRequest(token_url, payload)
    print(response)
    with open(tokenfile, "w") as f:
        f.write(response.text)

def getRefreshToken():
    with open(tokenfile, "r") as f:
        auth_text = f.read()
    auth_json = json.loads(auth_text)

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": auth_json["refresh_token"],
    }

    response = makeRequest(token_url, payload)
    print(response)
    with open(tokenfile, "w") as f:
        f.write(response.text)

def cleanup():
    if os.path.exists("Data/token.json"):
        os.remove("Data/token.json")
    if os.path.exists("Data/account.json"):
        os.remove("Data/account.json")
    print("Deleted token and account files.")
    print("Don't forget to clear crontab!")

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) == 0:
        print("Usage: python auth.py <(N)ew | (R)efresh | (S)et timer>")
        sys.exit(1)

    if args[0].lower() not in ['n', 'r', 'c', 's']:
        print("Usage: python auth.py <(N)ew | (R)efresh | (C)leanup | (S)et timer>")
        sys.exit(1)

    if args[0].lower() == 'n':
        cleanup()
        getNewToken()
    elif args[0].lower() == 'r':
        getRefreshToken()
    elif args[0].lower() == 'c':
        cleanup()
    elif args[0].lower() == 's':
        cron = CronTab(user=True)
        job = cron.new(command="~/Documents/Trading/Devel/auth.py r; say renew")
        job.setall('29,59 * * * *')
        cron.env['MAILTO'] = ''
        cron.write()
