
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

# tmp = get_all_expirations('20240615', 'TSLA')

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




# ----------------------------------------------------------------------

# symbol = 'JD'

# add_trades_for_date('20240520', symbol)
# add_trades_for_date('20240521', symbol)
# add_trades_for_date('20240522', symbol)
# add_trades_for_date('20240523', symbol)
# add_trades_for_date('20240524', symbol)
# ----------------------------------------------------------------------

# initial_date = 20240506

# for date in range(initial_date, initial_date + 5):
#     # print(f'Adding data for {date}')
#     add_trades_for_date(str(date), symbol)
# ----------------------------------------------------------------------

# def date_range(start_date, num_days=5):
#     start_date = pd.to_datetime(start_date, format='%Y%m%d')
#     return pd.date_range(start_date, periods=num_days).strftime('%Y%m%d').tolist()

# pd.date_range(start='2023-12-01', end='2024-01-01').strftime('%Y%m%d').tolist()

# symbol = 'BILI'

# for date in date_range('20240429', 30):
#     add_trades_for_date(str(date), symbol)

# symbol = 'LAC'

# for date in date_range('20240101', 2):
#     result = add_trades_for_date(str(date), symbol)

# show_available_dates('LAC')    

# add_trades_for_date(str(20240419), symbol)


# get date 30 days ago

# date = pd.to_datetime('today') - pd.DateOffset(days=30)

# date = date.strftime('%Y%m%d')

# def days_ago(num_days):
#     date = pd.to_datetime('today') - pd.DateOffset(days=num_days)
#     return date.strftime('%Y%m%d')

# days_ago(30)


# symbol = 'ATMU'

# for date in date_range(days_ago(30), 40):
#     result = add_trades_for_date(str(date), symbol)


# for date in date_range('20240101', 30*5):
#     result = add_trades_for_date(str(date), symbol)


# date = '20240428'

# add_trades_for_date('20240428', symbol)



# for date in pd.date_range(start='2023-12-01', end='2024-01-01').strftime('%Y%m%d').tolist():
#     add_trades_for_date(str(date), symbol)



# symbol = 'JD'

# for date in pd.date_range(start='2024-05-25', end='2024-06-01').strftime('%Y%m%d').tolist():
#     add_trades_for_date(str(date), symbol)


# show_available_dates('JD')

# show_available_dates('ATMU')
# add_trades_for_date('20240529', 'ATMU')

# ----------------------------------------------------------------------

# Get 'ATMU' trades for '20240321'

# df = get_all_trades('20240321', 'ATMU')

# df['premium'] = df['size'] * df['price'] * 100

# columns_to_drop = ['No data for the specified timeframe and chain. Debug code 1', 'ext_condition1', 'ext_condition2', 'ext_condition3', 'ext_condition4', 'ask_condition', 'bid_condition', 'records_back', 'condition_flags', 'volume_type' ]

# df = df.drop(columns=columns_to_drop)

# df.iloc[0]

# df.drop(columns=['No data for the specified timeframe and chain. Debug code 1', 'ext_condition1', 'ext_condition2', 'ext_condition3', 'ext_condition4', 'ask_condition', 'bid_condition', 'records_back', 'condition_flags', 'volume_type' ])

# df['ask_condition'].unique()
# df['records_back'].unique()
# df['condition_flags'].unique()
# df['volume_type'].unique()

# df.drop(columns=columns_to_drop)

# df[df['premium'] > 10000]

# Write this using query syntax: df[df['premium'] > 100]

# df.query('premium > 100')












# pkl_exists('RUN')

# symbol = 'HPQ'


# df = pd.read_pickle('pkl/JMIA.pkl')

# ----------------------------------------------------------------------

# update_trades('HOOD')

# update_trades('HPQ')

# update_trades('JMIA')

# update_trades_alt('JMIA')


# ----------------------------------------------------------------------


# update_trades_alt('GME')

# ----------------------------------------------------------------------


# symbol = 'HOOD'

# for date in pd.date_range(start='2024-05-01', end='2024-05-19').strftime('%Y%m%d').tolist():
    # add_trades_for_date(str(date), symbol)

# pd.date_range(start='2024-05-01', periods=5, freq='D')

# for date in pd.date_range(start='2024-05-01', end='2024-05-19'):
#     date = date.strftime('%Y%m%d')
#     add_trades_for_date(date, symbol)

# for date in pd.date_range(start='2024-04-01', end='2024-04-30'):
#     date = date.strftime('%Y%m%d')
#     add_trades_for_date(date, symbol)

# symbol = 'JD'

# for date in pd.date_range(start='2024-04-01', end='2024-04-28'):
#     date = date.strftime('%Y%m%d')
#     add_trades_for_date(date, symbol)