from backtest import Backtest
from report import Report
import datetime
from pprint import pprint

def main():
    thesis_name = 'thesis4'
    initial_capital = 10000
    slippage = 10
    commission = 5
    order_size = 50
    max_concurrent_trades = 10
    daily_loss_threshold = 5

    backtest = Backtest(initial_capital, slippage, commission, order_size, max_concurrent_trades, daily_loss_threshold, thesis_name)

    symbol = '^HSI'
    interval = '1h'  # Change this to '1m', '5m', '15m', '30m', '1h', '4h', '1d', '1wk' for different intervals
    current_time = datetime.datetime.now()
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    trade_start_date = '2024-4-01'
    trade_end_date = current_date

    thesis_instance = backtest.load_thesis(symbol, interval, current_time)
    backtest_summary = backtest.run_backtest(symbol, trade_start_date, trade_end_date, interval, current_time)
    
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
    
    print("\nEquity Curve:")
    print(backtest_summary['equity_curve'])
    
    print("\nDrawdowns:")
    print(backtest_summary['drawdowns'])
    
    print("\nTrade Logs:")
    backtest.print_trade_logs()

    # Generate and display the report
    report = Report(backtest.positions, backtest.trade_logs, backtest.api.get_data(symbol, trade_start_date, trade_end_date, interval), backtest_summary['equity_curve'], thesis_instance.rsi_period)
    report.plot_trades()

if __name__ == '__main__':
    main()
