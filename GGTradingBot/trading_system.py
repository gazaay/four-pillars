import uuid

class TradingSystem:
    def __init__(self):
        self.current_trades = []

    def add_trade(self, row):
        trade_id = str(uuid.uuid4())  # Generate a UUID and convert it to a string
        self.current_trades.append({
            'trade_id': trade_id,
            'entry_price': row['Close'],
            'entry_date': row['Date'],
            'trade_type': 'long'
        })

    def calculate_average_entry_price(self):
        if not self.current_trades:
            return 0
        
        average_entry_price = sum(map(lambda x: x['entry_price'], self.current_trades)) / len(self.current_trades)
        print(f"Average entry price: {average_entry_price}")
        return average_entry_price