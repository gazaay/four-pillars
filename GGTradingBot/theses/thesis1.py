from exit_strategies import ExitStrategy

class Thesis1:
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
        self.exit_strategy = ExitStrategy('standard', {'take_profit': 1/80, 'stop_loss': 1/4})

    def evaluate(self, row):
        if len(self.current_trades) >= self.max_concurrent_trades:
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
            return True, row['Close'], 'long'
        if not self.tracking_short and row['RSI'] > 70:
            self.tracking_short = True
        if self.tracking_short and row['RSI'] <= 69:
            self.tracking_short = False
            return True, row['Close'], 'short'

        return False, None, None

    def should_exit(self, entry_price, current_price, trade_type):
        return self.exit_strategy.should_exit(entry_price, current_price, trade_type)

    def update_daily_loss(self, trade):
        if trade['reason'] == 'Stop Loss':
            self.daily_loss += abs(trade['profit']) / trade['entry_price'] * 100
