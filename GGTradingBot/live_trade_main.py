import time
from backtest import Backtest
from report import Report
import datetime
from pprint import pprint
import talib

def main():
    thesis_name = 'thesis1'
    initial_capital = 100000
    slippage = 10
    commission = 5
    order_size = 50
    max_concurrent_trades = 4
    daily_loss_threshold = 5

    backtest = Backtest(initial_capital, slippage, commission, order_size, max_concurrent_trades, daily_loss_threshold, thesis_name)

    symbol = '^HSI'
    interval = '5m'  # Using '1m' interval for live data
    current_time = datetime.datetime.now()

    trade_start_date = '2024-06-01'
    trade_end_date = '2024-06-21'

    thesis_instance = backtest.load_thesis(symbol, interval, current_time)
    
    # Run initial backtest
    backtest_summary = backtest.run_backtest(symbol, trade_start_date, trade_end_date, interval, current_time)
    print_summary(backtest_summary)

    # Start live trading
    try:
        while True:
            live_data = backtest.api.get_data(symbol, trade_start_date, datetime.datetime.now().strftime('%Y-%m-%d'), interval)
            # Calculate RSI for the entire dataset
            live_data['RSI'] = talib.RSI(live_data['Close'], timeperiod=thesis_instance.rsi_period)
            latest_row = live_data.iloc[-1]
           
            # Update and evaluate the thesis with the latest row
            backtest.check_exit_conditions(thesis_instance, latest_row, backtest.get_date_column(live_data), [])
            backtest.check_entry_conditions(thesis_instance, latest_row, backtest.get_date_column(live_data))

            # Print live update
            print(f"Processed new data at {latest_row[backtest.get_date_column(live_data)]}")
            time.sleep(300)  # Sleep for 60 seconds before fetching new data
    except KeyboardInterrupt:
        print("Live trading stopped.")

    # Generate and display the final report
    report = Report(backtest.positions, backtest.trade_logs, backtest.api.get_data(symbol, trade_start_date, datetime.datetime.now().strftime('%Y-%m-%d'), interval), backtest.equity_curve, thesis_instance.rsi_period)
    report.plot_trades()

def print_summary(backtest_summary):
    print("\nBacktest Summary:\n")
    print(f"Total Trades: {backtest_summary['total_trades']}")
    print(f"Final Capital: ${backtest_summary['final_capital']:.2f}")
    print(f"Total Return: {backtest_summary['total_return']:.2f}%")
    print(f"Max Drawdown: {backtest_summary['max_drawdown']:.2f}%")
    print(f"Win Rate: {backtest_summary['win_rate']:.2f}%")
    print(f"Annual Performance: {backtest_summary['annual_performance']:.2f}%")
    print(f"Long Trades: {backtest_summary['long_trades']}")
    print(f"Short Trades: {backtest_summary['short_trades']}")
    print(f"Open Trades: {backtest_summary['open_trades']}")
    
    if backtest_summary['top_trade']:
        print("\nTop Trade:")
        pprint(backtest_summary['top_trade'])
    else:
        print("\nTop Trade: None")
    
    if backtest_summary['bottom_trade']:
        print("\nBottom Trade:")
        pprint(backtest_summary['bottom_trade'])
    else:
        print("\nBottom Trade: None")
    
    # print("\nEquity Curve:")
    # print(backtest_summary['equity_curve'])
    
    # print("\nDrawdowns:")
    # print(backtest_summary['drawdowns'])
    
    # print("\nTrade Logs:")
    # backtest.print_trade_logs()

if __name__ == '__main__':
    main()
