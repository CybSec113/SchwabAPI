import requests
import os
import base64
import pyperclip
from dotenv import load_dotenv

load_dotenv()

# set/get static data
api_key = os.getenv("SCHWAB_API_KEY")
api_secret = os.getenv("SCHWAB_API_SECRET")
auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={api_key}&redirect_url=https://127.0.0.1"
pyperclip.copy(auth_url)

# authorization requires logging in with standard (i.e., not developer) credentials in browser
print(f"Authorization URL (copied to clipboard): {auth_url}")

# browser will return a url with the code; user must copy it here
print("Enter returned URL:")
returned_url = input()

# extract the authentication response code from the url
response_code = f"{returned_url[returned_url.index('code=')+5: returned_url.index('%40')]}@"

# urlencode to base64
creds = f"{api_key}:{api_secret}"
b64_creds = base64.b64encode(creds.encode("utf-8")).decode("utf-8")

# headers for token POST request
headers = {
    "Authorization": f"Basic {b64_creds}",
    "Content-Type": "application/x-www-form-urlencoded",
}

# payload for token POST request
payload = {
    "grant_type": "authorization_code",
    "code": response_code,
    "redirect_uri": "https://127.0.0.1"
}

# the toke POST request
response = requests.post(
    url="https://api.schwabapi.com/v1/oauth/token",
    headers=headers,
    data=payload,
)

tokens_dict = response.json()