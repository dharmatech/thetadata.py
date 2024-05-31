import os
import glob
import pandas as pd
import streamlit as st
import plotly.express as px
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
def saved_symbols():
    files = glob.glob('pkl/*.pkl')

    files = [file for file in files if '-' not in file]

    files = [os.path.basename(file) for file in files]

    symbols = [os.path.splitext(file)[0] for file in files]

    return symbols

# files = glob.glob('pkl/*.pkl')

# files = [file for file in files if '-' not in file]

# files = [os.path.basename(file) for file in files]

# symbols = [os.path.splitext(file)[0] for file in files]

symbols = saved_symbols()

symbol = st.sidebar.selectbox('Symbol', symbols)

df = load_trades(symbol)
# ----------------------------------------------------------------------

df['date_'] = pd.to_datetime(df['date'].astype(int).astype(str), format='%Y%m%d')

# ----------------------------------------------------------------------
date_min = df['date_'].min()
date_max = df['date_'].max()

start_date = st.sidebar.date_input('Start date', min_value=date_min, max_value=date_max, value=date_min)

start_date = pd.to_datetime(start_date)

df = df[df['date_'] >= start_date]
# ----------------------------------------------------------------------
df['premium'] = df['size'] * df['price'] * 100

df = pd.merge(df, trade_conditions[['Code', 'Name']], left_on='condition', right_on='Code', how='left')

df = df.drop(columns=['Code'])

df = df.rename(columns={'Name': 'condition_name'})

df['strike_'] = df['strike'] / 100 / 10

# ----------
df['ask_sub_price'] = df['ask'] - df['price']

df['price_sub_bid'] = df['price'] - df['bid']

df.loc[df['ask_sub_price'] < df['price_sub_bid'], 'side'] = 'buy'

df.loc[df['ask_sub_price'] > df['price_sub_bid'], 'side'] = 'sell'

df.loc[df['ask_sub_price'].round(3) == df['price_sub_bid'].round(3), 'side'] = 'eq'

df.loc[(df['right'] == 'C') & (df['side'] == 'buy'),  'bb'] = '🟢'
df.loc[(df['right'] == 'C') & (df['side'] == 'sell'), 'bb'] = '🔴'

df.loc[(df['right'] == 'P') & (df['side'] == 'buy'),  'bb'] = '🔴'
df.loc[(df['right'] == 'P') & (df['side'] == 'sell'), 'bb'] = '🟢'


df.loc[(df['right'] == 'C') & (df['side'] == 'buy'),  'bb_'] = 'bullish'
df.loc[(df['right'] == 'C') & (df['side'] == 'sell'), 'bb_'] = 'bearish'
df.loc[(df['right'] == 'P') & (df['side'] == 'buy'),  'bb_'] = 'bearish'
df.loc[(df['right'] == 'P') & (df['side'] == 'sell'), 'bb_'] = 'bullish'

df.loc[(df['side'] == 'eq'), 'bb_'] = 'neutral'

df['ask_bid_diff'] = df['ask'] - df['bid']

df.loc[df['side'] == 'buy',  'bb_confidence'] = (df[df['side'] == 'buy' ]['ask_bid_diff'] - df[df['side'] == 'buy' ]['ask_sub_price']) / df[df['side'] == 'buy' ]['ask_bid_diff']
df.loc[df['side'] == 'sell', 'bb_confidence'] = (df[df['side'] == 'sell']['ask_bid_diff'] - df[df['side'] == 'sell']['price_sub_bid']) / df[df['side'] == 'sell']['ask_bid_diff']

df['bb_confidence'] = df['bb_confidence'].round(3)

df['expiration_'] = pd.to_datetime(df['expiration'].astype(int).astype(str), format='%Y%m%d')

df['ms_of_day_'] = pd.to_timedelta(df['ms_of_day'], unit='ms')

df['datetime'] = df['date_'] + df['ms_of_day_']

df['dte'] = (df['expiration_'] - df['date_']).dt.days

# Convert 'datetime' to string format
df['datetime_str'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
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
# df.columns

# df['condition_name'].unique()

# button to clear cache of load_trades

def clear_cache():
    load_conditions.clear()
    load_trades.clear()

st.button('Clear Cache', on_click=clear_cache)


# df[df['premium'] > 10000000][['premium', 'datetime_str', 'condition_name', 'side']]

# ----------------------------------------------------------------------

# df

# columns_to_drop = ['No data for the specified timeframe and chain. Debug code 1', 'ext_condition1', 'ext_condition2', 'ext_condition3', 'ext_condition4', 'ask_condition', 'bid_condition', 'records_back', 'condition_flags', 'volume_type' ]

# df = df.drop(columns=columns_to_drop)

# df.drop(columns=['bb', 'condition', 'strike', 'sequence', 'date_', 'ms_of_day_', 'datetime', 'expiration_', 'ask_sub_price', 'price_sub_bid', 'dte', 'ask_bid_diff'])

# # df[['date', 'ms_of_day', 'root', 'expiration', 'right', 'bid', 'price', 'ask', 'size', 'condition_name', 'ask_bid_diff']]

# df[['date', 'ms_of_day', 'root', 'expiration', 'right', 'strike_', 'bid', 'price', 'ask', 'ask_bid_diff', 'size', 'premium', 'side', 'bb_', 'bb_confidence', 'condition_name']]

# columns = ['date', 'ms_of_day', 'root', 'expiration', 'right', 'strike_', 'bid', 'price', 'ask', 'ask_bid_diff', 'size', 'premium', 'side', 'bb_', 'bb_confidence', 'condition_name']


# bid = 0.5
# price = 0.51
# ask = 1.0

# df['ask'] - df['bid']



# df[df['side'] == 'buy']['ask_sub_price'] / df[df['side'] == 'buy']['ask_bid_diff']


# (df[df['side'] == 'buy']['ask_bid_diff'] - df[df['side'] == 'buy']['ask_sub_price']) / df[df['side'] == 'buy']['ask_bid_diff']

# df[df['side'] == 'buy']['bb_confidence'] = (df[df['side'] == 'buy']['ask_bid_diff'] - df[df['side'] == 'buy']['ask_sub_price']) / df[df['side'] == 'buy']['ask_bid_diff']



# df.loc[df['ask_sub_price'] < df['price_sub_bid'], 'side'] = 'buy'

# ----------------------------------------------------------------------

# group rows by 'date', 'ms_of_day', 'expiration', 'size'

# result = df.groupby(['date', 'ms_of_day', 'expiration', 'size'])

# result.describe()

# import pprint

# pprint.pprint(result.groups, depth=2)

# result.groups

# type(result.groups)

# for key, value in result.groups.items():
#     print(key, value)

# len(result)

# list(result)[0:10]


# for key, item in list(result)[2000:2300]:
#     if len(item) > 1:
#         print(key)
#         print(result.get_group(key)[columns], "\n\n")



# df[columns]


# result = df.groupby(['date', 'ms_of_day', 'expiration', 'size']).filter(lambda x: len(x) > 1)

# result


# 100000010 // 3
# 100000011 // 3
# 100000012 // 3


# 35616622.0 // 3
# 35616623.0 // 3
# 35616624.0 // 3

# ----------------------------------------------------------------------

# df[columns]

# df[df['premium'] > 1000][columns]

# df.query('premium > 1000000')[columns]

# result = df.query('premium > 500000')[columns].sort_values(by=['date', 'ms_of_day'])

# # for loop through each row in result

# # loop through date in result['date']

# result = df.query('premium > 500000')[columns].sort_values(by=['date', 'ms_of_day'])

# for date in result['date']:    
#     result_ = result[result['date'] == date]

#     if len(result_) > 1:
#         print(date)
#         print(result_)
#         print()

#     result = result[result['date'] != date]






# def is_risk_reversal(row):
#     if row['right'] == 'C' and row['side'] == 'buy':
#         return True
#     elif row['right'] == 'P' and row['side'] == 'sell':
#         return True
#     else:
#         return False

# def is_risk_reversal(rows):
#     if rows['right'].iloc[0] == 'C' and rows['side'].iloc[0] == 'buy':
#         return True
#     elif rows['right'].iloc[0] == 'P' and rows['side'].iloc[0] == 'sell':
#         return True
#     else:
#         return False
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

st.write(f'Potential multi-leg trades')

exclude_gt_4 = st.checkbox('Exclude > 4', value=True)

multi_leg_count = 0

df['exp_str'] = df['expiration_'].astype(str)

df['date_str'] = df['date_'].astype(str)

columns = ['date_str', 'ms_of_day', 'root', 'exp_str', 'right', 'strike_', 'bid', 'price', 'ask', 'ask_bid_diff', 'size', 'premium', 'side', 'bb_', 'bb_confidence', 'condition_name']

# result = df.query('premium > 100000')[columns].sort_values(by=['date', 'ms_of_day'])

# result[columns]

result = df.query('premium > 100000').sort_values(by=['date', 'ms_of_day'])

# date = 20240529.0

for date in result['date']:    

    if multi_leg_count >= 100:
        st.write(f'### {multi_leg_count} multi-leg trades found. Stopping search.')
        break

    result_ = result[result['date'] == date]

    # result_[columns]

    # time = 45842799.0

    if len(result_) > 1:

        # st.write(f'{date}')

        for time in result_['ms_of_day']:

            tmp = pd.DataFrame(result_)

            tmp['diff'] = result_['ms_of_day'] - time

            tmp['diff'] = tmp['diff'].abs()

            tmp = tmp[tmp['diff'] < 4]

            # tmp[columns]

            if len(tmp) > 1:

                if exclude_gt_4 and len(tmp) > 4:
                    continue

                multi_leg_count += 1
                # print(date)
                # st.write(f'### {date}')

                # st.write(f'{date}')

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

                    fig.add_trace(
                        go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines', 
                                   text=[f'{bb_} {right}', f'{bb_} {right}'], hoverinfo='x+y+text+name'))

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
                    
                    fig.add_trace(
                        go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='lines', 
                                   text=[f'{bb_}, {right}', f'{bb_}, {right}'], hoverinfo='x+y+text+name'))
                    
                
                if is_spread(tmp):
                    # print('spread')
                    st.write('spread')

                # print(tmp)
                st.write(tmp[columns])
                # print()

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


st.plotly_chart(fig, use_container_width=True)