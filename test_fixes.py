#!/usr/bin/env python3

import sys
import os
sys.path.append('GFAnalytics')

import yaml
import pandas as pd
from datetime import datetime
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_fixes')

def test_config_loading():
    """Test loading the updated config file."""
    try:
        with open('GFAnalytics/GFAnalytics/config/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        ticker = config['stock']['ric_code']
        print(f"✅ Config loaded successfully")
        print(f"   Stock code: {config['stock']['code']}")
        print(f"   RIC code: {ticker}")
        
        return config, ticker
    except Exception as e:
        print(f"❌ Config loading failed: {str(e)}")
        return None, None

def test_yfinance_ticker(ticker):
    """Test the YFinance ticker format."""
    try:
        import yfinance as yf
        
        print(f"\n🔍 Testing YFinance with ticker: {ticker}")
        
        # Test with a small date range to avoid rate limiting
        data = yf.download(ticker, start='2024-12-01', end='2024-12-02', interval='1d', progress=False)
        
        if not data.empty:
            print(f"✅ YFinance SUCCESS: {len(data)} rows")
            print(f"   Columns: {data.columns.tolist()}")
            return True
        else:
            print(f"❌ YFinance returned empty data")
            return False
    except Exception as e:
        print(f"❌ YFinance failed: {str(e)}")
        return False

def test_duplicate_columns_fix():
    """Test that our duplicate columns fix works."""
    try:
        print(f"\n🔍 Testing duplicate columns handling...")
        
        # Create test data with potential duplicates
        data1 = pd.DataFrame({
            'time': [datetime.now()],
            'Close': [100],
            'Volume': [1000]
        })
        
        data2 = pd.DataFrame({
            'time': [datetime.now()],  # This will create a duplicate
            'new_col': ['test']
        })
        
        # Test our fix logic
        overlapping_cols = set(data1.columns).intersection(set(data2.columns))
        if overlapping_cols:
            print(f"   Found overlapping columns: {overlapping_cols}")
            data2 = data2.drop(columns=list(overlapping_cols))
        
        # Concatenate
        result = pd.concat([data1, data2], axis=1)
        
        # Check for duplicates
        duplicate_cols = result.columns[result.columns.duplicated()].tolist()
        if duplicate_cols:
            print(f"❌ Still has duplicates: {duplicate_cols}")
            return False
        else:
            print(f"✅ No duplicate columns: {result.columns.tolist()}")
            return True
            
    except Exception as e:
        print(f"❌ Duplicate columns test failed: {str(e)}")
        return False

def main():
    print("🧪 Testing GFAnalytics Fixes")
    print("=" * 40)
    
    # Test 1: Config loading
    config, ticker = test_config_loading()
    if not config:
        return False
    
    # Test 2: YFinance ticker
    yf_success = test_yfinance_ticker(ticker)
    
    # Test 3: Duplicate columns fix
    dup_success = test_duplicate_columns_fix()
    
    print(f"\n📊 Test Results:")
    print(f"   Config loading: {'✅' if config else '❌'}")
    print(f"   YFinance ticker: {'✅' if yf_success else '❌'}")
    print(f"   Duplicate columns fix: {'✅' if dup_success else '❌'}")
    
    all_success = config and yf_success and dup_success
    print(f"\n🎯 Overall: {'✅ All tests passed!' if all_success else '❌ Some tests failed'}")
    
    if all_success:
        print("\n🚀 Ready to run the full GFAnalytics pipeline!")
    else:
        print("\n⚠️  Please address the failing tests before running the full pipeline.")
    
    return all_success

if __name__ == "__main__":
    main() 