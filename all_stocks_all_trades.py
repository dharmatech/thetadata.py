
import sys

import api
import update_trades

# Example usage:
#
# python -m .\all_stocks_all_trades 20240624

print('Getting stocks list...')

roots = api.list_roots_option()

print('complete')

trade_date = sys.argv[1]

update_trades.all_stocks_all_trades(trade_date, roots['root'])
