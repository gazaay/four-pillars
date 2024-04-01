import enum
import time
from datetime import datetime
import asyncio
from database_client import DatabaseClient
from broker_interface import BrokerInterface

class BrokerType(enum.Enum):
    IB = 1
    FUTU = 2

# Initialize your database and broker interfaces
database_client = DatabaseClient()
broker_interface = BrokerInterface()

# Broker switching mechanism (example)
def switch_broker(broker_type):
    if broker_type == BrokerType.IB:
        # Initialize IB specific settings
        pass
    elif broker_type == BrokerType.FUTU:
        # Initialize Futu specific settings
        pass

async def poll_ticker(symbol):
    while True:
        # Poll ticker value from the broker
        # price = broker_interface.get_ticker_price(symbol)
        price = broker_interface.get_forex_price(symbol)
        print(f"Real-time price of {symbol}: {price}")
        # Save ticker value to database
        # database_client.save_ticker_price(symbol, price)
        await asyncio.sleep(5)  # Wait for 5 seconds before the next poll

async def check_strategy(symbol):
    while True:
        # This function runs every hour to check and execute the strategy
        strategy = database_client.get_trade_strategy(symbol, 'stop_reversal')
        if strategy['status'] == 'active':
            execute_strategy(strategy)
        await asyncio.sleep(3600)  # Wait for 1 hour before checking again
        # Initialize the client
        db_client = DatabaseClient()

        # Test a method, e.g., fetching configuration
        datat = db_client.get_price_action(symbol,'2023-02-20', '2024-03-27')
        print(f"First Entry Point - {datat['first_entry_point'].iloc[0]}")
        print(f"Second Entry Point - {datat['second_defence_entry_point'].iloc[0]}")
        print(f"Thrid Entry Point - {datat['third_defence_entry_point'].iloc[0]}")
        print(f"Number of Contracts - {datat['number_of_contracts'].iloc[0]}")
        print(f"Action - {datat['action'].iloc[0]}")
        print(f"First Exit Point - {datat['first_exit_point'].iloc[0]}")
        print(f"Second Exit Point - {datat['second_exit_point'].iloc[0]}")
        print(f"Third Exit Point - {datat['third_exit_point'].iloc[0]}")
        print(f"Symbol - {datat['symbol'].iloc[0]}")
   

def execute_strategy(strategy):
    # Extract strategy details from the database
    # Implement the logic for entry points, exit points, and defensive entries
    print("Executing strategy...")
    pass

def main():
    symbol = 'AUDJPY'  # Example ticker symbol
    broker_type = BrokerType.IB  # Example broker
    switch_broker(broker_type)
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(poll_ticker(symbol))
        asyncio.ensure_future(check_strategy(symbol))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
