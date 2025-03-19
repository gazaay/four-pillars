#!/usr/bin/env python
"""
Test script for the versioned pillars database.
This script can be run from the command line to test the database functionality.

Usage:
    python test_pillar_db.py [version] [--force]

Arguments:
    version: Optional version string (default: "v1.0")
    --force: Force recalculation even if the version exists in the database

Example:
    python test_pillar_db.py v2.0 --force
"""

import sys
import time
import argparse
import pandas as pd
from datetime import datetime
import os

# Add the current directory to the Python path so direct imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Also add parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels to project root
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test the versioned pillars database')
parser.add_argument('version', nargs='?', default='v1.0', help='Version string (default: v1.0)')
parser.add_argument('--force', action='store_true', help='Force recalculation')
args = parser.parse_args()

# Import our helper module using direct import
try:
    from pillar_helper import get_pillars_dataset, logger
except ImportError as e:
    print(f"Error importing pillar_helper: {e}")
    print("Make sure pillar_helper.py is in the same directory as this script")
    sys.exit(1)

def main():
    """Main test function"""
    version = args.version
    force_recalculate = args.force
    
    print(f"\n{'='*80}")
    print(f"Testing pillars database with version: {version}, force_recalculate: {force_recalculate}")
    print(f"{'='*80}\n")
    
    # Time the operation
    start_time = time.time()
    
    try:
        # Get the dataset
        dataset = get_pillars_dataset(version=version, force_recalculate=force_recalculate)
        
        # Print statistics
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"Test completed successfully in {elapsed_time:.2f} seconds")
        print(f"Retrieved dataset version {version} with {len(dataset)} rows")
        print(f"Date range: {dataset['time'].min()} to {dataset['time'].max()}")
        print(f"Sample data:")
        print(dataset.head())
        print(f"{'='*80}\n")
        
        return 0
    except Exception as e:
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"Test failed after {elapsed_time:.2f} seconds")
        print(f"Error: {str(e)}")
        print(f"{'='*80}\n")
        
        return 1

if __name__ == "__main__":
    sys.exit(main()) 