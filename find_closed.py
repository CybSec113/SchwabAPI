#!/Users/jnn/Documents/Trading/Devel/tosenv/bin/python3
import pandas as pd

def find_closed(df):
    # print rows with condition
    #print(df.loc[df['Symbol'] == 'NEM'])

    print("Positions")
    for symbol in df['Symbol'].unique():
        for exp in df.loc[df['Symbol'] == symbol]['Exp'].unique():
            for strike in df.loc[(df['Symbol'] == symbol) & (df['Exp'] == exp)]['Strike'].unique():
                position = df.loc[(df['Symbol'] == symbol) & (df['Exp'] == exp) & (df['Strike'] == strike)]['Qty'].sum()
                if position == 0:
                    print(df.loc[(df['Symbol'] == symbol) & (df['Exp'] == exp) & (df['Strike'] == strike)])
        print("----")

    return

if __name__ == '__main__':
    df = pd.read_csv('Data/trades.csv')
    find_closed(df)
    #df.to_csv('Data/closed.csv', index=False)
    print("Done")