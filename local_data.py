from datetime import datetime
from app  import gcp_data
import yfinance as yf
from app  import bazi
import pandas as pd
from datetime import timezone

# Example usage:
symbol_to_query = '00005'  # Replace with the symbol you want to query
result_df = gcp_data.query_stock_info(symbol=symbol_to_query)
print(result_df)