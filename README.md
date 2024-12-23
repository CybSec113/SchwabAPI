## Schwab API
Code to authenticate and access Schwab API
Currently only supports individual developer role and Market Data API

See the YouTube video here:
https://youtu.be/vnXVsJuI6ns

## auth.py  
usage: `python auth.py <(N)ew | (R)efresh | (S)et timer>`  

**New**: gets a new token, including website authentication  
**Refresh**: refreshes current token, no website authentication required  
**Set timer**: creates a `crontab` job reminder to renew token at 2d9 and 59 minutes past the hour (first token may be shorter than 30 minutes, but no harm)  

## option_tickers.py  
Usage: `python option_tickers.py <(T)o API | (F)rom API> <filename>`  

**To API**: formats option info into API ticker format (copy info from tos excel export (i.e., tab delimited))  
* **filename**: format: `DIS<tab>17-Jan-25<tab>114<tab>PUT`  

**From API**: not really used independently, but serves as a testbed for code used in `market_data.py` to output appropriate ticker format from quote  
* **filename**: format: `DIS___250117P00114000` (`_` = space)  

## market_data.py  
Usage: `python market_data.py <(Q)uote | (H)istory | (C)hains> <filename>`  

**Quote**: "quote" API call, takes a list of tickers formatted for API.  
* **filename**: First row should include "Stocks" or "Options", as appropriate.  This helps format output correctly for copy/paste to excel (i.e., comma delimited)  
 
**History**: Not implemented, yet.  
**Chains**: Not implemented, yet.  

## Requirements  
`Python 3.13.0`  
`pip freeze`  
charset-normalizer==3.4.0  
idna==3.10  
oauthlib==3.2.2  
pyperclip==1.9.0  
python-crontab==3.2.0  
python-dateutil==2.9.0.post0  
python-dotenv==1.0.1  
requests==2.32.3  
requests-oauthlib==2.0.0  
six==1.17.0  
urllib3==2.2.3  
