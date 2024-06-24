
import pandas as pd
# ----------------------------------------------------------------------
def load_conditions():
    return pd.read_json('TradeConditions.json')

trade_conditions = load_conditions()
# ----------------------------------------------------------------------
def find_premium_threshold_alt(df, pct):
    sorted = df['premium'].sort_values(ascending=False)
    i = int((pct / 100) * len(sorted))
    return sorted.iloc[i]
# ----------------------------------------------------------------------
def process_dataframe(df):
    df['date_'] = pd.to_datetime(df['date'].astype(int).astype(str), format='%Y%m%d')

    df['size'] = df['size'].astype(int)

    df['premium'] = df['size'] * df['price'] * 100

    df['premium'] = df['premium'].astype(int)

    df = pd.merge(df, trade_conditions[['Code', 'Name']], left_on='condition', right_on='Code', how='left')

    df = df.drop(columns=['Code'])

    df = df.rename(columns={'Name': 'condition_name'})

    df['strike_'] = df['strike'] / 100 / 10    

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

    return df

