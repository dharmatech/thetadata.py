
import os
import io
import glob
import requests
import pandas as pd
import datetime
import pytz

# ----------------------------------------------------------------------

trade_conditions = pd.read_json('TradeConditions.json')

# ----------------------------------------------------------------------
# Get all expirations for date

def get_all_expirations(date, symbol):

    url = "http://127.0.0.1:25510/v2/list/expirations"

    querystring = { "root": symbol }

    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, params=querystring)

    expirations = pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])
 
    expirations_ = expirations[expirations['date'] >= int(date)]

    return expirations_

# tmp = get_all_expirations('20240614', 'TSLA')

# tmp
# ----------------------------------------------------------------------
# Get all trades for a given symbol and expiration that were made on 'date'.

def trade_quote(symbol, expiration, date):

    url = "http://127.0.0.1:25510/v2/bulk_hist/option/trade_quote"
    
    querystring = { "root": symbol, "exp": expiration, "start_date": date, "end_date": date, "use_csv":"true" }

    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, params=querystring)
    
    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))    

    return df

# df = trade_quote('TSLA', '20260116', '20240614')

# df

# ----------------------------------------------------------------------
# Get all trades for date, symbol.

def get_all_trades(date, symbol):

    print(f'Retrieving trades for {date} and {symbol}')

    expirations = get_all_expirations(date, symbol)

    dfs = []

    for expiration in expirations['date']:
        print(f'    Retrieving data for expiration {expiration}')
        dfs.append(trade_quote(symbol, str(expiration), date))

    result = pd.concat(dfs)

    return result

# df = get_all_trades('20240614', 'LAC')

# df

# ----------------------------------------------------------------------
# Store trades locally

def add_trades_for_date(date, symbol):

    if os.path.exists('pkl') == False:
        os.mkdir('pkl')
        
    path = f'pkl/{symbol}.pkl'

    if os.path.exists(path) == False:
        new = get_all_trades(date, symbol)

        if len(new) > 0:
            new.to_pickle(path)
            return new
        else:
            print(f'No data found for {date}')
    else:    

        df = pd.read_pickle(path)

        if len(df[df['date'] == int(date)]) > 0:
            print('Data already exists for this date')
        else:
            new = get_all_trades(date, symbol)

            df = pd.concat([df, new]).sort_values(by=['date', 'ms_of_day'])
            
            df.to_pickle(path)

            return df
        
# ----------------------------------------------------------------------
# Remove trades stored locally.

def remove_trades_for_date(date, symbol):

    path = f'pkl/{symbol}.pkl'

    if os.path.exists(path) == False:
        print(f'No data found for {symbol}')
    else:
        df = pd.read_pickle(path)

        df = df[df['date'] != date]

        df.to_pickle(path)

        return df

# add_trades_for_date('20240522', 'TSLA')    
# ----------------------------------------------------------------------
# Show what dates are available locally.

def show_available_dates(symbol):

    path = f'pkl/{symbol}.pkl'

    # df = pd.read_pickle(f'{symbol}.pkl')

    df = pd.read_pickle(path)

    return pd.DataFrame(df['date'].unique()).sort_values(by=0)

# show_available_dates('TSLA')
# ----------------------------------------------------------------------
def get_most_recent_date(symbol):

    ls = show_available_dates(symbol)

    return ls.iloc[-1][0]

# get_most_recent_date('HOOD')
# ----------------------------------------------------------------------    
def most_recent_completed_options_trading_day():
    # Get the current time in PST
    current_time = datetime.datetime.now(pytz.timezone('US/Pacific')).time()

    # Compare the current time to 1:15 PM
    if current_time > datetime.time(13, 15):
        # If the current time is after 1:15 PM, return today's date
        return pd.to_datetime('today')
    else:
        # If the current time is before 1:15 PM, return yesterday's date
        return pd.to_datetime('today') + pd.DateOffset(days=-1)
    
# most_recent_completed_options_trading_day()
# ----------------------------------------------------------------------

def pkl_exists(symbol):
    path = f'pkl/{symbol}.pkl'
    return os.path.exists(path)

# pkl_exists('HOOD')
# ----------------------------------------------------------------------
# def update_trades(symbol):

#     if pkl_exists(symbol) == False:
#         print(f'No data found for {symbol}')

#         end_date = most_recent_completed_options_trading_day()

#         start_date = end_date + pd.DateOffset(days=-30)    

#         for date in pd.date_range(start=start_date, end=end_date):
#             add_trades_for_date(date.strftime('%Y%m%d'), symbol)
#     else:
#         most_recent_date = get_most_recent_date(symbol)

#         most_recent_date = pd.to_datetime(most_recent_date, format='%Y%m%d')

#         start_date = most_recent_date + pd.DateOffset(days=1)

#         end_date = most_recent_completed_options_trading_day()

#         for date in pd.date_range(start=start_date, end=end_date):
#             add_trades_for_date(date.strftime('%Y%m%d'), symbol)

# update_trades('LAC')
# ----------------------------------------------------------------------
# If no data exists for symbol, download and store trades for the last 30 days.

# Removes trades for most recent date stored (in case it's incomplete).
# Then, adds trades from most recent date stored to present.

def update_trades_alt(symbol):

    if pkl_exists(symbol) == False:
        print(f'No data found for {symbol}')

        end_date = pd.to_datetime('today')

        start_date = end_date + pd.DateOffset(days=-30)    

        for date in pd.date_range(start=start_date, end=end_date):
            add_trades_for_date(date.strftime('%Y%m%d'), symbol)
    else:
        most_recent_date = get_most_recent_date(symbol)

        remove_trades_for_date(most_recent_date, symbol)
        
        most_recent_date = pd.to_datetime(most_recent_date, format='%Y%m%d')

        start_date = most_recent_date

        end_date = pd.to_datetime('today')

        for date in pd.date_range(start=start_date, end=end_date):
            add_trades_for_date(date.strftime('%Y%m%d'), symbol)

# update_trades_alt('LAC')
# ----------------------------------------------------------------------

def get_all_symbols():
    files = glob.glob('pkl/*.pkl')

    files = [file for file in files if '-' not in file]

    files = [os.path.basename(file) for file in files]

    symbols = [os.path.splitext(file)[0] for file in files]

    return symbols

# get_all_symbols()
# ----------------------------------------------------------------------
def update_all_symbols():
    symbols = get_all_symbols()

    for symbol in symbols:
        # update_trades(symbol)
        update_trades_alt(symbol)

# update_all_symbols()



