# trading_actions.py

from broker_api import BrokerAPI

class TradingActions:
    def __init__(self, api_key):
        self.api = BrokerAPI(api_key)

    def buy(self, symbol, quantity, price=None, stop_loss=None):
        self.api.place_order(symbol, 'buy', quantity, price, stop_loss)

    def sell(self, symbol, quantity, price=None):
        self.api.place_order(symbol, 'sell', quantity, price)

    def get_position(self, symbol):
        return self.api.get_position(symbol)

    def close_position(self, symbol):
        self.api.close_position(symbol)
