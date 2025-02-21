## Schwab API
Code to authenticate and query Schwab API
Currently only supports individual developer role for Account and Market Data API
All scripts now include "shebang" to allow for direct execution.

See the YouTube video here (admittedly, this needs to be updated):  
https://youtu.be/vnXVsJuI6ns

I made lots of enhancements since uploading the video, so check back here for more updated code
and functionality.

All scripts have `shebang` line at the top, but user must check location of Python venv for it to
work properly. User must also ensure executable permissions on script files.

## SchwabAPI.py (UPDATE!!)
Usage: `SchwabAPI.py <(P)ositions | (T)rades [days back]>`  
Note: Must run auth.py to manage tokens.  

Queries Schwab API for account and market data, and combines output for monitoring OPTION positions.
For example, I added current mark, ITMOTM, Days (to maturity), and PLOpen to the OPTION position records.
I also identified unique underlying tickers and got marks for those, as well.

Logic supports authentication with a single or multiple accounts. For example, position and
trade records are retrieved for all accounts included during token authentication. The position/trade records are output sequentially for each account, and the logger message
should indicate which account is being queried.

I took everything I learned during this project and created a single file that implements
an object-oriented approach to getting account balances, positions, and transactions.
I'm keeping the old files (account_data.py, market_date.py, option_tickers.py)
because they still have the stdin functionality which is helpful. Eventually, I will expand
SchwabAPI.py to include stdin functionality as well.

## auth.py  
Usage: `python auth.py <(N)ew | (R)efresh | (S)et timer>`  
Note: must have the following env variables set in a `.env` file:  
* **SCHWAB_API_KEY**: provided by Schwab when you complete API registration  
* **SCHWAB_API_SECRET**: provided by Schwab when you complete API registration  
* **SCHWAB_TOKEN_FILE**: provided by USER, local directory where `token.json` will be kept  

**New**: gets a new token, including website authentication  
**Refresh**: refreshes current token, no website authentication required  
**Set timer**: NEW! Crontab command now actually runs the token refresh, so set it and forget it!
If you forget to remove the crontab, Schwab will no longer refresh the token after 24 hours.
Remove the crontab via `crontab -r` or `crontab -e` if you have other crontab entries.
On my machine, it also announces when the token is getting refreshed so I don't literally
forget about it!

## option_tickers.py  
Usage: `python option_tickers.py <(T)o API | (F)rom API> <infile> > <outfile>`  
Currently, 'position' information is required, but unused. I am working on a function to calculate realized P/L. 
`position` is required for input processing to function properly, but largely ignored. 
I used the same format as the thinkorswim excel file export under "Options" section so you can just copy/paste into the \<infile\>.  

**To API**: formats option info into API ticker format (copy info from tos excel export (i.e., tab delimited))  
* **infile**: format: `DIS⋅17-Jan-25⋅114⋅PUT⋅position` (`⋅` = tab)  

**From API**: not really used independently, but serves as a testbed for code used in `market_data.py` to output appropriate ticker format from quote  
* **infile**: format: `DIS⋅⋅⋅250117P00114000` (`⋅` = space)  

## market_data.py  
Usage: `python market_data.py <(Q)uote | (H)istory | (C)hains> <filename>`  

**Quote**: "quote" API call, takes a list of tickers formatted for API.  
* **filename**: First row should include "Stocks" or "Options", as appropriate.
This helps format output correctly for copy/paste to excel (i.e., comma delimited)  
`option_tickers.py` automatically adds the "Options" label.
 
**History**: Not implemented, yet.  
**Chains**: Not implemented, yet.  

## realpl.py  
**Under Development**  
Find the Realized P/L for each symbol provided in a set of option trades.  
Input is a csv file that contains the trades as provided by tos export function  
Output is a list of realized p/l for each symbol that can be cut/pasted into excel.  

## bjer-sten.py  
**Under Development**  
Implements Bjerksun-Stensland option pricing model.  
Requires installation of QuantLib and Python QuantLib module.  

## Requirements  
`Python 3.13.0`  
Additional requirements available in 'requirements' (txt) file.
Use `pip -r requirements` to automatically load all requirements.