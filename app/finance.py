import pandas as pd
import pytz
from datetime import datetime, timedelta
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz


def convert_to_hk_time(ticker, timestamp_attribute, timezone_attribute, enquiry):
    """
    Convert a timestamp in a given data set to Hong Kong Time (GMT+8).

    Parameters:
    - data: Dictionary containing the data attributes.
    - timestamp_attribute: String, the key for the timestamp attribute in the data.
    - timezone_attribute: String, the key for the timezone attribute in the data.
    - enquiry: String, the specific field to enquire about.

    Returns:
    - Converted timestamp in Hong Kong Time (GMT+8).
    """

    data = yf.Ticker(ticker)

    data = data.history_metadata

    # Extract relevant data
    timestamp = data.get(timestamp_attribute)
    timezone = data.get(timezone_attribute)

    if timestamp is None or timezone is None:
        return "Timestamp or timezone information missing in the provided data."

    # Convert timestamp to datetime object and set the timezone
    timestamp_dt = pd.to_datetime(timestamp, unit='s', utc=True)

    if timezone == "HKT":
      timezone = 'Asia/Hong_Kong'
    # Convert to the specified timezone
    specified_timezone = pytz.timezone(timezone)
    timestamp_converted = timestamp_dt.tz_convert(specified_timezone)

    # Enquire about a specific field
    result = data.get(enquiry)
    # print("Original Regular Market Time:", timestamp_dt)
    # print("Regular Market Time in Hong Kong Time (GMT+8):", timestamp_converted)
    return {
        "UTC": timestamp_dt,
        "EST": timestamp_converted,
        "Enquiry": result
    }

def get_historical_data_UTC(ticker, start_date, end_date, interval):
    """
    Download historical data for a given ticker.

    Parameters:
    - ticker: String, the ticker to download the data for.  
    - start_date: String, the start date of the historical data.
    - end_date: String, the end date of the historical data.
    - interval: String, the interval between each data point.
    """
    historical_data = yf.download(ticker, start=start_date, end=end_date, interval=interval, auto_adjust=True)
    # historical_data.index = historical_data.index.tz_convert('UTC')
    return historical_data

import requests

def get_hk_stock_symbols():
    api_key = "FDD6pAUpzxsv5eukM9dSBAKqrjv9HgYc"
    # URL for the Reference Data API to get a list of stock symbols for Hong Kong
    url = f'https://api.polygon.io/v3/reference/tickers?type=cs&market=stocks&exchange=HKX&apiKey={api_key}'

    # Send a GET request to the API
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract stock symbols from the response (customize based on the API response structure)
        stock_symbols = [ticker['symbol'] for ticker in data['results']]

        return stock_symbols
    else:
        # Print an error message if the request was not successful
        print(f"Error: Unable to retrieve stock symbols. Status code: {response.status_code}")
        return []



import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_listing_date_timestamp(symbol):
    # URL of the webpage
    url = f'http://www.aastocks.com/en/stocks/analysis/company-fundamental/basic-information?symbol={symbol}'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <tr> elements
        tr_elements = soup.find_all('tr')

        # Iterate through <tr> elements to find the one containing "Listing Date"
        for tr in tr_elements:
            td_elements = tr.find_all('td', class_='mcFont')
            if len(td_elements) == 2 and td_elements[0].text.strip() == 'Listing Date':
                # Extract the value of Listing Date
                listing_date_str = td_elements[1].text.strip()

                # Convert the date string to a timestamp in 'Asia/Hong_Kong' timezone
                hong_kong_timezone = pytz.timezone('Asia/Hong_Kong')
                listing_date_timestamp = datetime.strptime(listing_date_str, '%Y/%m/%d').replace(tzinfo=hong_kong_timezone).timestamp()
                # Set the time to 9:30 AM
                listing_datetime = datetime.fromtimestamp(listing_date_timestamp).replace(hour=9, minute=30, second=0, tzinfo=hong_kong_timezone)

                return listing_datetime
                break  # Break out of the loop once Listing Date is found
        else:
            print("Listing Date not found on the webpage.")
    else:
        # Print an error message if the request was not successful
        print(f"Error: Unable to retrieve webpage. Status code: {response.status_code}")

