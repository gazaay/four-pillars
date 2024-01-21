import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from app import finance

historical_data = finance.get_historical_data_UTC('0001.hk', start_date='2022-02-20', end_date='2024-01-20', interval='1h')

# historical_data.index = historical_data.index.tz_convert( 'Asia/Hong_Kong')

# Display the downloaded data
print(historical_data.head(10))