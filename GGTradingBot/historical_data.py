# historical_data.py

from broker_api import BrokerAPI

class HistoricalData:
    def __init__(self, api_key):
        self.api = BrokerAPI(api_key)

    def get_data(self, symbol, start_date, end_date):
        return self.api.get_historical_data(symbol, start_date, end_date)


