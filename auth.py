import requests
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
    with open("token.json", "w") as f:
        f.write(response.text)

def getRefreshToken():
    with open("token.json", "r") as f:
        auth_text = f.read()
    auth_json = json.loads(auth_text)

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": auth_json["refresh_token"],
    }

    response = makeRequest(token_url, payload)
    print(response)
    with open("token.json", "w") as f:
        f.write(response.text)

if __name__ == "__main__":
    print("1 - New token")
    print("2 - Refresh token")
    print("3 - Set token timer")
    command = input("Selection: ")

    if command == '1':
        getNewToken()
    elif command == '2':
        getRefreshToken()
    elif command == '3':
        cron = CronTab(user=True)
        cron.remove_all()
        cron.write()
        job = cron.new(command="say 'token'")
        job.setall('29,59 * * * *')
        cron.write()