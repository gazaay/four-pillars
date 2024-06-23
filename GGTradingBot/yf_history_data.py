import yfinance as yf

class YFHistoricalData:
    def __init__(self):
        pass

    def get_data(self, symbol, start_date, end_date, interval='1d'):
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        data.reset_index(inplace=True)
        # print(data)
        return data
