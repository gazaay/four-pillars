import importlib
import pandas as pd
from yf_history_data import YFHistoricalData
import talib
from pprint import pprint

class Backtest:
    def __init__(self, initial_capital, slippage, commission, order_size, max_concurrent_trades, daily_loss_threshold, thesis_name):
        self.api = YFHistoricalData()
        self.initial_capital = initial_capital
        self.slippage = slippage
        self.commission = commission
        self.order_size = order_size
        self.max_concurrent_trades = max_concurrent_trades
        self.daily_loss_threshold = daily_loss_threshold
        self.thesis_name = thesis_name
        self.trade_logs = []
        self.cash = initial_capital
        self.positions = []
        self.equity_curve = []

    @staticmethod
    def get_date_column(data):
        if 'Datetime' in data.columns:
            return 'Datetime'
        elif 'Date' in data.columns:
            return 'Date'
        else:
            raise ValueError("Data does not contain 'Datetime' or 'Date' columns.")

    def run_backtest(self, symbol, start_date, end_date, interval, current_time):
        thesis_instance = self.load_thesis(symbol, interval, current_time)

        thesis_instance.set_intial_capital(self.initial_capital)

        data = self.api.get_data(symbol, start_date, end_date, interval)
        thesis_instance.set_date_or_datetime_column(self.get_date_column(data))
        trades = []
        equity_curve = []

        # Calculate RSI for the entire dataset
        data['RSI'] = talib.RSI(data['Close'], timeperiod=thesis_instance.rsi_period)

        date_column = self.get_date_column(data)
        thesis_instance.set_equity_curve(self.equity_curve)

        for index, row in data.iterrows():
            current_date = row[date_column]
            self.update_equity_curve(current_date, row['Close'])
            self.check_exit_conditions(thesis_instance, row, date_column, trades)
            self.check_entry_conditions(thesis_instance, row, date_column)

        # Ensure equity curve has an entry for each date in the data
        self.equity_curve = self.align_equity_curve_with_data(self.equity_curve, data[date_column])

        summary = self.generate_summary(trades, self.equity_curve, data)
        return summary

    def load_thesis(self, symbol, interval, current_time):
        # Dynamically load and initialize the thesis class from the theses module
        thesis_module = importlib.import_module(f'theses.{self.thesis_name}')
        thesis_class = getattr(thesis_module, self.thesis_name.capitalize())
        return thesis_class(symbol, interval, current_time, self.max_concurrent_trades, self.daily_loss_threshold)

    def check_exit_conditions(self, thesis_instance, row, date_column, trades):
        for position in self.positions[:]:
            exit_condition, exit_reason, exit_price = thesis_instance.should_exit(position['entry_price'], row['Close'], position['trade_type'])
            if exit_condition:
                print(f"Exit condition met: {exit_reason}, {position['trade_type']} trade at {exit_price}")
                trade = self.exit_trade(row, exit_reason, position, date_column)
                trades.append(trade)
                self.cash += trade['profit']
                self.positions.remove(position)
                thesis_instance.update_daily_loss(trade)
                self.log_trade(trade)

    def check_entry_conditions(self, thesis_instance, row, date_column):
        entry_signal, entry_price, trade_type, qty = thesis_instance.evaluate(row)
        if entry_signal: 
            # If already one position is open, then open another position with the same entry price
            # for position in self.positions[:]:
            #     if position['trade_type'] == trade_type:
            #         print(f"Entry signal detected: {trade_type} trade at {entry_price}")
            #         self.positions.append({'entry_price': entry_price, 'entry_date': row[date_column], 'trade_type': trade_type})
            # print(f"Entry signal detected: {trade_type} trade at {entry_price}")
            # self.positions.append({'entry_price': entry_price, 'entry_date': row[date_column], 'trade_type': trade_type})
            # thesis_instance.current_trades = self.positions

            # Let the thesis to define how many qty to buy 
            # open_trade_count = sum(1 for position in self.positions if position['trade_type'] == trade_type)
            # total_qty = qty * (1 + open_trade_count)

            for _ in range(int(qty)):
                print(f"Entry signal detected: {trade_type} trade at {entry_price}")
                self.positions.append({'entry_price': entry_price, 'entry_date': row[date_column], 'trade_type': trade_type})

            thesis_instance.current_trades = self.positions

    def update_equity_curve(self, current_date, current_price):
        total_value = self.cash + sum(
            (current_price - position['entry_price']) * self.order_size if position['trade_type'] == 'long'
            else (position['entry_price'] - current_price) * self.order_size
            for position in self.positions
        )
        self.equity_curve.append((current_date, total_value))

    def align_equity_curve_with_data(self, equity_curve, date_column):
        equity_dict = dict(equity_curve)
        aligned_equity_curve = [equity_dict.get(date, equity_curve[-1][1]) for date in date_column]
        return aligned_equity_curve

    def exit_trade(self, row, reason, position, date_column):
        # Calculate profit and ticks
        profit, ticks = self.calculate_profit(position['entry_price'], row['Close'], reason, position['trade_type'])
        # Calculate days holding
        entry_date = position['entry_date']
        exit_date = row[date_column]
        days_holding = (exit_date - entry_date).days if isinstance(exit_date, pd.Timestamp) else (pd.to_datetime(exit_date) - pd.to_datetime(entry_date)).days
        trade = {
            'entry_date': entry_date,
            'entry_price': position['entry_price'],
            'exit_date': exit_date,
            'exit_price': row['Close'],
            'profit': profit,
            'ticks': ticks,
            'days_holding': days_holding,
            'type': position['trade_type'],
            'reason': reason
        }
        return trade

    def calculate_profit(self, entry_price, exit_price, reason, trade_type):
        # Calculate profit, include slippage and commission
        price_change = exit_price - entry_price
        if trade_type == 'short':
            price_change = -price_change
        profit = (price_change * self.order_size) - self.slippage - self.commission
        ticks = price_change
        return profit, ticks

    def log_trade(self, trade):
        self.trade_logs.append(trade)

    def print_trade_logs(self):
        if not self.trade_logs:
            print("No trades were made.")
            return
        for trade in self.trade_logs:
            print(f"Trade executed: Entry Date: {trade['entry_date']}, Entry Price: {trade['entry_price']}, "
                  f"Exit Date: {trade['exit_date']}, Exit Price: {trade['exit_price']}, "
                  f"Profit: {trade['profit']}, Ticks: {trade['ticks']}, Days Holding: {trade['days_holding']}, "
                  f"Type: {trade['type']}, Reason: {trade['reason']}")

    def generate_summary(self, trades, equity_curve, data):
        total_return = (equity_curve[-1] - self.initial_capital) / self.initial_capital * 100
        drawdowns = self.calculate_drawdowns(equity_curve)
        max_drawdown = min(drawdowns) if drawdowns else 0
        win_rate = sum(1 for trade in trades if trade['profit'] > 0) / len(trades) * 100 if trades else 0
        annual_performance = self.calculate_annual_performance(equity_curve, data) if len(equity_curve) > 1 else 0
        long_trades = [trade for trade in trades if trade['type'] == 'long']
        short_trades = [trade for trade in trades if trade['type'] == 'short']
        top_trade = max(trades, key=lambda x: x['profit']) if trades else None
        bottom_trade = min(trades, key=lambda x: x['profit']) if trades else None

        # Calculate the number of open trades that did not exit
        open_trades = len(self.positions)

        return {
            'total_trades': len(trades),
            'final_capital': equity_curve[-1],
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'annual_performance': annual_performance,
            'long_trades': len(long_trades),
            'short_trades': len(short_trades),
            'top_trade': top_trade,
            'bottom_trade': bottom_trade,
            'equity_curve': equity_curve,
            'drawdowns': drawdowns,
            'open_trades': open_trades  # Add this line to include open trades in the summary
        }

    def calculate_drawdowns(self, equity_curve):
        peaks = [max(equity_curve[:i+1]) for i in range(len(equity_curve))]
        drawdowns = [(equity - peak) / peak * 100 for equity, peak in zip(equity_curve, peaks)]
        return drawdowns

    def calculate_annual_performance(self, equity_curve, data):
        date_column = self.get_date_column(data)
        num_years = (data[date_column].iloc[-1] - data[date_column].iloc[0]).days / 365.25
        annual_return = (equity_curve[-1] / self.initial_capital) ** (1 / num_years) - 1
        return annual_return * 100
