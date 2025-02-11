#!/Users/jnn/Documents/Trading/Devel/tosenv/bin/python3
import pandas as pd

def closed_realpl(df):
    # print rows with condition
    #print(df.loc[df['Symbol'] == 'NEM'])

    realpl = 0
    print("Realized P/L")
    for symbol in df['Symbol'].unique():
        for exp in df.loc[df['Symbol'] == symbol]['Exp'].unique():
            for strike in df.loc[(df['Symbol'] == symbol) & (df['Exp'] == exp)]['Strike'].unique():
                position = df.loc[(df['Symbol'] == symbol) & (df['Exp'] == exp) & (df['Strike'] == strike)]['Qty'].sum()
                # found all positions for this symbol, exp, strike that net to zero (i.e., closed)
                if position == 0:
                    #print(df.loc[(df['Symbol'] == symbol) & (df['Exp'] == exp) & (df['Strike'] == strike)].to_csv(index=False))
                    realpl = realpl + df.loc[(df['Symbol'] == symbol) & (df['Exp'] == exp) & (df['Strike'] == strike)]['MktVal'].sum()
                else:
                    #print(f"Open: {symbol},{exp},{strike},{position}")
                    pass

        print(f"{symbol},{realpl:.2f}")
        realpl = 0

    return

if __name__ == '__main__':
    df = pd.read_csv('Data/trades.csv')
    df['MktVal'] = df['Qty'] * df['Price'] * -100
    df.sort_values(by=['Symbol', 'Exp', 'Strike'], inplace=True)
    closed_realpl(df)
    #df.to_csv('Data/closed.csv', index=False)