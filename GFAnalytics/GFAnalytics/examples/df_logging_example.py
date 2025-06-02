#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example script demonstrating the use of DataFrame logging utilities.
"""

import os
import sys
import pandas as pd
import numpy as np
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the CSV logging utility
from GFAnalytics.utils.csv_utils import logdf, configure

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function demonstrating DataFrame logging utility."""
    print("DataFrame Logging Example")
    print("========================")
    
    # Get path to config file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), 'config', 'config.yaml')
    
    # Configure the DataFrame logger with our config
    print(f"Configuring DataFrame logger with config from: {config_path}")
    configure(config_path)
    
    # Create a sample DataFrame
    print("\nCreating sample DataFrame...")
    df = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=100),
        'stock_code': np.random.choice(['000001', '000002', '000003'], 100),
        'open': np.random.random(100) * 100,
        'high': np.random.random(100) * 100 + 5,
        'low': np.random.random(100) * 100 - 5,
        'close': np.random.random(100) * 100,
        'volume': np.random.randint(1000, 10000, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'boolean': np.random.choice([True, False], 100)
    })
    
    # Add some NaN values to demonstrate handling of missing data
    df.loc[10:15, 'close'] = np.nan
    df.loc[20:25, 'category'] = np.nan
    
    # Log the DataFrame
    print("\nLogging the full DataFrame...")
    csv_path = logdf(df, 'sample_data')
    print(f"DataFrame logged to: {csv_path}")
    
    # Log with custom parameters
    print("\nLogging with custom parameters (no index, different float format)...")
    csv_path = logdf(df, 'sample_data_custom', index=False, float_format='%.2f')
    print(f"DataFrame logged to: {csv_path}")
    
    # Create a DataFrame with many rows to demonstrate row limiting
    print("\nCreating a large DataFrame to demonstrate row limiting...")
    large_df = pd.DataFrame({
        'id': range(2000),
        'value': np.random.random(2000)
    })
    csv_path = logdf(large_df, 'large_sample')
    print(f"Large DataFrame logged to: {csv_path}")
    
    # Log a filtered subset of the DataFrame
    print("\nLogging a filtered subset of the DataFrame...")
    filtered_df = df[df['category'] == 'A']
    csv_path = logdf(filtered_df, 'filtered_data')
    print(f"Filtered DataFrame logged to: {csv_path}")
    
    # Log with compression
    print("\nLogging with compression...")
    csv_path = logdf(df, 'compressed_data', compression='gzip')
    print(f"Compressed DataFrame logged to: {csv_path}")
    
    print("\nDataFrame logging example complete.")
    print(f"CSV log files can be found in the 'csv_logs' directory.")

if __name__ == "__main__":
    main() 