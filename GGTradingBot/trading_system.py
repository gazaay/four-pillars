import uuid
from backtest import Backtest
import pandas as pd

class TradingSystem:
    def __init__(self):
        self.current_trades = []

    def add_trade(self, row):
        # Convert row to DataFrame if it's a dictionary or Series
        if isinstance(row, (pd.Series, dict)):
            data = pd.DataFrame([row])
        else:
            raise ValueError("Row must be a dictionary or pandas Series")

        # Use the static method
        date_column = Backtest.get_date_column(data)
        trade_id = str(uuid.uuid4())  # Generate a UUID and convert it to a string
        self.current_trades.append({
            'trade_id': trade_id,
            'entry_price': row['Close'],
            'entry_date': row[date_column],
            'trade_type': 'long'
        })

    def calculate_average_entry_price(self):
        if not self.current_trades:
            return 0
        
        average_entry_price = sum(map(lambda x: x['entry_price'], self.current_trades)) / len(self.current_trades)
        print(f"Average entry price: {average_entry_price}")
        return average_entry_price