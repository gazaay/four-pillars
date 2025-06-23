#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Time Utilities for GFAnalytics

This module provides utility functions for handling time-related operations,
particularly focusing on timezone conversions to ensure all datetime values
are in GMT+8 (Hong Kong) timezone as required by the framework.
"""

import pandas as pd
import pytz
from datetime import datetime, timedelta
import logging

# Configure logging settings
logging.basicConfig(
    level=logging.INFO,  # Set the minimum level for displayed logs
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('gfanalytics.log')  # Log to file
    ]
)

# Create a logger
logger = logging.getLogger(__name__)


def ensure_hk_timezone(dt):
    """
    Ensure a datetime object is in Hong Kong timezone (GMT+8).
    
    Args:
        dt (datetime): The datetime object to convert.
        
    Returns:
        datetime: The datetime object in Hong Kong timezone.
    """
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    # Log the datetime object and its timezone info
    logger.debug(f"Converting datetime: {dt}")
    logger.debug(f"Original timezone: {dt.tzinfo}")
    # If datetime is naive (no timezone info), assume it's UTC and convert
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    
    # Convert to Hong Kong timezone
    return dt.astimezone(hk_tz)


def convert_timestamp_to_hk(timestamp, unit='s'):
    """
    Convert a timestamp to a datetime object in Hong Kong timezone.
    
    Args:
        timestamp (int or float): The timestamp to convert.
        unit (str): The unit of the timestamp ('s' for seconds, 'ms' for milliseconds).
        
    Returns:
        datetime: The datetime object in Hong Kong timezone.
    """
    dt = pd.to_datetime(timestamp, unit=unit, utc=True)
    return ensure_hk_timezone(dt)


def convert_df_timestamps_to_hk(df, timestamp_col='time'):
    """
    Convert timestamp column in a DataFrame to Hong Kong timezone.
    
    Args:
        df (pandas.DataFrame): The DataFrame containing the timestamp column.
        timestamp_col (str): The name of the timestamp column.
        
    Returns:
        pandas.DataFrame: The DataFrame with the timestamp column converted to Hong Kong timezone.
    """
    # Make a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Convert the timestamp column to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df_copy[timestamp_col]):
        df_copy[timestamp_col] = pd.to_datetime(df_copy[timestamp_col], utc=True)
    
    # If the column has timezone info, convert to Hong Kong timezone
    if df_copy[timestamp_col].dt.tz is not None:
        df_copy[timestamp_col] = df_copy[timestamp_col].dt.tz_convert('Asia/Hong_Kong')
    else:
        # If the column doesn't have timezone info, assume it's UTC and convert
        df_copy[timestamp_col] = df_copy[timestamp_col].dt.tz_localize('UTC').dt.tz_convert('Asia/Hong_Kong')
    
    return df_copy


def generate_time_range(start_date, end_date, freq='1D'):
    """
    Generate a time range with the specified frequency in Hong Kong timezone.
    
    Args:
        start_date (str or datetime): The start date of the range.
        end_date (str or datetime): The end date of the range.
        freq (str): The frequency of the time range (e.g., '1H', '2H', '1D').
        
    Returns:
        pandas.DatetimeIndex: A DatetimeIndex with the specified range and frequency.
    """
    # Convert string dates to datetime objects if necessary
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    # Ensure both dates are in Hong Kong timezone
    start_date = ensure_hk_timezone(start_date) if start_date.tzinfo else pytz.timezone('Asia/Hong_Kong').localize(start_date)
    end_date = ensure_hk_timezone(end_date) if end_date.tzinfo else pytz.timezone('Asia/Hong_Kong').localize(end_date)
    
    # Generate the time range
    return pd.date_range(start=start_date, end=end_date, freq=freq, tz='Asia/Hong_Kong')


def get_trading_hours_mask(df, timestamp_col='time', market='HK'):
    """
    Create a mask for trading hours in the specified market.
    
    Args:
        df (pandas.DataFrame): The DataFrame containing the timestamp column.
        timestamp_col (str): The name of the timestamp column.
        market (str): The market to get trading hours for ('HK' for Hong Kong).
        
    Returns:
        pandas.Series: A boolean mask where True indicates trading hours.
    """
    # Ensure the timestamp column is in datetime format with timezone info
    if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        df = convert_df_timestamps_to_hk(df, timestamp_col)
    
    # Define trading hours for different markets
    trading_hours = {
        'HK': {
            'morning_start': 1,
            'morning_end': 12,
            'afternoon_start': 13,
            'afternoon_end': 24,
            'weekdays': [0, 1, 2, 3, 4]  # Monday to Friday
        }
    }
    
    # Get trading hours for the specified market
    hours = trading_hours.get(market, trading_hours['HK'])
    
    # Create masks for morning and afternoon sessions
    morning_mask = (
        (df[timestamp_col].dt.hour >= hours['morning_start']) & 
        (df[timestamp_col].dt.hour < hours['morning_end']) & 
        (df[timestamp_col].dt.dayofweek.isin(hours['weekdays']))
    )
    
    afternoon_mask = (
        (df[timestamp_col].dt.hour >= hours['afternoon_start']) & 
        (df[timestamp_col].dt.hour < hours['afternoon_end']) & 
        (df[timestamp_col].dt.dayofweek.isin(hours['weekdays']))
    )
    
    # Combine masks
    return morning_mask | afternoon_mask


def is_trading_day(dt, market='HK'):
    """
    Check if a given date is a trading day in the specified market.
    
    Args:
        dt (datetime): The date to check.
        market (str): The market to check for ('HK' for Hong Kong).
        
    Returns:
        bool: True if the date is a trading day, False otherwise.
    """
    # Ensure dt is in Hong Kong timezone
    dt = ensure_hk_timezone(dt)
    
    # Define trading days for different markets
    trading_days = {
        'HK': [0, 1, 2, 3, 4]  # Monday to Friday
    }
    
    # Get trading days for the specified market
    days = trading_days.get(market, trading_days['HK'])
    
    # Check if the day of the week is a trading day
    return dt.weekday() in days


def get_next_trading_day(dt, market='HK'):
    """
    Get the next trading day from a given date.
    
    Args:
        dt (datetime): The date to start from.
        market (str): The market to get trading days for ('HK' for Hong Kong).
        
    Returns:
        datetime: The next trading day.
    """
    # Ensure dt is in Hong Kong timezone
    dt = ensure_hk_timezone(dt)
    
    # Add one day
    next_day = dt + timedelta(days=1)
    
    # Keep adding days until we find a trading day
    while not is_trading_day(next_day, market):
        next_day += timedelta(days=1)
    
    return next_day 