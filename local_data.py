from datetime import datetime
from app  import gcp_data
import yfinance as yf
from app  import bazi
import pandas as pd
from datetime import timezone
from app.trading.database_client import DatabaseClient

# Initialize the client
db_client = DatabaseClient()

# Test a method, e.g., fetching configuration
datat = db_client.get_price_action('AAPL','2023-02-20', '2024-03-27')
print(datat['first_entry_point'].iloc[0])
print(datat['second_defence_entry_point'].iloc[0])
print(datat['third_defence_entry_point'].iloc[0])
print(datat['number_of_contracts'].iloc[0])
print(datat['action'].iloc[0])
print(datat['first_exit_point'].iloc[0])
print(datat['second_exit_point'].iloc[0])
print(datat['third_exit_point'].iloc[0])
print(datat['symbol'].iloc[0])