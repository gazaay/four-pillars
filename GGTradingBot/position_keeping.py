# position_keeping.py

from broker_api import BrokerAPI

class PositionKeeping:
    def __init__(self, api_key):
        self.api = BrokerAPI(api_key)

    def get_position(self, symbol):
        return self.api.get_position(symbol)
