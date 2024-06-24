
import glob
import os
import pandas as pd

def saved_symbols():
    files = glob.glob('pkl/*.pkl')

    files = [file for file in files if '-' not in file]

    files = [os.path.basename(file) for file in files]

    symbols = [os.path.splitext(file)[0] for file in files]

    return symbols

def load_trades(symbol):
    path = f'pkl/{symbol}.pkl'
    return pd.read_pickle(path)