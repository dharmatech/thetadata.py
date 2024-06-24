
Python code to download and visualize data from [ThetaData](https://www.thetadata.net/).

The dashboard is built using [streamlit](https://streamlit.io/).

![image](https://github.com/dharmatech/thetadata.py/assets/20816/830a0a93-a86a-42c0-aa2b-5829d638bcd4)

# Thetadata requirements

You'll need to have the 'Standard' options tier to run all the API calls in these modules.

# Downloading options trades

This will download and store all options trades on 2024-06-24:

    python -m all_stocks_all_trades 20240624

# Chart of options trades (Streamlit application)

    streamlit run thetadata_streamlit.py
    

# Unusual Trades

Generate a list of unusual trades that occurred on 2024-06-21:

    python -m unusual_trades 20240621

For each stock that you have data for, this will filter down to the top 0.01% of trades. If any of these trades occurred on the trade date specified, they'll show up in the resulting report.

The report will be in the file:

    out/unusual_trades_20240621.csv

