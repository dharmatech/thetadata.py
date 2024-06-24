
import os
import io
import glob
import requests
import pandas as pd
import datetime
import pytz

# ----------------------------------------------------------------------

# trade_conditions = pd.read_json('TradeConditions.json')

# ----------------------------------------------------------------------
# Get all expirations for date

# def get_all_expirations(date, symbol):

#     url = "http://127.0.0.1:25510/v2/list/expirations"

#     querystring = { "root": symbol }

#     headers = {"Accept": "application/json"}

#     response = requests.get(url, headers=headers, params=querystring)


#     response.status_code


#     expirations = pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])
 
#     expirations_ = expirations[expirations['date'] >= int(date)]

#     return expirations_


def get_all_expirations(date, symbol):

    url = "http://127.0.0.1:25510/v2/list/expirations"

    querystring = { "root": symbol }

    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, params=querystring)

        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

        expirations = pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])

        expirations_ = expirations[expirations['date'] >= int(date)]
        return expirations_

    # except requests.exceptions.HTTPError as errh:
    #     print ("HTTP Error:",errh)
    #     return None
    # except requests.exceptions.ConnectionError as errc:
    #     print ("Error Connecting:",errc)
    #     return None
    # except requests.exceptions.Timeout as errt:
    #     print ("Timeout Error:",errt)
    #     return None
    except requests.exceptions.RequestException as err:
        print ("Something went wrong with the request:",err)
        return None

# tmp = get_all_expirations('20240614', 'TSLA')
# ----------------------------------------------------------------------
# Get all trades for a given symbol and expiration that were made on 'date'.

# symbol = 'TSLA'
# expiration = '20260116'
# date = '20240614'

def trade_quote(symbol, expiration, date):

    url = "http://127.0.0.1:25510/v2/bulk_hist/option/trade_quote"
    
    querystring = { "root": symbol, "exp": expiration, "start_date": date, "end_date": date, "use_csv":"true" }

    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.headers['Next-page'] != 'null':
        print('Next page exists')
        print(f'{symbol=} {expiration=} {date=}')
    
    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))    

    return df

# df = trade_quote('TSLA', '20260116', '20240614')
# ----------------------------------------------------------------------
# Get all trades for date, symbol.

# def get_all_trades(date, symbol):

#     print(f'Retrieving trades for {date} and {symbol}')

#     expirations = get_all_expirations(date, symbol)

#     dfs = []

#     for expiration in expirations['date']:
#         print(f'    Retrieving data for expiration {expiration}')
#         dfs.append(trade_quote(symbol, str(expiration), date))

#     result = pd.concat(dfs)

#     return result

def get_all_trades(date, symbol):

    print(f'Retrieving trades for {date} and {symbol}')

    try:

        expirations = get_all_expirations(date, symbol)

        if expirations is None:
            print(f"No expirations found for {date} and {symbol}")
            return None

        dfs = []

        for expiration in expirations['date']:
            print(f'    Retrieving data for expiration {expiration}')
            dfs.append(trade_quote(symbol, str(expiration), date))

        result = pd.concat(dfs)

        return result

    except Exception as e:
        print(f"An error occurred while retrieving trades for {date} and {symbol}: {str(e)}")
        return None

# df = get_all_trades('20240614', 'LAC')

# ----------------------------------------------------------------------
# Store trades locally

def add_trades_for_date(date, symbol):

    if os.path.exists('pkl') == False:
        os.mkdir('pkl')
        
    path = f'pkl/{symbol}.pkl'

    if os.path.exists(path) == False:
        new = get_all_trades(date, symbol)

        if new is None:
            print(f"No trades found for {symbol} on {date}")
            return None
        elif len(new) > 0:
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

# show_available_dates('AAPL')
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

# update_trades_alt('QRVO')
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

# def list_roots_stock():

#     url = 'http://127.0.0.1:25510/v2/list/roots/stock'

#     headers = {"Accept": "application/json"}

#     response = requests.get(url, headers=headers)

#     roots = pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])
     
#     return roots

# roots_stocks = list_roots_stock()

# roots_stocks

# roots = roots_stocks

# roots['root']

# ----------------------------------------------------------------------

import time

def all_trades(trade_date, roots):
        
    i = 0

    start_time = time.time()
        
    for root in roots['root']:
        print(f'Retrieving trades for {root} {i} of {len(roots)}. Time elapsed: {str(datetime.timedelta(seconds=(time.time() - start_time)))[:7]}')
        
        df = get_all_trades(trade_date, root)

        i += 1

        if df is None:
            print(f"No trades found for {root} on {trade_date}")
            with open('pkl-all/no-trades.txt', 'a') as file:
                file.write(root + '\n')            
        else:
            df.to_pickle(f'pkl-all/{root}.pkl')
# ----------------------------------------------------------------------
# roots_stocks = list_roots_stock()

# all_trades('20240618', roots_stocks)
# ----------------------------------------------------------------------

# df = get_all_trades('20240618', 'AAA')

# type(df)


# date = '20240618'
# symbol = 'AAA'

# trade_date = date
# ----------------------------------------------------------------------
def all_stocks_all_trades(trade_date, stocks):

    i = 0

    start_time = time.time()

    no_trades_path = f'pkl/no-trades-{trade_date}.txt'

    with open(no_trades_path, 'w') as file:
        file.write('')

    for stock in stocks:

        elapsed_time = str(datetime.timedelta(seconds=(time.time() - start_time)))[:7]

        print(f'Retrieving trades for {stock}. Time elapsed: {elapsed_time}')

        df = add_trades_for_date(trade_date, stock)

        if df is None:
            print(f"No trades found for {stock} on {trade_date}")
            with open(no_trades_path, 'a') as file:
                file.write(stock + '\n')

# all_stocks_all_trades('20240614', roots_stocks['root'])
# ----------------------------------------------------------------------
# trade_date = '20240617'
# symbol = 'AAA'
# stock = 'AAA'
# date = trade_date
# ----------------------------------------------------------------------

# def list_roots_option():

#     url = 'http://127.0.0.1:25510/v2/list/roots/option'

#     headers = {"Accept": "application/json"}

#     response = requests.get(url, headers=headers)

#     roots = pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])
     
#     return roots

# roots_stocks = list_roots_stock()

# roots_options = list_roots_option()

# roots_stocks

# roots_options

# rows where 'root' starts with 'ZV'

# roots[roots['root'].str.startswith('ZV')]

# ----------------------------------------------------------------------

def list_contracts(start_date):

    url = "http://127.0.0.1:25510/v2/list/contracts/option/trade"

    querystring = { "start_date": start_date }

    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, params=querystring)

        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        
        df = pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])

        return df

    except requests.exceptions.RequestException as err:
        print ("Something went wrong with the request:",err)
        return None

# contracts = list_contracts('20240620')

# ls = contracts[['root', 'expiration']].drop_duplicates()

# ls = ls.reset_index(drop=True)

# ----------------------------------------------------------------------
# start_time = time.time()

# tmp = pd.DataFrame()

# for index, row in ls.iterrows():

#     df = trade_quote(symbol=row['root'], expiration=row['expiration'], date='20240620')
    
#     tmp = pd.concat([tmp, df])
    
#     if index % 10 == 0:
#         elapsed_time = str(datetime.timedelta(seconds=(time.time() - start_time)))[:7]
#         print(f'{index} of {len(ls)} completed. Time elapsed: {elapsed_time}')

# elapsed_time = str(datetime.timedelta(seconds=(time.time() - start_time)))[:7]

# tmp.query('root == "AAPL"')

# tmp.to_pickle('pkl/tmp.pkl')

# ----------------------------------------------------------------------

# contracts.query('root == "AAPL"').query('expiration == 20241018')



# tmp = contracts[['root', 'expiration']].drop_duplicates()

# tmp.query('root == "AAPL"')

# tmp

# ----------------------------------------------------------------------

# ls = ls.reset_index(drop=True)

# for index, row in ls.iterrows():
#     print(f'{index} of {len(ls)} completed')





# import pprint

# def trade_quote_alt(symbol, expiration, date):

#     url = "http://127.0.0.1:25510/v2/bulk_hist/option/trade_quote"
    
#     querystring = { "root": symbol, "exp": expiration, "start_date": date, "end_date": date }

#     headers = {"Accept": "application/json"}

#     response = requests.get(url, headers=headers, params=querystring)

#     pprint.pprint(response.json(), depth=1)

#     pprint.pprint(response.json()['header'], depth=1)

#     pprint.pprint(response.json()['header']['format'], depth=1)

#     next_page = response.json()['header']['next_page']

#     if next_page != 'null':
#         print('Next page exists')



#     pprint.pprint(response.json()['response'], depth=1)

#     pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])

#     type(response.json()['response'])

#     pprint.pprint(response.json()['response'][0])
    
    


    
    
#     # df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))    

#     return df