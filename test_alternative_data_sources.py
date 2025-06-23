#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Alternative Data Sources Test Script

Test HSI data availability from TradingView and MT5.
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AlternativeDataTest')

def test_tradingview():
    """
    Test TradingView data access for HSI.
    """
    logger.info("Testing TradingView data access...")
    
    try:
        # Try to import tvdatafeed with correct module name
        from tvDatafeed import TvDatafeed, Interval
        
        logger.info("✅ tvdatafeed library available")
        
        # Initialize TradingView data feed (without login first)
        tv = TvDatafeed()
        
        # HSI symbols to try
        hsi_symbols = [
            ("HSI", "HKEX"),           # Hang Seng Index on HKEX
            ("HK50", "OANDA"),         # HSI on OANDA
            ("HSI", "TVC"),            # HSI on TradingView
            ("HSTECH", "HKEX"),        # Hang Seng Tech Index
            ("HSCE", "HKEX"),          # Hang Seng China Enterprises
        ]
        
        successful_symbols = []
        
        for symbol, exchange in hsi_symbols:
            logger.info(f"\nTesting {symbol} on {exchange}...")
            
            try:
                # Get recent data (last 30 days)
                data = tv.get_hist(
                    symbol=symbol,
                    exchange=exchange,
                    interval=Interval.in_daily,
                    n_bars=30
                )
                
                if data is not None and not data.empty:
                    logger.info(f"✅ SUCCESS: {symbol}@{exchange} - {len(data)} rows")
                    logger.info(f"   Date range: {data.index.min()} to {data.index.max()}")
                    logger.info(f"   Columns: {data.columns.tolist()}")
                    logger.info(f"   Sample data:\n{data.head(2)}")
                    
                    successful_symbols.append((symbol, exchange))
                    
                    # Save sample data
                    output_file = f"tradingview_{symbol}_{exchange}_sample.csv"
                    data.to_csv(output_file)
                    logger.info(f"   Sample saved to {output_file}")
                    
                else:
                    logger.warning(f"❌ EMPTY: {symbol}@{exchange} returned no data")
                    
            except Exception as e:
                logger.error(f"❌ ERROR: {symbol}@{exchange} failed - {str(e)}")
            
            # Small delay between requests
            time.sleep(1)
        
        logger.info(f"\nTradingView Summary: {len(successful_symbols)} successful symbols")
        for symbol, exchange in successful_symbols:
            logger.info(f"  ✅ {symbol}@{exchange}")
            
        return successful_symbols
        
    except ImportError as e:
        logger.error(f"❌ tvdatafeed library not installed: {str(e)}")
        logger.info("Install with: pip install --upgrade --no-cache-dir git+https://github.com/rongardF/tvdatafeed.git")
        return []
    except Exception as e:
        logger.error(f"❌ TradingView test failed: {str(e)}")
        return []

def test_mt5():
    """
    Test MT5 data access for HSI.
    """
    logger.info("Testing MT5 data access...")
    
    try:
        # Try to import MetaTrader5
        import MetaTrader5 as mt5
        
        logger.info("✅ MetaTrader5 library available")
        
        # Initialize MT5
        if not mt5.initialize():
            logger.error("❌ MT5 initialization failed")
            logger.error(f"Error: {mt5.last_error()}")
            return []
        
        logger.info("✅ MT5 initialized successfully")
        
        # HSI symbols to try (broker dependent)
        hsi_symbols = [
            "HSI",          # Direct HSI
            "HK50",         # HSI as HK50
            "HSI.cash",     # Cash index
            "HSTECH",       # Hang Seng Tech
            "HSCE",         # Hang Seng China Enterprises
        ]
        
        successful_symbols = []
        
        # Get all available symbols
        symbols = mt5.symbols_get()
        if symbols:
            logger.info(f"MT5 broker has {len(symbols)} symbols available")
            
            # Look for HSI-related symbols
            hsi_related = [s for s in symbols if 'HSI' in s.name or 'HK' in s.name or 'HANG' in s.name.upper()]
            if hsi_related:
                logger.info("Found HSI-related symbols:")
                for s in hsi_related[:10]:  # Show first 10
                    logger.info(f"  - {s.name}: {s.description}")
        
        for symbol in hsi_symbols:
            logger.info(f"\nTesting {symbol}...")
            
            try:
                # Check if symbol exists
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    logger.warning(f"❌ SYMBOL NOT FOUND: {symbol}")
                    continue
                
                logger.info(f"✅ Symbol found: {symbol_info.description}")
                
                # Get recent data
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 30)
                
                if rates is not None and len(rates) > 0:
                    # Convert to DataFrame
                    df = pd.DataFrame(rates)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    
                    logger.info(f"✅ SUCCESS: {symbol} - {len(df)} rows")
                    logger.info(f"   Date range: {df['time'].min()} to {df['time'].max()}")
                    logger.info(f"   Columns: {df.columns.tolist()}")
                    logger.info(f"   Sample data:\n{df.head(2)}")
                    
                    successful_symbols.append(symbol)
                    
                    # Save sample data
                    output_file = f"mt5_{symbol}_sample.csv"
                    df.to_csv(output_file, index=False)
                    logger.info(f"   Sample saved to {output_file}")
                    
                else:
                    logger.warning(f"❌ EMPTY: {symbol} returned no data")
                    
            except Exception as e:
                logger.error(f"❌ ERROR: {symbol} failed - {str(e)}")
            
            time.sleep(0.5)
        
        # Shutdown MT5
        mt5.shutdown()
        
        logger.info(f"\nMT5 Summary: {len(successful_symbols)} successful symbols")
        for symbol in successful_symbols:
            logger.info(f"  ✅ {symbol}")
            
        return successful_symbols
        
    except ImportError:
        logger.error("❌ MetaTrader5 library not available on macOS")
        logger.info("MetaTrader5 is Windows-only")
        return []
    except Exception as e:
        logger.error(f"❌ MT5 test failed: {str(e)}")
        return []

def install_missing_libraries():
    """
    Install missing libraries.
    """
    logger.info("Checking and installing missing libraries...")
    
    libraries_to_check = [
        ("tvDatafeed", "git+https://github.com/rongardF/tvdatafeed.git"),
        ("MetaTrader5", "MetaTrader5")
    ]
    
    for lib_name, pip_name in libraries_to_check:
        try:
            __import__(lib_name)
            logger.info(f"✅ {lib_name} is available")
        except ImportError:
            logger.info(f"❌ {lib_name} not found, installing...")
            import subprocess
            import sys
            try:
                if "git+" in pip_name:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", pip_name])
                else:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
                logger.info(f"✅ {lib_name} installed successfully")
            except Exception as e:
                logger.error(f"❌ Failed to install {lib_name}: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Alternative Data Sources Test")
    logger.info("="*60)
    
    # Install missing libraries first
    install_missing_libraries()
    
    print("\n" + "="*60)
    print("TEST 1: TradingView")
    print("="*60)
    tv_symbols = test_tradingview()
    
    print("\n" + "="*60)
    print("TEST 2: MetaTrader 5")
    print("="*60)
    mt5_symbols = test_mt5()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if tv_symbols:
        print(f"✅ TradingView: {len(tv_symbols)} working symbols")
        for symbol, exchange in tv_symbols:
            print(f"   - {symbol}@{exchange}")
    else:
        print("❌ TradingView: No working symbols")
    
    if mt5_symbols:
        print(f"✅ MT5: {len(mt5_symbols)} working symbols")
        for symbol in mt5_symbols:
            print(f"   - {symbol}")
    else:
        print("❌ MT5: No working symbols")
    
    # Recommendation
    if tv_symbols and mt5_symbols:
        print("\n🎯 RECOMMENDATION: Both sources work! TradingView is easier to integrate.")
    elif tv_symbols:
        print("\n🎯 RECOMMENDATION: Use TradingView - it's working and easier to integrate.")
    elif mt5_symbols:
        print("\n🎯 RECOMMENDATION: Use MT5 - it's working but requires more setup.")
    else:
        print("\n⚠️  Neither source is working. Check your installations and connections.")
    
    logger.info("Alternative data sources test completed") 