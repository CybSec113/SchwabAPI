## Assumptions  
1. Schwab (individual) developer account activated and API request FULLY approved
2. python3 installed
3. some familiarity with venv  
4. some familiarity with HTTP post and get requests

## Requirements  
1. Python 3.13.0
2. following python modules:
   1. requests
   2. ouathlib
   2. pyperclip
   3. dotenv
   4. python-crontab

## Authentication    
### oauth2 features  
1. no coding/transmission of username/password
2. user authentication takes place through 'normal' Schwab browser login (e.g., HTTPS)
3. api key, api secret, and tokens replace 'standard' username/login authentication method
4. tokens (not api keys or api secrets) expire in 30 minutes

## Workflow  
1. use api key and api secret to get an initial 'bearer' token
2. later on, bearer token is included with API calls - this is how schwab knows it's you!
3. since tokens expire every 30 minutes, we need to actively 'refresh' the token. This save us from having to re-authenticate on Schwab.com with username/password.

## Setup  
1. there A LOT of secrets required for authentication that should NEVER be hardcoded in ANY code file.  
   1. I will use env variables for api key and api secret  
   2. I will use a token.json file for tokens  
2. If syncing with GitHub (I am), make absolutely CERTAIN to add a gitignore file that excludes any env and token.json files
