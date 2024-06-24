import requests
import pandas as pd

def list_roots_stock():

    url = 'http://127.0.0.1:25510/v2/list/roots/stock'

    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    roots = pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])
     
    return roots

def list_roots_option():

    url = 'http://127.0.0.1:25510/v2/list/roots/option'

    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    roots = pd.DataFrame(response.json()['response'], columns=response.json()['header']['format'])
     
    return roots
