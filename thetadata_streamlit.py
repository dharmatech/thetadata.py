import os
import glob
import pandas as pd
import streamlit as st
import plotly.express as px

import store
import process_dataframe
# ----------------------------------------------------------------------
@st.cache_data
def load_conditions():
    return pd.read_json('TradeConditions.json')

trade_conditions = load_conditions()

@st.cache_data
def load_trades(symbol):
    path = f'pkl/{symbol}.pkl'
    # return pd.read_pickle(f'{symbol}.pkl')
    return pd.read_pickle(path)
# ----------------------------------------------------------------------
# def saved_symbols():
#     files = glob.glob('pkl/*.pkl')

#     files = [file for file in files if '-' not in file]

#     files = [os.path.basename(file) for file in files]

#     symbols = [os.path.splitext(file)[0] for file in files]

#     return symbols
# ----------------------------------------------------------------------
import store

symbols = store.saved_symbols()

symbol = st.sidebar.selectbox('Symbol', symbols)

df = load_trades(symbol)

# df = load_trades('NVDA')

# df[columns]

# df.query('premium > 40000')[columns].tail(30)

df['size'] = df['size'].astype(int)

df['premium'] = df['size'] * df['price'] * 100

df['premium'] = df['premium'].astype(int)

# def find_premium_threshold_alt(df, pct):
#     sorted = df['premium'].sort_values(ascending=False)
#     i = int((pct / 100) * len(sorted))
#     return sorted.iloc[i]

premium_pct_threshold = st.sidebar.number_input('% threshold for premium', value=1.0, min_value=0.0001, format='%f', help='''
Filter trades by premium.
                    
For example, if this number is 5%, then the top 5% of trades by premium are included in the analysis.
                                                ''')

premium_threshold = process_dataframe.find_premium_threshold_alt(df, premium_pct_threshold)

st.sidebar.write(f'Premium threshold: {premium_threshold:,}')

df = df.query(f'premium > {premium_threshold}')

# ----------------------------------------------------------------------

# def process_dataframe(df):
#     df['date_'] = pd.to_datetime(df['date'].astype(int).astype(str), format='%Y%m%d')

#     df['size'] = df['size'].astype(int)

#     df['premium'] = df['size'] * df['price'] * 100

#     df['premium'] = df['premium'].astype(int)

#     df = pd.merge(df, trade_conditions[['Code', 'Name']], left_on='condition', right_on='Code', how='left')

#     df = df.drop(columns=['Code'])

#     df = df.rename(columns={'Name': 'condition_name'})

#     df['strike_'] = df['strike'] / 100 / 10    

#     df['ask_sub_price'] = df['ask'] - df['price']

#     df['price_sub_bid'] = df['price'] - df['bid']

#     df.loc[df['ask_sub_price'] < df['price_sub_bid'], 'side'] = 'buy'

#     df.loc[df['ask_sub_price'] > df['price_sub_bid'], 'side'] = 'sell'

#     df.loc[df['ask_sub_price'].round(3) == df['price_sub_bid'].round(3), 'side'] = 'eq'

#     df.loc[(df['right'] == 'C') & (df['side'] == 'buy'),  'bb'] = '🟢'
#     df.loc[(df['right'] == 'C') & (df['side'] == 'sell'), 'bb'] = '🔴'

#     df.loc[(df['right'] == 'P') & (df['side'] == 'buy'),  'bb'] = '🔴'
#     df.loc[(df['right'] == 'P') & (df['side'] == 'sell'), 'bb'] = '🟢'


#     df.loc[(df['right'] == 'C') & (df['side'] == 'buy'),  'bb_'] = 'bullish'
#     df.loc[(df['right'] == 'C') & (df['side'] == 'sell'), 'bb_'] = 'bearish'
#     df.loc[(df['right'] == 'P') & (df['side'] == 'buy'),  'bb_'] = 'bearish'
#     df.loc[(df['right'] == 'P') & (df['side'] == 'sell'), 'bb_'] = 'bullish'

#     df.loc[(df['side'] == 'eq'), 'bb_'] = 'neutral'

#     df['ask_bid_diff'] = df['ask'] - df['bid']

#     df.loc[df['side'] == 'buy',  'bb_confidence'] = (df[df['side'] == 'buy' ]['ask_bid_diff'] - df[df['side'] == 'buy' ]['ask_sub_price']) / df[df['side'] == 'buy' ]['ask_bid_diff']
#     df.loc[df['side'] == 'sell', 'bb_confidence'] = (df[df['side'] == 'sell']['ask_bid_diff'] - df[df['side'] == 'sell']['price_sub_bid']) / df[df['side'] == 'sell']['ask_bid_diff']

#     df['bb_confidence'] = df['bb_confidence'].round(3)

#     df['expiration_'] = pd.to_datetime(df['expiration'].astype(int).astype(str), format='%Y%m%d')

#     df['ms_of_day_'] = pd.to_timedelta(df['ms_of_day'], unit='ms')

#     df['datetime'] = df['date_'] + df['ms_of_day_']

#     df['dte'] = (df['expiration_'] - df['date_']).dt.days

#     # Convert 'datetime' to string format
#     df['datetime_str'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')    

#     return df

import process_dataframe

df = process_dataframe.process_dataframe(df)

df['exp_str'] = df['expiration_'].astype(str)

df['date_str'] = df['date_'].astype(str)

# columns = ['date_str', 'ms_of_day', 'root', 'exp_str', 'right', 'strike_', 'bid', 'price', 'ask', 'ask_bid_diff', 'size', 'premium', 'side', 'bb_', 'bb_confidence', 'condition_name']

# columns = ['date_str', 'ms_of_day', 'root', 'exp_str', 'right', 'strike_', 'dte', 'bid', 'price', 'ask', 'ask_bid_diff', 'size', 'premium', 'side', 'bb_confidence', 'condition_name', 'bb']

# df[columns]
# df.iloc[-1]

# ----------------------------------------------------------------------
date_min = df['date_'].min()
date_max = df['date_'].max()

start_date = st.sidebar.date_input('Start date', min_value=date_min, max_value=date_max, value=date_min)

start_date = pd.to_datetime(start_date)

df = df[df['date_'] >= start_date]
# ----------------------------------------------------------------------
# df['premium'] = df['size'] * df['price'] * 100

# df = pd.merge(df, trade_conditions[['Code', 'Name']], left_on='condition', right_on='Code', how='left')

# df = df.drop(columns=['Code'])

# df = df.rename(columns={'Name': 'condition_name'})

# df['strike_'] = df['strike'] / 100 / 10

# ----------
# df['ask_sub_price'] = df['ask'] - df['price']

# df['price_sub_bid'] = df['price'] - df['bid']

# df.loc[df['ask_sub_price'] < df['price_sub_bid'], 'side'] = 'buy'

# df.loc[df['ask_sub_price'] > df['price_sub_bid'], 'side'] = 'sell'

# df.loc[df['ask_sub_price'].round(3) == df['price_sub_bid'].round(3), 'side'] = 'eq'

# df.loc[(df['right'] == 'C') & (df['side'] == 'buy'),  'bb'] = '🟢'
# df.loc[(df['right'] == 'C') & (df['side'] == 'sell'), 'bb'] = '🔴'

# df.loc[(df['right'] == 'P') & (df['side'] == 'buy'),  'bb'] = '🔴'
# df.loc[(df['right'] == 'P') & (df['side'] == 'sell'), 'bb'] = '🟢'


# df.loc[(df['right'] == 'C') & (df['side'] == 'buy'),  'bb_'] = 'bullish'
# df.loc[(df['right'] == 'C') & (df['side'] == 'sell'), 'bb_'] = 'bearish'
# df.loc[(df['right'] == 'P') & (df['side'] == 'buy'),  'bb_'] = 'bearish'
# df.loc[(df['right'] == 'P') & (df['side'] == 'sell'), 'bb_'] = 'bullish'

# df.loc[(df['side'] == 'eq'), 'bb_'] = 'neutral'

# df['ask_bid_diff'] = df['ask'] - df['bid']

# df.loc[df['side'] == 'buy',  'bb_confidence'] = (df[df['side'] == 'buy' ]['ask_bid_diff'] - df[df['side'] == 'buy' ]['ask_sub_price']) / df[df['side'] == 'buy' ]['ask_bid_diff']
# df.loc[df['side'] == 'sell', 'bb_confidence'] = (df[df['side'] == 'sell']['ask_bid_diff'] - df[df['side'] == 'sell']['price_sub_bid']) / df[df['side'] == 'sell']['ask_bid_diff']

# df['bb_confidence'] = df['bb_confidence'].round(3)

# df['expiration_'] = pd.to_datetime(df['expiration'].astype(int).astype(str), format='%Y%m%d')

# df['ms_of_day_'] = pd.to_timedelta(df['ms_of_day'], unit='ms')

# df['datetime'] = df['date_'] + df['ms_of_day_']

# df['dte'] = (df['expiration_'] - df['date_']).dt.days

# # Convert 'datetime' to string format
# df['datetime_str'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
# ----------------------------------------------------------------------
minimum_premium = 1000

while len(df[df['premium'] > minimum_premium]) > 10000:
    minimum_premium *= 2

minimum_premium = st.sidebar.number_input('Minimum Premium', value=minimum_premium)

tmp = df[df['premium'] > minimum_premium]
# ----------------------------------------------------------------------
if st.sidebar.checkbox('Exclude expired trades', value=False):
    
    tmp = tmp[tmp['expiration_'] >= pd.to_datetime('today')]
# ----------------------------------------------------------------------
if st.sidebar.checkbox('Exclude trades expiring before', value=False):

    # expired_range_a = st.date_input('Exclude trades expiring before:', value=pd.to_datetime('1900-01-01'))

    expired_range_a = st.date_input(label='', value=pd.to_datetime('1900-01-01'))

    expired_range_a = expired_range_a.strftime('%Y%m%d')

    tmp = tmp[tmp['expiration_'] >= expired_range_a]
# ----------------------------------------------------------------------
st.sidebar.write(f'Number of trades: {len(tmp)}')

tmp_alt = tmp
# ----------------------------------------------------------------------
# Create a Plotly figure
fig = px.scatter(tmp, x='datetime_str', y='premium', 
                 color='bb_', color_discrete_map={'bullish': 'green', 'bearish': 'red', 'neutral': 'blue'}, 
                 symbol='condition_name', hover_data=['expiration', 'right', 'strike_', 'dte', 'side', 'size', 'ask', 'price', 'bid', 'bb_confidence'])

fig.update_layout(title=f'Options Trades for {symbol}')

st.plotly_chart(fig, use_container_width=True)
# ----------------------------------------------------------------------
fig = px.scatter(tmp, x='datetime_str', y='premium', color='condition_name',
                 symbol='bb_',
                 symbol_map={'neutral': 'circle', 'bearish': 'square', 'bullish': 'diamond'})

fig.update_layout(title=f'Options Trades for {symbol}')

# Display the figure in Streamlit
st.plotly_chart(fig, use_container_width=True)
# ----------------------------------------------------------------------
# df[['date', 'ms_of_day', 'root', 'expiration', 'strike_', 'right', 'premium', 'condition_name', 'side', 'bb_']]

# x-axis: expiration
# y-axis: strike

# Convert 'expiration' to integer, then to string in the format 'yyyymmdd', and then to datetime
tmp['expiration_'] = pd.to_datetime(tmp['expiration'].astype(int).astype(str), format='%Y%m%d')

# Convert 'expiration' to string format for plotting
tmp['expiration_str'] = tmp['expiration_'].dt.strftime('%Y-%m-%d')

# fig = px.scatter(tmp, x='expiration_str', y='strike', color='bb_', color_discrete_map={'bullish': 'green', 'bearish': 'red', 'neutral': 'blue'})

fig = px.scatter(tmp, x='expiration_str', y='strike', 
                 color='bb_', color_discrete_map={'bullish': 'green', 'bearish': 'red', 'neutral': 'blue'},
                 size='premium', size_max=20,
                 symbol='condition_name')

st.plotly_chart(fig, use_container_width=True)
# ----------------------------------------------------------------------
def clear_cache():
    load_conditions.clear()
    load_trades.clear()

st.button('Clear Cache', on_click=clear_cache)
# ----------------------------------------------------------------------

import yfinance_download

@st.cache_data
def get_stock_data(symbol):
    return yfinance_download.update_records(symbol)

df_stock = get_stock_data(symbol)

df_stock = df_stock[df_stock.index >= '2010-01-01']

import plotly.graph_objects as go

fig = go.Figure(data=[go.Candlestick(x=df_stock.index,
                open=df_stock['Open'],
                high=df_stock['High'],
                low=df_stock['Low'],
                close=df_stock['Close'])])

fig.update_yaxes(fixedrange=False)


# st.plotly_chart(fig, use_container_width=True)
# ----------------------------------------------------------------------
def is_risk_reversal(rows):
    if len(rows) != 2:
        return False

    rights = rows['right'].tolist()
    sides  = rows['side'].tolist()

    if 'C' in rights and 'P' in rights and 'buy' in sides and 'sell' in sides:
        return True
    else:
        return False
# ----------------------------------------------------------------------
def is_spread(rows):
    if len(rows) != 2:
        return False

    rights = rows['right'].tolist()
    sides = rows['side'].tolist()
    strikes = rows['strike_'].tolist()

    if rights[0] == rights[1] and 'buy' in sides and 'sell' in sides and strikes[0] != strikes[1]:
        return True
    else:
        return False    
# ----------------------------------------------------------------------

if st.checkbox('Show multi-leg trades', value=False) == False:
    st.stop()

st.write(f'Potential multi-leg trades')

exclude_gt_4 = st.checkbox('Exclude > 4', value=True)

multi_leg_count = 0

df['exp_str'] = df['expiration_'].astype(str)

df['date_str'] = df['date_'].astype(str)

columns = ['date_str', 'ms_of_day', 'root', 'exp_str', 'right', 'strike_', 'bid', 'price', 'ask', 'ask_bid_diff', 'size', 'premium', 'side', 'bb_', 'bb_confidence', 'condition_name']

result = df.query('premium > 100000').sort_values(by=['date', 'ms_of_day'])

for date in result['date']:    

    if multi_leg_count >= 100:
        st.write(f'### {multi_leg_count} multi-leg trades found. Stopping search.')
        break

    result_ = result[result['date'] == date]

    if len(result_) > 1:

        for time in result_['ms_of_day']:

            tmp = pd.DataFrame(result_)

            tmp['diff'] = result_['ms_of_day'] - time

            tmp['diff'] = tmp['diff'].abs()

            tmp = tmp[tmp['diff'] < 4]

            if len(tmp) > 1:

                if exclude_gt_4 and len(tmp) > 4:
                    continue

                multi_leg_count += 1
                
                if is_risk_reversal(tmp):
                    # print('risk_reversal')
                    st.write('risk_reversal')
                    
                    # tmp.iloc[0]
                    # --------------------------------------------------
                    x1 = tmp[tmp['right'] == 'P'].iloc[0].date_                    
                    y1 = df_stock[df_stock.index == x1].iloc[0]['Close']

                    x2 = tmp[tmp['right'] == 'P'].iloc[0].expiration_
                    y2 = tmp[tmp['right'] == 'P'].iloc[0].strike_

                    bb_ = tmp[tmp['right'] == 'P'].iloc[0]['bb_']

                    right = tmp[tmp['right'] == 'P'].iloc[0]['right']

                    # fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines'))

                    # fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines', text=[bb_, bb_], hoverinfo='x+y+text+name'))

                    # fig.add_trace(
                    #     go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines', 
                    #                text=[f'{bb_} {right}', f'{bb_} {right}'], hoverinfo='x+y+text+name'))

                    # --------------------------------------------------
                    x1 = tmp[tmp['right'] == 'C'].iloc[0].date_                    
                    y1 = df_stock[df_stock.index == x1].iloc[0]['Close']

                    x2 = tmp[tmp['right'] == 'C'].iloc[0].expiration_
                    y2 = tmp[tmp['right'] == 'C'].iloc[0].strike_

                    bb_ = tmp[tmp['right'] == 'C'].iloc[0]['bb_']

                    right = tmp[tmp['right'] == 'C'].iloc[0]['right']

                    # fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines'))                    

                    # fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines', text=[bb_, bb_], hoverinfo='text+name'))

                    # fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines', text=[bb_, bb_], hoverinfo='x+y+text+name'))
                    
                    # fig.add_trace(
                    #     go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines', 
                    #                text=[f'{bb_}, {right}', f'{bb_}, {right}'], hoverinfo='x+y+text+name'))
                    
                
                if is_spread(tmp):
                    # print('spread')
                    st.write('spread')
                
                st.write(tmp[columns])
                
            result_ = result_[result_['ms_of_day'] != time]

    result = result[result['date'] != date]



# for date in result['date']:    
#     result_ = result[result['date'] == date]

#     if len(result_) > 1:

#         for time in result_['ms_of_day']:

#             tmp = pd.DataFrame(result_)

#             tmp['diff'] = result_['ms_of_day'] - time

#             tmp['diff'] = tmp['diff'].abs()

#             tmp = tmp[tmp['diff'] < 4]

#             if len(tmp) > 1:
#                 print(date)

#                 if is_risk_reversal(tmp):
#                     print('risk_reversal')
                
#                 if is_spread(tmp):
#                     print('spread')

#                 print(tmp)
#                 print()

#             result_ = result_[result_['ms_of_day'] != time]

#     result = result[result['date'] != date]
# ----------------------------------------------------------------------

# result[columns]

# x1: date_
# y1: strike_
# x2: expiration_
# y2: strike_

# result = df.query('premium > 100000').sort_values(by=['date', 'ms_of_day'])

# result = tmp

result = tmp_alt

while len(result[result['premium'] > minimum_premium]) > 100:
    minimum_premium *= 2

minimum_premium = st.number_input('Minimum Premium ', value=minimum_premium)

result = result[result['premium'] > minimum_premium]

if st.checkbox(label='calls', value=True) == False:
    result = result[result['right'] != 'C']

if st.checkbox(label='puts', value=True) == False:
    result = result[result['right'] != 'P']

if st.checkbox('Exclude expired trades ', value=False):
    
    result = result[result['expiration_'] >= pd.to_datetime('today')]    

st.write(f'Number of trades: {len(result)}')

# for _, row in result.iterrows():
#     x1 = row['date_']
#     y1 = row['strike_']
#     x2 = row['expiration_']
#     y2 = row['strike_']
#     color = 'green' if row['bb_'] == 'bullish' else 'red' if row['bb_'] == 'bearish' else 'black'
#     line_type = 'solid' if row['right'] == 'C' else 'dash' if row['right'] == 'P' else 'solid'

#     fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', line=dict(color=color, dash=line_type)))

fig.update_layout(title=f'{symbol}')
# ----------------------------------------------------------------------

# result[columns]

# df_stock

# '''

# 'result' and 'df_stock are dataframes.

# merge result and df_stock.

# result['date_'] should match df_stock.index

# '''

df_stock_reset = df_stock.reset_index()
merged_df = pd.merge(result, df_stock_reset, left_on='date_', right_on='Date')

for _, row in merged_df.iterrows():
    x1 = row['date_']
    y1 = row['Close']
    x2 = row['expiration_']
    y2 = row['strike_']
    color = 'green' if row['bb_'] == 'bullish' else 'red' if row['bb_'] == 'bearish' else 'black'
    line_type = 'solid' if row['right'] == 'C' else 'dash' if row['right'] == 'P' else 'solid'

    fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', line=dict(color=color, dash=line_type)))

# merged_df

# result['date_']
# df_stock.index

# ----------------------------------------------------------------------

st.plotly_chart(fig, use_container_width=True)



# ----------------------------------------------------------------------

len(df)

# rows where premium > 100000

# df['premium']

len(df.query('premium > 100000')) / len(df) * 100

len(df.query('premium > 10000')) / len(df) * 100

df['premium'].max()

pct = 5

def find_premium_threshold(df, pct):
    a = 0
    c = df['premium'].max()

    while True:

        b = (a + c) / 2

        # print(f'a: {a} b: {b}, c: {c}')

        # print(f'a: {int(a):20}')
        # print(f'b: {int(b):20}')
        # print(f'c: {int(c):20}')

        # print()

        # len(df.query('premium > 10000')) / len(df) * 100

        result = len(df.query(f'premium > {b}')) / len(df) * 100

        if abs(result - pct) < 0.1:
            return b
        elif result < pct:   # result pct was too low.  premium guess was too high.
            # a = b
            c = b
        elif result > pct:   # result pct was too high. premium guess was too low.
            # c = b
            a = b

a = 185400000.0
b = 185400000.0
c = 185400000.0

premium_threshold_5_pct = find_premium_threshold(df, 5)

premium_threshold_2_pct = find_premium_threshold(df, 1)

        # if len(df.query(f'premium > {b}')) > threshold:

df.query(f'premium > {premium_threshold_5_pct}').sort_values(by=['date', 'ms_of_day'])

df.query(f'premium > {premium_threshold_2_pct}').tail(30)[columns]

df[columns]

symbols

len(symbols)

# ----------------------------------------------------------------------

len(df)

def find_premium_threshold_alt(df, pct):
    # sorted_premiums = df['premium'].sort_values(ascending=False).values
    sorted_premiums = df['premium'].sort_values().values
    total_rows = len(sorted_premiums)
    target_rows = total_rows * (pct / 100)

    # left, right = 0, total_rows - 1

    left = 0
    right = total_rows - 1

    while left <= right:
        mid = (left + right) // 2
        if mid < target_rows:
            right = mid - 1
        else:
            left = mid + 1

    return sorted_premiums[right]

find_premium_threshold(df, 5)

find_premium_threshold_alt(df, 5)

# ----------------------------------------------------------------------

sorted = df['premium'].sort_values(ascending=False)

i = int((5 / 100) * len(sorted))

sorted.iloc[i]

# def find_premium_threshold_alt(df, pct):
#     sorted = df['premium'].sort_values(ascending=False)
#     i = int((pct / 100) * len(sorted))
#     return sorted.iloc[i]

find_premium_threshold(df, 2)
find_premium_threshold_alt(df, 2)
# ----------------------------------------------------------------------
ls = []

for symbol in symbols:
    print(symbol)

    df = load_trades(symbol)

    df['size'] = df['size'].astype(int)

    df['premium'] = df['size'] * df['price'] * 100

    df['premium'] = df['premium'].astype(int)    

    premium_threshold_5_pct = find_premium_threshold_alt(df, 5)
    premium_threshold_2_pct = find_premium_threshold_alt(df, 2)

    ls.append([symbol, premium_threshold_5_pct, premium_threshold_2_pct])

df_thresholds = pd.DataFrame(ls, columns=['symbol', 'premium_threshold_5_pct', 'premium_threshold_2_pct'])
# ----------------------------------------------------------------------

df = load_trades('NVDA')

symbol = 'LAC'

df = load_trades(symbol)

df = process_dataframe(df)

df['exp_str'] = df['expiration_'].astype(str)

df['date_str'] = df['date_'].astype(str)

# premium_threshold = df_thresholds.query('symbol == "NVDA"')['premium_threshold_5_pct'].values[0]

# premium_threshold = df_thresholds.query(f'symbol == "{symbol}"')['premium_threshold_5_pct'].values[0]

premium_threshold = df_thresholds.query(f'symbol == "{symbol}"')['premium_threshold_2_pct'].values[0]

df.query(f'premium > {premium_threshold}')[columns]

len(df.query(f'premium > {premium_threshold}').query('date == 20240611')[columns])

df[df['date'] == 20240617]

df['date'].unique()

# df_thresholds[df_thresholds['symbol'] == 'NVDA']

# ----------------------------------------------------------------------

# for symbol in symbols:
#     print(symbol)

#     df = load_trades(symbol)

#     df['size'] = df['size'].astype(int)

#     df['premium'] = df['size'] * df['price'] * 100

#     df['premium'] = df['premium'].astype(int)

#     # premium_threshold = find_premium_threshold_alt(df, 0.01)

#     premium_threshold = find_premium_threshold_alt(df, 0.01)

#     df = df.query(f'premium >= {premium_threshold}')

#     df = process_dataframe(df)

#     df['exp_str'] = df['expiration_'].astype(str)

#     df['date_str'] = df['date_'].astype(str)

#     if len(df.query('date == 20240621')) > 0:
#         df.query('date == 20240621')[columns]






# def test_alt():
#     for symbol in symbols:
#         print(symbol)

#         df = load_trades(symbol)

#         df['size'] = df['size'].astype(int)

#         df['premium'] = df['size'] * df['price'] * 100

#         df['premium'] = df['premium'].astype(int)

#         # premium_threshold = find_premium_threshold_alt(df, 0.01)

#         premium_threshold = find_premium_threshold_alt(df, 0.01)

#         # df = df.query(f'premium >= {premium_threshold}')

#         df = df.query(f'premium >= {premium_threshold}').copy()

#         process_dataframe(df)


# test_alt()













# def unusual_trades():
#     for symbol in symbols:
#         print(symbol)

#         df = load_trades(symbol)

#         df['size'] = df['size'].astype(int)

#         df['premium'] = df['size'] * df['price'] * 100

#         df['premium'] = df['premium'].astype(int)

#         # premium_threshold = find_premium_threshold_alt(df, 0.01)

#         premium_threshold = find_premium_threshold_alt(df, 0.01)

#         df = df.query(f'premium >= {premium_threshold}')

#         df = process_dataframe(df)

#         # print('')

#         # print('***')

#         df['exp_str'] = df['expiration_'].astype(str)

#         df['date_str'] = df['date_'].astype(str)

#         if len(df.query('date == 20240621')) > 0:
#             df.query('date == 20240621')[columns]

# unusual_trades()
        

def unusual_trades(trade_date, pct_threshold):

    for symbol in symbols:
        # print(symbol)

        df = load_trades(symbol)

        df['size'] = df['size'].astype(int)

        df['premium'] = df['size'] * df['price'] * 100

        df['premium'] = df['premium'].astype(int)
        
        premium_threshold = find_premium_threshold_alt(df, pct_threshold)

        df = df.query(f'premium >= {premium_threshold}').copy()

        df = process_dataframe(df)

        df['exp_str'] = df['expiration_'].astype(str)

        df['date_str'] = df['date_'].astype(str)

        result = df.query(f'date == {trade_date}')

        if len(result) > 0:
            print(result[columns])

# unusual_trades(20240621, 0.01)




# def unusual_trades(trade_date, pct_threshold):

#     # dfs = []

#     dfs = pd.DataFrame()

#     for symbol in symbols:
#         # print(symbol)

#         df = load_trades(symbol)

#         df['size'] = df['size'].astype(int)

#         df['premium'] = df['size'] * df['price'] * 100

#         df['premium'] = df['premium'].astype(int)
        
#         premium_threshold = find_premium_threshold_alt(df, pct_threshold)

#         df = df.query(f'premium >= {premium_threshold}').copy()

#         df = process_dataframe(df)

#         df['exp_str'] = df['expiration_'].astype(str)

#         df['date_str'] = df['date_'].astype(str)

#         result = df.query(f'date == {trade_date}')

#         if len(result) > 0:
#             print(result[columns])

#             # dfs.append(result)

#             dfs = pd.concat([dfs, result])

#     return dfs



# result = unusual_trades(20240621, 0.01)

# result[columns]

# with open('unusual_trades_20240621.txt', 'w', encoding='utf-8') as f:
#     f.write(result[columns].to_string())