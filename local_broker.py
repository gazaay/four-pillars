# Assume BrokerInterface is defined in broker_interface.py
from app.trading.broker_interface import BrokerInterface

def test_broker_interface():
    broker = BrokerInterface()
    broker.connect()
    
    if broker.isConnected():
        print("Successfully connected to Interactive Brokers.")
        
        # Fetch the real-time price of AAPL
        symbol = 'AUD.JPY'
        price = broker.get_forex_price(symbol)
        print(f"Real-time price of {symbol}: {price}")

        # Fetch the real-time price of AAPL
        symbol = 'APPL'
        price = broker.get_ticker_price(symbol)
        print(f"Real-time price of {symbol}: {price}")

        # Fetch the real-time price of AAPL
        symbol = 'HSIH4'
        price = broker.get_ticker_price(symbol)
        print(f"Real-time price of {symbol}: {price}")
        
        # broker.place_fx_order('AUDJPY', 1000, 'BUY')

        # Disconnect after fetching the price
        broker.disconnect()
        print("Disconnected from Interactive Brokers.")
    else:
        print("Failed to connect to Interactive Brokers.")

if __name__ == "__main__":
    test_broker_interface()
