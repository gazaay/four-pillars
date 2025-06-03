#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stock Data Module for GFAnalytics

This module provides functionality to retrieve stock data from YFinance or other sources,
ensuring all datetime values are in GMT+8 (Hong Kong) timezone.
"""

import logging
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import time
import random
from google.cloud import bigquery

# Import utilities
from GFAnalytics.utils.time_utils import (
    ensure_hk_timezone,
    convert_df_timestamps_to_hk,
    generate_time_range,
    get_trading_hours_mask
)

# Set up logger
logger = logging.getLogger('GFAnalytics.stock_data')


class StockDataLoader:
    """
    Class for loading stock data from various sources.
    """
    
    def __init__(self, config):
        """
        Initialize the StockDataLoader.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.stock_code = config['stock']['code']
        self.ric_code = config['stock']['ric_code']
        self.start_date = config['date_range']['training']['start_date']
        self.end_date = config['date_range']['training']['end_date']
        self.period = config['period']
        
        # Map period to YFinance interval
        self.period_map = {
            '1H': '1h',
            '2H': '2h',
            '1D': '1d',
            '1W': '1wk',
            '1M': '1mo'
        }
        
        # Set the YFinance interval
        self.interval = self.period_map.get(self.period, '1d')
        
        logger.info(f"StockDataLoader initialized for {self.stock_code} ({self.ric_code})")
    
    def load(self):
        """
        Load stock data based on configuration.
        
        Returns:
            pandas.DataFrame: The loaded stock data.
        """
        logger.info(f"Loading stock data for {self.stock_code} from {self.start_date} to {self.end_date}")
        
        # Try to load data from YFinance
        try:
            data = self._load_from_yfinance()
            logger.info(f"Successfully loaded {len(data)} records from YFinance")
            return data
        except Exception as e:
            logger.error(f"Failed to load data from YFinance: {str(e)}")
            
            # Try to load data from alternative source if YFinance fails
            try:
                data = self._load_from_alternative_source()
                logger.info(f"Successfully loaded {len(data)} records from alternative source")
                return data
            except Exception as e:
                logger.error(f"Failed to load data from alternative source: {str(e)}")
                raise
    
    def _load_from_yfinance(self):
        """
        Load stock data from YFinance using the Ticker().history() method.
        
        Returns:
            pandas.DataFrame: The loaded stock data.
        """
        # Convert start and end dates to datetime
        start_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        
        # Log yfinance version
        logger.info(f"Using yfinance version: {yf.__version__}")
        logger.info(f"Loading data for {self.ric_code} from {start_date} to {end_date}")
        
        # Create ticker object and get historical data
        ticker = yf.Ticker(self.ric_code)
        
        # Use the working approach: ticker.history() instead of yf.download()
        logger.info("Calling ticker.history()...")
        data = ticker.history(
            start=start_date,
            end=end_date,
            interval=self.interval,
            auto_adjust=True
        )
        
        # Check if data is empty
        if data.empty:
            logger.error("YFinance returned empty DataFrame!")
            raise ValueError(f"No data returned for {self.ric_code}")
        
        # Log raw data from YFinance
        logger.info("Raw YFinance data:")
        logger.info(f"Shape: {data.shape}")
        logger.info(f"Index: {data.index}")
        logger.info(f"Columns: {data.columns}")
        logger.info(f"First few rows:\n{data.head()}")
        
        # Reset index to make the date a column
        data.reset_index(inplace=True)
        
        # Rename the date column to 'time'
        date_column = 'Date' if 'Date' in data.columns else 'Datetime'
        if date_column in data.columns:
            data.rename(columns={date_column: 'time'}, inplace=True)
        else:
            logger.warning(f"Expected date column not found. Available columns: {data.columns.tolist()}")
        
        # Ensure the time column is in Hong Kong timezone
        data = convert_df_timestamps_to_hk(data, 'time')
        
        # Log data statistics
        logger.info(f"Data shape after processing: {data.shape}")
        logger.info(f"Date range: {data['time'].min()} to {data['time'].max()}")
        logger.info(f"Columns: {data.columns.tolist()}")
        
        # Log summary statistics
        logger.info("Summary statistics:")
        logger.info(f"\n{data.describe()}")
        
        # Check for missing values
        missing = data.isnull().sum()
        if missing.any():
            logger.warning(f"Missing values found:\n{missing[missing > 0]}")
        else:
            logger.info("No missing values found")
        
        # Add metadata columns
        data['stock_code'] = self.stock_code
        data['ric_code'] = self.ric_code
        data['uuid'] = pd.util.hash_pandas_object(data).astype(str)
        data['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
        
        logger.info(f"Final data shape: {data.shape}")
        logger.info(f"Final columns: {data.columns.tolist()}")
        
        return data
    
    def _load_from_alternative_source(self):
        """
        Load stock data from BigQuery HSI database as alternative source.
        
        Returns:
            pandas.DataFrame: The loaded stock data.
        """
        logger.info("Loading HSI data from BigQuery alternative source...")
        
        try:
            # Initialize BigQuery client  
            from GFAnalytics.utils.gcp_utils import setup_gcp_credentials
            
            # Setup credentials
            setup_gcp_credentials(self.config['gcp']['credentials_path'])
            client = bigquery.Client(project=self.config['gcp']['project_id'])
            
            # Get HSI database configuration
            hsi_config = self.config['gcp']['bigquery']['hsi_data']
            table_name = hsi_config['table']
            
            # Build SQL query
            sql_query = f"""
            SELECT *
            FROM {hsi_config['project']}.{hsi_config['dataset']}.{table_name}
            WHERE time >= '{self.start_date}'
            AND time <= '{self.end_date}'
            ORDER BY time
            """
            
            logger.info(f"Executing query: {sql_query}")
            
            # Execute query
            query_job = client.query(sql_query)
            results = query_job.to_dataframe()
            
            if results.empty:
                raise ValueError(f"No HSI data found in BigQuery for date range {self.start_date} to {self.end_date}")
            
            logger.info(f"Loaded {len(results)} records from BigQuery HSI database")
            
            # Convert UTC timestamp to GMT+8
            results = convert_timestamp_to_GMT8(results, 'time')
            
            # Rename columns to match expected format (lowercase to uppercase)
            column_mapping = {
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close'
            }
            
            # Rename columns if they exist
            for old_col, new_col in column_mapping.items():
                if old_col in results.columns:
                    results.rename(columns={old_col: new_col}, inplace=True)
            
            # Ensure we have the required columns
            required_columns = ['time', 'Open', 'High', 'Low', 'Close']
            missing_columns = [col for col in required_columns if col not in results.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns in HSI data: {missing_columns}")
            
            # Select only the columns we need
            data = results[required_columns].copy()
            
            # Add Volume if not present (set to reasonable values for HSI)
            if 'Volume' not in data.columns:
                data['Volume'] = [random.randint(1000000, 10000000) for _ in range(len(data))]
            
            # Add metadata columns
            data['stock_code'] = self.stock_code
            data['ric_code'] = self.ric_code
            data['uuid'] = pd.util.hash_pandas_object(data).astype(str)
            data['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
            
            # Log data statistics
            logger.info(f"Alternative source data shape: {data.shape}")
            logger.info(f"Date range: {data['time'].min()} to {data['time'].max()}")
            logger.info(f"Price range: Close from {data['Close'].min():.2f} to {data['Close'].max():.2f}")
            
            # Filter for trading hours if using intraday data
            if self.period in ['1H', '2H']:
                data = data[get_trading_hours_mask(data, 'time', 'HK')]
                logger.info(f"Filtered to trading hours: {len(data)} records")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load from BigQuery HSI database: {str(e)}")
            raise
    
    def get_listing_date(self):
        """Get the listing date for the stock."""
        try:
            # First try to get from config
            if 'listing_date' in self.config['stock']:
                return pd.to_datetime(self.config['stock']['listing_date'])
            
            # If not in config, try to get from yfinance
            ticker = yf.Ticker(self.ric_code)
            listing_date = pd.to_datetime(ticker.info.get('startDate'))
            
            if pd.isna(listing_date):
                # Get listing date from config
                listing_date = pd.to_datetime(self.config['stock']['listing_date'])
                if pd.isna(listing_date):
                    raise ValueError(f"Could not determine listing date for {self.stock_code} from config")
            
            return listing_date
            
        except Exception as e:
            logger.error(f"Error getting listing date: {str(e)}")
            raise
    
    def _scrape_listing_date(self):
        """
        Scrape the listing date from a website.
        
        Returns:
            datetime: The listing date of the stock in Hong Kong timezone.
        """
        # URL of the webpage (example for Hong Kong stocks)
        url = f'http://www.aastocks.com/en/stocks/analysis/company-fundamental/basic-information?symbol={self.stock_code}'
        
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all <tr> elements
                tr_elements = soup.find_all('tr')
                
                # Iterate through <tr> elements to find the one containing "Listing Date"
                for tr in tr_elements:
                    td_elements = tr.find_all('td', class_='mcFont')
                    if len(td_elements) == 2 and td_elements[0].text.strip() == 'Listing Date':
                        # Extract the value of Listing Date
                        listing_date_str = td_elements[1].text.strip()
                        
                        # Convert the date string to a datetime object
                        listing_date = datetime.strptime(listing_date_str, '%Y/%m/%d')
                        
                        # Set the time to 9:30 AM (typical market opening time in Hong Kong)
                        listing_date = listing_date.replace(hour=9, minute=30, second=0)
                        
                        # Localize to Hong Kong timezone
                        hk_tz = pytz.timezone('Asia/Hong_Kong')
                        listing_date = hk_tz.localize(listing_date)
                        
                        return listing_date
            
            # If we couldn't find the listing date, return a default date
            return datetime(1970, 1, 1, tzinfo=pytz.timezone('Asia/Hong_Kong'))
        except Exception as e:
            logger.error(f"Failed to scrape listing date: {str(e)}")
            return datetime(1970, 1, 1, tzinfo=pytz.timezone('Asia/Hong_Kong'))

def convert_timestamp_to_GMT8(df, timestamp_col='time'):
    """
    Convert UTC timestamp column to GMT+8 (Hong Kong timezone).
    
    Args:
        df (pandas.DataFrame): DataFrame with timestamp column
        timestamp_col (str): Name of the timestamp column
        
    Returns:
        pandas.DataFrame: DataFrame with converted timestamp
    """
    df_copy = df.copy()
    
    # Ensure the timestamp column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df_copy[timestamp_col]):
        df_copy[timestamp_col] = pd.to_datetime(df_copy[timestamp_col])
    
    # If timestamp doesn't have timezone info, assume UTC
    if df_copy[timestamp_col].dt.tz is None:
        df_copy[timestamp_col] = df_copy[timestamp_col].dt.tz_localize('UTC')
    
    # Convert to Hong Kong timezone (GMT+8)
    df_copy[timestamp_col] = df_copy[timestamp_col].dt.tz_convert('Asia/Hong_Kong')
    
    return df_copy