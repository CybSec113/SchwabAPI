## Schwab API
Code to authenticate and access Schwab API
Currently only supports individual developer role and Market Data API
All scripts now include "shebang" to allow for direct execution.


See the YouTube video here:  
https://youtu.be/vnXVsJuI6ns

I made lots of enhancements since uploading the video, so check back here for more updated code
and functionality.

All scripts have `shebang` line at the top, but user must check location of Python venv for it to
work properly. User must also ensure executable permissions on script files.

## auth.py  
usage: `python auth.py <(N)ew | (R)efresh | (S)et timer>`  
Note: must have the following env variables set in a `.env` file:  
* **SCHWAB_API_KEY**: provided by Schwab when you complete API registration  
* **SCHWAB_API_SECRET**: provided by Schwab when you complete API registration  
* **SCHWAB_TOKEN_FILE**: provided by USER, local directory where `token.json` will be kept  

**New**: gets a new token, including website authentication  
**Refresh**: refreshes current token, no website authentication required  
**Set timer**: NEW! Crontab command now actually runs the token refresh, so set it and forget it!
If you forget to remove the crontab, Schwab will no longer refresh the token after 24 hours.
Remove the crontab via `crontab -r` or `crontab -e` if you have other crontab entries.

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