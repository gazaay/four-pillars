#!/usr/bin/env python
"""
Test script for the month calculation function.
Tests the calculate_month_heavenly_withSeason_for_current_time function
for a specific date (2025-12-24).

Usage:
    python test_month_calculation.py [--date YYYY-MM-DD] [--hour HOUR]

Examples:
    python test_month_calculation.py
    python test_month_calculation.py --date 2025-12-24 --hour 12
"""

import sys
import os
import argparse
from datetime import datetime

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import logging configuration
import logging
logging.basicConfig(level=logging.INFO, 
                     format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description='Test month calculation function')
    parser.add_argument('--date', default='2025-12-24', help='Test date in YYYY-MM-DD format')
    parser.add_argument('--hour', type=int, default=12, help='Hour of the day (0-23)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Parse the date
    try:
        test_date = datetime.strptime(args.date, '%Y-%m-%d')
        test_date = test_date.replace(hour=args.hour)
    except ValueError:
        logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD.")
        return 1
    
    logger.info(f"Testing month calculation for date: {test_date}")
    
    # Import the bazi module
    try:
        from app.bazi import calculate_month_heavenly_withSeason_for_current_time
    except ImportError as e:
        logger.error(f"Error importing bazi module: {e}")
        logger.error("Make sure the app directory is in your Python path")
        return 1
    
    try:
        # Call the function
        heavenly_stem, earthly_branch = calculate_month_heavenly_withSeason_for_current_time(
            test_date.year, test_date.month, test_date.day, test_date.hour)
        
        # Print results
        print("\n" + "="*50)
        print(f"MONTH CALCULATION RESULTS FOR: {test_date}")
        print("="*50)
        print(f"Heavenly Stem: {heavenly_stem}")
        print(f"Earthly Branch: {earthly_branch}")
        print("="*50 + "\n")
        
        return 0
    except Exception as e:
        logger.error(f"Error calculating month: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 