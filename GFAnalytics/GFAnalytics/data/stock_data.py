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
        Load stock data from YFinance.
        
        Returns:
            pandas.DataFrame: The loaded stock data.
        """
        # Convert start and end dates to datetime
        start_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        # Log yfinance version
        logger.info(f"Using yfinance version: {yf.__version__}")
        # Download data from YFinance
        data = yf.download(
            self.ric_code,
            start=start_date,
            end=end_date,
            interval=self.interval,
            auto_adjust=True
        ).xs(self.ric_code, axis=1, level='Ticker')
        # Log raw data from YFinance
        logger.info("Raw YFinance data:")
        logger.info(f"\nShape: {data.shape}")
        logger.info(f"Index: {data.index}")
        logger.info(f"Columns: {data.columns}")
        logger.info(f"First few rows:\n{data.head()}")
        # Reset index to make the date a column
        data.reset_index(inplace=True)
        
        # Rename the date column to 'time'
        data.rename(columns={'Date': 'time', 'Datetime': 'time'}, inplace=True)
        
        # Ensure the time column is in Hong Kong timezone
        data = convert_df_timestamps_to_hk(data, 'time')
        # Log data statistics
        logger.info(f"Data shape: {data.shape}")
        logger.info(f"Date range: {data['time'].min()} to {data['time'].max()}")
        logger.info(f"Columns: {data.columns.tolist()}")
        
        # Log summary statistics
        logger.info("Summary statistics:")
        logger.info(f"\n{data.describe()}")
        
        # Check for missing values
        missing = data.isnull().sum()
        if missing.any():
            logger.warning(f"Missing values found:\n{missing[missing > 0]}")
        
        # Add stock code column
        data['stock_code'] = self.stock_code
        data['ric_code'] = self.ric_code
        
        # Add a UUID column for tracking
        data['uuid'] = pd.util.hash_pandas_object(data).astype(str)
        
        # Add last modified date
        data['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
        
        return data
    
    def _load_from_alternative_source(self):
        """
        Load stock data from an alternative source if YFinance fails.
        
        Returns:
            pandas.DataFrame: The loaded stock data.
        """
        # This is a placeholder for loading data from an alternative source
        # In a real implementation, this would connect to another data provider
        
        # For now, we'll create a dummy DataFrame with the same structure as YFinance data
        start_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        
        # Generate a date range based on the period
        if self.period == '1D':
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
        elif self.period == '1H':
            dates = pd.date_range(start=start_date, end=end_date, freq='H')
        elif self.period == '2H':
            dates = pd.date_range(start=start_date, end=end_date, freq='2H')
        else:
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create a DataFrame with the date range
        data = pd.DataFrame({'time': dates})
        
        # Add dummy data
        data['Open'] = [random.uniform(100, 200) for _ in range(len(dates))]
        data['High'] = data['Open'] + [random.uniform(0, 10) for _ in range(len(dates))]
        data['Low'] = data['Open'] - [random.uniform(0, 10) for _ in range(len(dates))]
        data['Close'] = [random.uniform(data['Low'].iloc[i], data['High'].iloc[i]) for i in range(len(dates))]
        data['Volume'] = [random.randint(1000, 10000) for _ in range(len(dates))]
        
        # Ensure the time column is in Hong Kong timezone
        data = convert_df_timestamps_to_hk(data, 'time')
        
        # Add stock code column
        data['stock_code'] = self.stock_code
        data['ric_code'] = self.ric_code
        
        # Add a UUID column for tracking
        data['uuid'] = pd.util.hash_pandas_object(data).astype(str)
        
        # Add last modified date
        data['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
        
        # Filter for trading hours if using intraday data
        if self.period in ['1H', '2H']:
            data = data[get_trading_hours_mask(data, 'time', 'HK')]
        
        return data
    
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
                # Default to HSI launch date if not found
                if self.stock_code == 'HSI':
                    listing_date = pd.to_datetime('1969-11-24')
                else:
                    raise ValueError(f"Could not determine listing date for {self.stock_code}")
            
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