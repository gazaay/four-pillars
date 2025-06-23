#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YFinance Test Script

This script tests the exact YFinance logic used in GFAnalytics to isolate
any rate limiting or data retrieval issues.
"""

import pandas as pd
import yfinance as yf
import logging
from datetime import datetime
import pytz
import time
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('YFinanceTest')

def test_yfinance_exact_logic():
    """
    Test YFinance with the exact same logic and parameters used in GFAnalytics.
    """
    # Exact configuration from config.yaml
    stock_code = "HSI"
    ric_code = "^HSI"
    start_date = "2023-11-01"
    end_date = "2024-12-31"
    period = "1D"
    
    # Map period to YFinance interval (same as in stock_data.py)
    period_map = {
        '1H': '1h',
        '2H': '2h',
        '1D': '1d',
        '1W': '1wk',
        '1M': '1mo'
    }
    interval = period_map.get(period, '1d')
    
    logger.info(f"Testing YFinance for {stock_code} ({ric_code})")
    logger.info(f"Date range: {start_date} to {end_date}")
    logger.info(f"Period: {period} -> Interval: {interval}")
    
    # Convert start and end dates to datetime (same as in stock_data.py)
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    # Log yfinance version (same as in stock_data.py)
    logger.info(f"Using yfinance version: {yf.__version__}")
    
    try:
        # Download data from YFinance (exact same call as in stock_data.py)
        logger.info("Calling yf.download()...")
        data = yf.download(
            ric_code,
            start=start_dt,
            end=end_dt,
            interval=interval,
            auto_adjust=True
        )
        
        # Check if multi-level columns (same logic as in stock_data.py)
        if isinstance(data.columns, pd.MultiIndex):
            logger.info("Multi-level columns detected, extracting ticker level")
            data = data.xs(ric_code, axis=1, level='Ticker')
        
        # Log raw data from YFinance (same as in stock_data.py)
        logger.info("Raw YFinance data:")
        logger.info(f"Shape: {data.shape}")
        logger.info(f"Index: {data.index}")
        logger.info(f"Columns: {data.columns}")
        logger.info(f"First few rows:\n{data.head()}")
        logger.info(f"Last few rows:\n{data.tail()}")
        
        # Check if data is empty
        if data.empty:
            logger.error("YFinance returned empty DataFrame!")
            return None
        
        # Reset index to make the date a column (same as in stock_data.py)
        data.reset_index(inplace=True)
        
        # Rename the date column to 'time' (same as in stock_data.py)
        data.rename(columns={'Date': 'time', 'Datetime': 'time'}, inplace=True)
        
        # Log data statistics (same as in stock_data.py)
        logger.info(f"Data shape after processing: {data.shape}")
        logger.info(f"Date range: {data['time'].min()} to {data['time'].max()}")
        logger.info(f"Columns: {data.columns.tolist()}")
        
        # Log summary statistics (same as in stock_data.py)
        logger.info("Summary statistics:")
        logger.info(f"\n{data.describe()}")
        
        # Check for missing values (same as in stock_data.py)
        missing = data.isnull().sum()
        if missing.any():
            logger.warning(f"Missing values found:\n{missing[missing > 0]}")
        else:
            logger.info("No missing values found")
        
        # Add metadata columns (same as in stock_data.py)
        data['stock_code'] = stock_code
        data['ric_code'] = ric_code
        data['uuid'] = pd.util.hash_pandas_object(data).astype(str)
        data['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
        
        logger.info(f"Final data shape: {data.shape}")
        logger.info(f"Final columns: {data.columns.tolist()}")
        
        # Save to CSV for inspection
        output_file = f"yfinance_test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        data.to_csv(output_file, index=False)
        logger.info(f"Data saved to {output_file}")
        
        return data
        
    except Exception as e:
        logger.error(f"YFinance download failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return None

def test_with_retry():
    """
    Test YFinance with retry logic to handle rate limiting.
    """
    max_retries = 3
    base_wait_time = 60  # Start with 1 minute
    
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1} of {max_retries}")
        
        result = test_yfinance_exact_logic()
        
        if result is not None and not result.empty:
            logger.info("Success! Data retrieved successfully")
            return result
        
        if attempt < max_retries - 1:
            wait_time = base_wait_time * (2 ** attempt) + random.uniform(0, 30)
            logger.info(f"Attempt failed, waiting {wait_time:.1f} seconds before retry...")
            time.sleep(wait_time)
        else:
            logger.error("All retry attempts failed")
    
    return None

def test_alternative_symbols():
    """
    Test different symbol variations for HSI.
    """
    symbols_to_try = [
        "^HSI",      # Original
        "HSI",       # Without caret
        "0000.HK",   # HK format
        "HSI.HK",    # Alternative HK format
        "HSTECH",    # Hang Seng Tech Index
        "^HSCE"      # Hang Seng China Enterprises Index
    ]
    
    for symbol in symbols_to_try:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing symbol: {symbol}")
        logger.info(f"{'='*50}")
        
        try:
            # Quick test with shorter date range
            data = yf.download(
                symbol,
                start="2024-01-01",
                end="2024-01-31",
                interval="1d"
            )
            
            if not data.empty:
                logger.info(f"✅ SUCCESS: {symbol} returned {len(data)} rows")
                logger.info(f"Date range: {data.index.min()} to {data.index.max()}")
                logger.info(f"Columns: {data.columns.tolist()}")
                logger.info(f"Sample data:\n{data.head(2)}")
            else:
                logger.warning(f"❌ EMPTY: {symbol} returned no data")
                
        except Exception as e:
            logger.error(f"❌ ERROR: {symbol} failed with {type(e).__name__}: {str(e)}")
        
        # Small delay between requests
        time.sleep(2)

if __name__ == "__main__":
    logger.info("Starting YFinance test script")
    logger.info("="*60)
    
    # Test 1: Exact logic from GFAnalytics
    logger.info("TEST 1: Exact GFAnalytics logic")
    result = test_yfinance_exact_logic()
    
    if result is None or result.empty:
        logger.info("\nTEST 2: Retry with exponential backoff")
        result = test_with_retry()
    
    if result is None or result.empty:
        logger.info("\nTEST 3: Alternative symbols")
        test_alternative_symbols()
    
    logger.info("\nYFinance test completed") 