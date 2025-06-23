#!/usr/bin/env python3

import yfinance as yf
import pandas as pd

print('Testing HSI.HK ticker...')
try:
    data = yf.download('HSI.HK', start='2024-12-01', end='2024-12-31', interval='1d')
    if not data.empty:
        print(f'✅ SUCCESS: HSI.HK returned {len(data)} rows')
        print(f'Date range: {data.index.min()} to {data.index.max()}')
        print(f'Latest close: {data["Close"].iloc[-1]:.2f}')
        print(f'Columns: {data.columns.tolist()}')
    else:
        print('❌ EMPTY: No data returned')
except Exception as e:
    print(f'❌ ERROR: {str(e)}') 