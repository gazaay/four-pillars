from exit_strategies import ExitStrategy
from trading_system import TradingSystem

# Still use RSI however if the stop loss trigger with a loss. It will do a reversal trade

class Thesis4:
    def __init__(self, symbol, interval, current_time, max_concurrent_trades, daily_loss_threshold):
        self.symbol = symbol
        self.interval = interval
        self.current_time = current_time
        self.max_concurrent_trades = max_concurrent_trades
        self.daily_loss_threshold = daily_loss_threshold
        self.rsi_period = 9  # Define the RSI period here
        self.tracking_long = False
        self.tracking_short = False
        self.daily_loss = 0
        self.current_trades = []
        self.daily_loss_skip = 0
        self.exit_strategy = ExitStrategy('standard', {'take_profit': 1/40, 'stop_loss': 1/1})
        self.bag_average_pricing = 0
        self.trading_system = TradingSystem()
        self.equity_curve = []
        self.initial_capital = 0
        self.DATEORDATETIME = 'Date'
        self.reversal = {
            'ShouldReverse': False,
            'TradeType': None,
            'NumberOfTrades': 0
        }

    def set_date_or_datetime_column (self, date_or_datetime):
        self.DATEORDATETIME = date_or_datetime

    def set_intial_capital(self, initial_capital):
        self.initial_capital = initial_capital

    def set_equity_curve(self, equity_curve):
        self.equity_curve = equity_curve

    def get_latest_equity_total(self):
        if not self.equity_curve:
            raise ValueError("Equity curve is empty")
        return self.equity_curve[-1][1]

    def evaluate(self, row):
        # Check if a reversal is indicated
        if self.reversal['ShouldReverse']:
            reverse_tradetype = self.reversal['TradeType']
            reverse_numberoftrades = self.reversal['NumberOfTrades']
            
            self.trading_system.add_trade(row)
            print(f"Reversal: Total Equity Now {self.get_latest_equity_total()}")

            self.reversal = {
                'ShouldReverse': False,
                'TradeType': None,
                'NumberOfTrades': 0
            }
            print(f"Stop Reversal {row['Close']} {reverse_tradetype} and trades: {reverse_numberoftrades}")
            # return True, row['Close'], reverse_tradetype, 1

            if reverse_tradetype == "long": 
                row['trade_type'] = 'long'
                if self.bag_average_pricing > 0:
                    self.bag_average_pricing = self.calculate_average_entry_price('long')

                if abs(self.bag_average_pricing - row['Close']) < self.bag_average_pricing / 20:
                    print(f"{row[self.DATEORDATETIME]} Bagged average {self.bag_average_pricing} Create Long Trade at {row['Close']} {self.bag_average_pricing / 20}")
                    print("Create Gaps between Bagged Average Pricing and Current Price")
                    return False, None, None, None
                else:
                    print(f"{row[self.DATEORDATETIME]} Bagged average {self.bag_average_pricing} Create Long Trade at {row['Close']} {self.bag_average_pricing / 20}")
                self.trading_system.add_trade(row)
                print(f"Total Equity Now {self.get_latest_equity_total()}")

                qty = 3
                if self.initial_capital < self.get_latest_equity_total():
                    qty = self.get_latest_equity_total() // self.initial_capital
                    print(f"Total Equity Now {self.get_latest_equity_total()} and Initial Capital {self.initial_capital} and Qty {qty}")
                return True, row['Close'], 'long', min(qty, 4)
            if reverse_tradetype == "short": 
                row['trade_type'] = 'short'
                if self.bag_average_pricing > 0:
                    self.bag_average_pricing = self.calculate_average_entry_price('short')

                if abs(self.bag_average_pricing - row['Close']) < self.bag_average_pricing / 120:
                    print(f"{row[self.DATEORDATETIME]} Bagged average {self.bag_average_pricing} Create Short Trade at {row['Close']} {self.bag_average_pricing / 120}")
                    print("Create Gaps between Bagged Average Pricing and Current Price")
                    return False, None, None, None
                else:
                    print(f"{row[self.DATEORDATETIME]} Bagged average {self.bag_average_pricing} Create Short Trade at {row['Close']} {self.bag_average_pricing / 120}")

                self.trading_system.add_trade(row)
                return True, row['Close'], 'short', 1
        # Check if the number of current trades has reached a quarter of the maximum
        if len(self.current_trades) >= self.max_concurrent_trades / 4:
            print(f"Max concurrent trades reached: {len(self.current_trades)}")
            self.bag_average_pricing = self.calculate_average_entry_price('long')
            if self.bag_average_pricing == 0:
                print(f"Bagged average pricing @{self.bag_average_pricing}")
                self.bag_average_pricing = self.calculate_average_entry_price('short')

        # Check if the number of current trades has reached the maximum
        if len(self.current_trades) >= self.max_concurrent_trades:
            self.bag_average_pricing = self.calculate_average_entry_price('long')
            if self.bag_average_pricing == 0:
                print(f"Bagged average pricing @{self.bag_average_pricing}")
                self.bag_average_pricing = self.calculate_average_entry_price('short')
            return False, None, None, None

        # Check if daily loss threshold has been reached
        if self.daily_loss >= self.daily_loss_threshold and self.daily_loss_skip < 8:
            print("Daily loss threshold reached")
            self.daily_loss_skip += 1
            return False, None, None, None

        # Reset daily loss if skip threshold has been reached
        if self.daily_loss >= self.daily_loss_threshold and self.daily_loss_skip >= 8:
            self.daily_loss = 0
            self.daily_loss_skip = 0

        # Check for long trade condition based on RSI
        if not self.tracking_long and row['RSI'] < 30:
            self.tracking_long = True
        if self.tracking_long and row['RSI'] >= 29:
            self.tracking_long = False
            row['trade_type'] = 'long'
            if self.bag_average_pricing > 0:
                self.bag_average_pricing = self.calculate_average_entry_price('long')

            if abs(self.bag_average_pricing - row['Close']) < self.bag_average_pricing / 20:
                print(f"{row[self.DATEORDATETIME]} Bagged average {self.bag_average_pricing} Create Long Trade at {row['Close']} {self.bag_average_pricing / 20}")
                print("Create Gaps between Bagged Average Pricing and Current Price")
                return False, None, None, None
            else:
                print(f"{row[self.DATEORDATETIME]} Bagged average {self.bag_average_pricing} Create Long Trade at {row['Close']} {self.bag_average_pricing / 20}")
            self.trading_system.add_trade(row)
            print(f"Total Equity Now {self.get_latest_equity_total()}")

            qty = 1
            if self.initial_capital < self.get_latest_equity_total():
                qty = self.get_latest_equity_total() // self.initial_capital
                print(f"Total Equity Now {self.get_latest_equity_total()} and Initial Capital {self.initial_capital} and Qty {qty}")
            return True, row['Close'], 'long', min(qty, 4)

        # Check for short trade condition based on RSI
        if not self.tracking_short and row['RSI'] > 70:
            self.tracking_short = True
        if self.tracking_short and row['RSI'] <= 69:
            self.tracking_short = False
            row['trade_type'] = 'short'
            if self.bag_average_pricing > 0:
                self.bag_average_pricing = self.calculate_average_entry_price('short')

            if abs(self.bag_average_pricing - row['Close']) < self.bag_average_pricing / 120:
                print(f"{row[self.DATEORDATETIME]} Bagged average {self.bag_average_pricing} Create Short Trade at {row['Close']} {self.bag_average_pricing / 120}")
                print("Create Gaps between Bagged Average Pricing and Current Price")
                return False, None, None, None
            else:
                print(f"{row[self.DATEORDATETIME]} Bagged average {self.bag_average_pricing} Create Short Trade at {row['Close']} {self.bag_average_pricing / 120}")

            self.trading_system.add_trade(row)
            return True, row['Close'], 'short', 1

        return False, None, None, None

    def should_exit(self, entry_price, current_price, trade_type):
        if self.bag_average_pricing > 0:
            bag_average_pricing_exit_strategy = ExitStrategy('bag_DCA', {
                'take_profit': 1/1200,
                'stop_loss': 1/40,
                'bag_average_pricing': self.bag_average_pricing
            })
            exit_condition, exit_reason, exit_price = bag_average_pricing_exit_strategy.should_exit(self.bag_average_pricing, current_price, trade_type)
            
            if exit_reason == "Stop Loss":
                self.reversal = {
                    'ShouldReverse': True,
                    'TradeType': 'long' if trade_type == 'long' else 'short',
                    'NumberOfTrades': len(self.current_trades)
                }
            
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
        print(f"Average Price {average_entry_price}")
        return average_entry_price