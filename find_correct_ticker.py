#!/usr/bin/env python3

import yfinance as yf
import time

# Test multiple ticker formats for Hang Seng Index
tickers_to_test = [
    "^HSI",           # Yahoo Finance format
    "HSI.HK",         # Hong Kong format
    "0000.HK",        # Alternative HK format  
    "HSI",            # Simple format
    "HSTECH",         # Hang Seng Tech Index
    "^HSCE",          # Hang Seng China Enterprises
    "2800.HK",        # Tracker Fund of Hong Kong (HSI ETF)
    "FXI",            # iShares China Large-Cap ETF (US-listed HSI proxy)
]

print("🔍 Testing multiple HSI ticker formats...")
print("=" * 60)

successful_tickers = []

for ticker in tickers_to_test:
    print(f"\nTesting: {ticker}")
    try:
        # Use a minimal date range and disable progress to avoid rate limiting
        data = yf.download(ticker, start='2024-12-20', end='2024-12-21', 
                          interval='1d', progress=False, auto_adjust=False)
        
        if not data.empty:
            print(f"✅ SUCCESS: {len(data)} rows")
            print(f"   Latest close: {data['Close'].iloc[-1]:.2f}")
            print(f"   Date: {data.index[-1]}")
            successful_tickers.append(ticker)
        else:
            print(f"❌ EMPTY: No data returned")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Small delay to avoid rate limiting
    time.sleep(1)

print(f"\n🎯 SUMMARY:")
print(f"=" * 30)
if successful_tickers:
    print(f"✅ Working tickers: {successful_tickers}")
    print(f"\n💡 Recommended ticker for config: {successful_tickers[0]}")
else:
    print(f"❌ No working tickers found")
    print(f"💡 This might be due to:")
    print(f"   - YFinance rate limiting")  
    print(f"   - Network issues")
    print(f"   - Market closure/holiday")
    print(f"   - Need to use ETF proxies instead of direct index") 