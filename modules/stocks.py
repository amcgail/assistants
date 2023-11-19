from ..common import * 
import requests 
class StockTickerValue(Module): 
    description = "This module fetches the current value of a given stock ticker." 
    name = "stock_ticker_value" 
    goal = "to fetch the current value of a given stock ticker." 
    params = """ { 'ticker': 'AAPL' } """ 

    def execute_it(self, args): 
        ticker = args['ticker'] 
        url = f"https://api.stockmarket.com/tickers/{ticker}/value" 
        try: 
            response = requests.get(url) 
            if response.status_code == 200: 
                value = response.json()['value'] 
                return value
            else:
                raise Exception(f"Error! Non-200 HTTP status: {response.status_code}")
        except requests.exceptions.RequestException as e: 
            raise