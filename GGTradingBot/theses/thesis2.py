from exit_strategies import ExitStrategy
from trading_system import TradingSystem

class Thesis2:
    def __init__(self, symbol, interval, current_time, max_concurrent_trades, daily_loss_threshold):
        self.symbol = symbol
        self.interval = interval
        self.current_time = current_time
        self.max_concurrent_trades = max_concurrent_trades
        self.daily_loss_threshold = daily_loss_threshold
        self.rsi_period = 11  # Define the RSI period here
        self.tracking_long = False
        self.tracking_short = False
        self.daily_loss = 0
        self.current_trades = []
        self.dail_loss_skip = 0
        self.exit_strategy = ExitStrategy('standard', {'take_profit': 1/40, 'stop_loss': 1/1})
        self.bag_average_pricing = 0
        self.trading_system = TradingSystem()

    def evaluate(self, row):
        if len(self.current_trades) >= self.max_concurrent_trades / 3:
            self.bag_average_pricing = self.calculate_average_entry_price('long')
        if len(self.current_trades) >= self.max_concurrent_trades:
            self.bag_average_pricing = self.calculate_average_entry_price('long')
            return False, None, None
        if self.daily_loss >= self.daily_loss_threshold and self.dail_loss_skip < 8:
            print("Daily loss threshold reached")
            self.dail_loss_skip += 1
            return False, None, None
        if self.daily_loss >= self.daily_loss_threshold and self.dail_loss_skip >= 8:
            self.daily_loss = 0
            self.dail_loss_skip = 0
        if not self.tracking_long and row['RSI'] < 30:
            self.tracking_long = True
        if self.tracking_long and row['RSI'] >= 29:
            self.tracking_long = False
            row['trade_type'] = 'long'
            self.trading_system.add_trade(row)
            if self.bag_average_pricing > 0:
                self.bag_average_pricing = self.calculate_average_entry_price('long')
            return True, row['Close'], 'long'
        if not self.tracking_short and row['RSI'] > 70:
            self.tracking_short = True
        if self.tracking_short and row['RSI'] <= 69:
            self.tracking_short = False
            row['trade_type'] = 'short'
            self.trading_system.add_trade(row)
            if self.bag_average_pricing > 0:
                self.bag_average_pricing = self.calculate_average_entry_price('short')
            return True, row['Close'], 'short'

        return False, None, None

    def should_exit(self, entry_price, current_price, trade_type):
        if (self.bag_average_pricing > 0):
            # print(f"Bagged average pricing @{self.bag_average_pricing} and {self.current_trades}")
            bag_average_pricing_exit_strategy = ExitStrategy('bag_DCA', {'take_profit': 1/120, 'stop_loss': 1/0.1, 'bag_average_pricing' : self.bag_average_pricing})
            exit_condition, exit_reason, exit_price =  bag_average_pricing_exit_strategy.should_exit(self.bag_average_pricing, current_price, trade_type) 
            if exit_condition:
                print(f"Exit condition met: {exit_reason}, {trade_type} trade at {exit_price}")
                if len(self.current_trades) <= 1:
                    self.average_entry_price = 0
            return exit_condition, exit_reason, exit_price  
        else:
            return self.exit_strategy.should_exit(entry_price, current_price, trade_type)

    def update_daily_loss(self, trade):
        if trade['reason'] == 'Stop Loss':
            self.daily_loss += abs(trade['profit']) / trade['entry_price'] * 100

    def calculate_average_entry_price(self, trade_type):
        filtered_positions = list(filter(lambda x: x['trade_type'] == trade_type, self.current_trades))
        
        if not filtered_positions:
            return 0
        
        average_entry_price = sum(map(lambda x: x['entry_price'], filtered_positions)) / len(filtered_positions)
        print(average_entry_price)
        return average_entry_price