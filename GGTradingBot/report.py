import matplotlib.pyplot as plt
import pandas as pd
import talib

class Report:
    def __init__(self, positions, trades, data, equity_curve, rsi_period):
        self.positions = positions
        self.trades = trades
        self.data = data
        self.equity_curve = self.align_equity_curve_with_data(equity_curve, self.data[self.get_date_column(self.data)])
        self.rsi_period = rsi_period  # Use RSI period from Thesis1

    def plot_trades(self):
        date_column = self.get_date_column(self.data)
        
        # Ensure RSI is calculated
        if 'RSI' not in self.data.columns:
            self.data['RSI'] = talib.RSI(self.data['Close'], timeperiod=self.rsi_period )
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(15, 15), sharex=True)

        # Plot close price on ax1
        ax1.plot(self.data[date_column], self.data['Close'], label='HSI Close Price', color='black')
        long_signals = [trade for trade in self.trades if trade['type'] == 'long']
        short_signals = [trade for trade in self.trades if trade['type'] == 'short']

        # Plot long entry and exit signals on ax1
        ax1.plot([trade['entry_date'] for trade in long_signals], 
                 [trade['entry_price'] for trade in long_signals], 
                 '^', markersize=10, color='green', lw=0, label='Buy Signal')
        ax1.plot([trade['exit_date'] for trade in long_signals], 
                 [trade['exit_price'] for trade in long_signals], 
                 'v', markersize=10, color='red', lw=0, label='Sell Signal')

        # Plot short entry and exit signals on ax1
        ax1.plot([trade['entry_date'] for trade in short_signals], 
                 [trade['entry_price'] for trade in short_signals], 
                 'v', markersize=10, color='purple', lw=0, label='Short Entry Signal')
        ax1.plot([trade['exit_date'] for trade in short_signals], 
                 [trade['exit_price'] for trade in short_signals], 
                 '^', markersize=10, color='brown', lw=0, label='Short Exit Signal')
        
        for trade in self.trades:
            ax1.plot([trade['entry_date'], trade['exit_date']], 
                     [trade['entry_price'], trade['exit_price']], 
                     '--', color='grey')
        
        # Plot positions that are still open
        open_long_positions = [position for position in self.positions if position['trade_type'] == 'long']
        open_short_positions = [position for position in self.positions if position['trade_type'] == 'short']
        
        # Plot open long positions on ax1
        ax1.plot([position['entry_date'] for position in open_long_positions], 
                 [position['entry_price'] for position in open_long_positions], 
                 'o', markersize=10, color='blue', lw=0, label='Open Long Position')
        
        # Plot open short positions on ax1
        ax1.plot([position['entry_date'] for position in open_short_positions], 
                 [position['entry_price'] for position in open_short_positions], 
                 'x', markersize=10, color='orange', lw=0, label='Open Short Position')

        # Plot RSI on ax2
        ax2.plot(self.data[date_column], self.data['RSI'], label='RSI', color='blue')
        ax2.axhline(y=30, color='red', linestyle='--')
        ax2.axhline(y=70, color='red', linestyle='--')

        # Plot equity curve on ax3
        ax3.plot(self.data[date_column], self.equity_curve, label='Equity Curve', color='blue')

        # Set labels and legend
        ax1.set_title('HSI Close Price with Buy and Sell Signals')
        ax1.set_ylabel('Close Price')
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        ax2.set_title('RSI')
        ax2.set_ylabel('RSI')
        ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        ax3.set_title('Equity Curve')
        ax3.set_ylabel('Equity')
        ax3.set_xlabel('Date')
        ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        plt.show()

    def align_equity_curve_with_data(self, equity_curve, date_column):
        aligned_equity_curve = []

        equity_index = 0
        for i, date in enumerate(date_column):
            if equity_index < len(equity_curve):
                aligned_equity_curve.append(equity_curve[equity_index])
                equity_index += 1
            else:
                aligned_equity_curve.append(equity_curve[-1])

        return aligned_equity_curve

    def get_date_column(self, data):
        if 'Datetime' in data.columns:
            return 'Datetime'
        elif 'Date' in data.columns:
            return 'Date'
        else:
            raise ValueError("Data does not contain 'Datetime' or 'Date' columns.")
