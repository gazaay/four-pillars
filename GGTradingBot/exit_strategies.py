class ExitStrategy:
    def __init__(self, strategy_name, params):
        self.strategy_name = strategy_name
        self.params = params

    def should_exit(self, entry_price, current_price, trade_type):
        exit_condition = False
        exit_reason = ''
        exit_price = current_price
        long_target_price = entry_price * (1 + self.params.get('take_profit'))
        long_target_stop_loss = entry_price * (1 - self.params.get('stop_loss'))
        short_target_price = entry_price * (1 - self.params.get('take_profit'))
        short_target_stop_loss = entry_price * (1 + self.params.get('stop_loss'))
        # print(f"Long Target Price {long_target_price} and Long Target Stop Loss {long_target_stop_loss} and Short Target Price {short_target_price} and Short Target Stop Loss {short_target_stop_loss}")
        if self.strategy_name == 'bag_DCA':
            # Add ATR trailing logic
                        # Standard exit strategy logic
            # print(f"Checking with DCA Entry Price @{entry_price} and Current Price @{current_price} and Target Price {target_price} and Target Stop Loss {target_stop_loss} and Trade Type {trade_type}")
            if trade_type == 'long':
                if current_price >= long_target_price:
                    exit_condition = True
                    exit_reason = 'Take Profit'
                elif current_price <= long_target_stop_loss:
                    exit_condition = True
                    exit_reason =  'Stop Loss'
            elif trade_type == 'short':
                if current_price <= short_target_price:
                    exit_condition = True
                    exit_reason = 'Take Profit'
                elif current_price >= short_target_stop_loss:
                    exit_condition = True
                    exit_reason = 'Stop Loss'
            pass
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
