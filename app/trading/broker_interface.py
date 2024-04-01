from ib_insync import IB, Stock, MarketOrder, util
from ib_insync import Forex

class BrokerInterface:
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        """
        Initializes the connection to Interactive Brokers.

        Parameters:
        - host (str): The hostname where IB Gateway or TWS is running (usually localhost).
        - port (int): The port on which IB Gateway or TWS is listening for API connections.
        - clientId (int): An identifier for the API client. Each running client should have a unique ID.
        """
        self.ib = IB()
        self.host = host
        self.port = port
        self.clientId = clientId

    def connect(self):
        """Connects to the Interactive Brokers API."""
        self.ib.connect(self.host, self.port, clientId=self.clientId)

    def disconnect(self):
        """Disconnects from the Interactive Brokers API."""
        self.ib.disconnect()

    def isConnected(self):
        """Checks if the connection to Interactive Brokers is active."""
        return self.ib.isConnected()
    
    def get_ticker_price(self, symbol):
        """
        Fetches the current market price of a symbol.

        Parameters:
        - symbol (str): The ticker symbol of the stock.

        Returns:
        - float: The current market price of the stock.
        """
        contract = Stock(symbol, 'SMART', 'USD')
        self.ib.reqMarketDataType(1)  # Live data
        ticker = self.ib.reqMktData(contract)
        self.ib.sleep(2)  # Wait for the data to be updated
        return ticker.marketPrice()
    
    def get_forex_price(self, symbol):
        formatted_symbol = symbol.replace(".", "")  # Ensure correct format
        contract = Forex(formatted_symbol)
        self.ib.reqMarketDataType(1)  # Request live data
        ticker = self.ib.reqMktData(contract)
        self.ib.sleep(2)  # Wait for the data to be updated

        # Handle potential 'nan' values
        price = (ticker.bid + ticker.ask) / 2 if ticker.bid and ticker.ask else None
        if price is not None:
            return price
        else:
            print(f"Could not fetch real-time price for {symbol}. Please check your market data subscriptions and connection.")
            return None
    

    def get_fx_price(self, symbol):
        """
        Fetches the current market price of a forex symbol.

        Parameters:
        - symbol (str): The ticker symbol of the forex pair, formatted as "base.quote", e.g., "AUD.JPY".

        Returns:
        - float: The current market price of the forex pair.
        """
        # Use Forex contract for currency pairs
        contract = Forex(symbol)
        self.ib.reqMarketDataType(1)  # Request live data
        ticker = self.ib.reqMktData(contract)
        self.ib.sleep(2)  # Wait for the data to be updated
        
        # Use 'midpoint' for forex or check if 'bid' and 'ask' are needed
        return (ticker.bid + ticker.ask) / 2 if ticker.bid and ticker.ask else None

    def place_order(self, symbol, qty, action):
        """
        Places a market order.

        Parameters:
        - symbol (str): The ticker symbol of the stock.
        - qty (int): Quantity of the stock to buy/sell.
        - action (str): 'BUY' or 'SELL'.
        """
        contract = Stock(symbol, 'SMART', 'USD')
        order = MarketOrder(action, qty)
        trade = self.ib.placeOrder(contract, order)
        return trade
    
    def place_fx_order(self, symbol, qty, action):
        """
        Places a market order.

        Parameters:
        - symbol (str): The ticker symbol of the stock.
        - qty (int): Quantity of the stock to buy/sell.
        - action (str): 'BUY' or 'SELL'.
        """
        contract = Forex(symbol)
        order = MarketOrder(action, qty)
        trade = self.ib.placeOrder(contract, order)
        return trade

# Example Usage
if __name__ == "__main__":
    broker = BrokerInterface()
    broker.connect()
    print(broker.get_ticker_price('AAPL'))
    broker.place_order('AAPL', 1, 'BUY')
    broker.disconnect()
