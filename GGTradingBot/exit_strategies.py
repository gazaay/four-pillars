class ExitStrategy:
    def __init__(self, strategy_name, params):
        self.strategy_name = strategy_name
        self.params = params

    def should_exit(self, entry_price, current_price, trade_type):
        exit_condition = False
        exit_reason = ''
        exit_price = current_price

        if self.strategy_name == 'atr_trailing':
            # Add ATR trailing logic
            pass
        elif self.strategy_name == 'time_based':
            # Add time-based exit logic
            pass
        elif self.strategy_name == 'standard':
            # Standard exit strategy logic
            if trade_type == 'long':
                if current_price >= entry_price * (1 + self.params.get('take_profit', 1/80)):
                    exit_condition = True
                    exit_reason = 'Take Profit'
                elif current_price <= entry_price * (1 - self.params.get('stop_loss', 1/4)):
                    exit_condition = True
                    exit_reason = 'Stop Loss'
            elif trade_type == 'short':
                if current_price <= entry_price * (1 - self.params.get('take_profit', 1/80)):
                    exit_condition = True
                    exit_reason = 'Take Profit'
                elif current_price >= entry_price * (1 + self.params.get('stop_loss', 1/4)):
                    exit_condition = True
                    exit_reason = 'Stop Loss'

        return exit_condition, exit_reason, exit_price
