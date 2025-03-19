from datetime import datetime
from app  import finance
import yfinance as yf
from app  import bazi
import pandas as pd
from datetime import timezone

ticker = "HSI.hk"
print (f"time Stamp of HK STock {finance.get_listing_date_timestamp('00007')}")

result = finance.convert_to_hk_time(ticker, 'firstTradeDate', 'timezone', 'chartPreviousClose')
print(result)

# Extract year, month, day, and hour from Converted Timestamp
converted_timestamp = result['EST']
target_year = converted_timestamp.year
target_month = converted_timestamp.month
target_day = converted_timestamp.day
target_hour = converted_timestamp.hour



start_date = f'{target_year}-{target_month}-{target_day}'
print(start_date)
print(converted_timestamp)

time_format = "%Y-%m-%dT%H:%M:%S%z"
parsed_time = converted_timestamp.strftime("%Y-%m-%dT%H:%M:%S")
print(parsed_time)

# Download historical data for AAPL every 2 hours
historical_data = yf.download('AAPL', start='2023-02-20', end='2024-01-20', interval='1h', auto_adjust=True)

historical_data.index = historical_data.index.tz_convert('UTC')

# Display the downloaded data
print(historical_data.head(1).index)

historical_data = finance.get_historical_data_UTC('AAPL', start_date='2023-02-20', end_date='2024-01-20', interval='1h')

historical_data.index = historical_data.index.tz_convert('UTC')

# Display the downloaded data
print(historical_data.head(1).index)



# Call the method to get a list of Hong Kong stock symbols
hk_stock_symbols = finance.get_hk_stock_symbols()

# Display the list of symbols
print(hk_stock_symbols)



# List of Hong Kong stock symbols
hong_kong_stocks = [
    '00001'
]

# Create Tickers instance
hk_tickers = yf.Tickers(hong_kong_stocks)



# Get information about the stocks and convert start time to Hong Kong time
result_objects = []

for symbol, info in hk_tickers.tickers.items():
    try:
        # Convert UTC first trade date to Hong Kong time using the hypothetical function
        first_trade = finance.get_listing_date_timestamp(symbol)
        print(first_trade)
        current_date_time_hk = first_trade


        base_8w = bazi.get_heavenly_branch_ymdh_pillars_current(current_date_time_hk.year, 
                                                            current_date_time_hk.month, 
                                                            current_date_time_hk.day, 
                                                            current_date_time_hk.hour)

        current_hour = base_8w["時"]
        current_day = base_8w["日"]
        negative_current_hour = base_8w["-時"]
        current_month = base_8w["月"]
        current_year = base_8w["年"]
        negative_current_month = base_8w["-月"]


        # Create a result object
        result_object = {
            'Symbol': symbol,
            'First_Trade_Date_UTC': first_trade.astimezone(timezone.utc),
            'First_Trade_Date_HK': first_trade,
            '流時': current_hour,
            '流日': current_day,
            '-流時': negative_current_hour,
            '流月': current_month,
            '流年': current_year,
            '-流月': negative_current_month
        }

        # Append the result object to the list
        result_objects.append(result_object)
    except Exception as e:
        print(f"An error occurred: {e}")
        continue

# Create a DataFrame from the list of result objects
result_df = pd.DataFrame(result_objects)

# Display the DataFrame
print(result_df)

try:
    # Code that may raise an exception
    historical_data = finance.get_historical_data_UTC(hong_kong_stocks[0], start_date='2023-02-20', end_date='2024-01-20', interval='1h')
    
    # Convert index to UTC timezone
    historical_data.index = historical_data.index.tz_convert('UTC')
    
    # Display the index of the first data point
    print("Index of the first data point:", historical_data.index[0])

except Exception as e:
    # Handle the exception
    print("An error occurred:", e)



# URL of the webpage
stock_code = "00002"
# Extract company information
company_info = finance.extract_company_info(stock_code)

print(company_info)
# Print the extracted information
for attribute, value in company_info.items():
    print(f"{attribute}: {value}")