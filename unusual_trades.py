
import pandas as pd
import argparse

import process_dataframe
import store

symbols = store.saved_symbols()

columns = ['date_str', 'ms_of_day', 'root', 'exp_str', 'right', 'strike_', 'bid', 'price', 'ask', 'ask_bid_diff', 'size', 'premium', 'side', 'bb_', 'bb_confidence', 'condition_name']

# symbol = 'TSLA'

# import importlib

# importlib.reload(store)
# importlib.reload(process_dataframe)

def unusual_trades(trade_date, pct_threshold):

    # dfs = []

    dfs = pd.DataFrame()

    for symbol in symbols:
        
        df = store.load_trades(symbol)

        df['size'] = df['size'].astype(int)

        df['premium'] = df['size'] * df['price'] * 100

        df['premium'] = df['premium'].astype(int)
        
        premium_threshold = process_dataframe.find_premium_threshold_alt(df, pct_threshold)

        df = df.query(f'premium >= {premium_threshold}').copy()

        df = process_dataframe.process_dataframe(df)

        df['exp_str'] = df['expiration_'].astype(str)

        df['date_str'] = df['date_'].astype(str)

        result = df.query(f'date == {trade_date}')

        if len(result) > 0:
            print(result[columns])

            # dfs.append(result)

            dfs = pd.concat([dfs, result])

    return dfs
# ----------------------------------------------------------------------
import argparse

parser = argparse.ArgumentParser(description="Process some integers.")

parser.add_argument('trade_date', type=int,                            help='Retrieve trades for this date (required)')
parser.add_argument('pct',        type=float, nargs='?', default=0.01, help='Percent threshold (optional, default is 0.01)')

args = parser.parse_args()

trade_date = args.trade_date

pct = args.pct
# ----------------------------------------------------------------------
result = unusual_trades(trade_date, pct)

# result = unusual_trades(20240621, 0.01)
# ----------------------------------------------------------------------
with open(f'out/unusual_trades_{trade_date}.txt', 'w', encoding='utf-8') as f:
    f.write(result[columns].to_string())

result[columns].to_csv(f'out/unusual_trades_{trade_date}.csv', index=False)