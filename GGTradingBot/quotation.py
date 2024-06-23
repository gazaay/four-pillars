# quotation.py

from broker_api import BrokerAPI

class Quotation:
    def __init__(self, api_key):
        self.api = BrokerAPI(api_key)

    def get_current_price(self, symbol):
        return self.api.get_quotation(symbol)
