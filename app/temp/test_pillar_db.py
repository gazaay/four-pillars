#!/usr/bin/env python
"""
Test script for the versioned pillars database.
This script can be run from the command line to test the database functionality.

Usage:
    python test_pillar_db.py [version] [--force] [--remove-database] [--create-dataset] [--test]
                            [--days-back DAYS] [--days-forward DAYS] [--forecast-months MONTHS]

Arguments:
    version: Optional version string (default: "v1.0")
    --force: Force recalculation even if the version exists in database
    --remove-database: Remove the specified version from the database
    --create-dataset: Only create/update the dataset
    --test: Test the dataset with a sample date (default operation)
    --days-back: Number of days to look back from today (default: 50)
    --days-forward: Number of days to look forward from today (default: 2)
    --forecast-months: Number of months to include in the forecast (default: 12)

Examples:
    python test_pillar_db.py v2.0 --force               # Force recalculation of v2.0
    python test_pillar_db.py v1.0 --remove-database     # Remove v1.0 from database
    python test_pillar_db.py v1.1 --create-dataset      # Just create v1.1 dataset
    python test_pillar_db.py v1.0 --test                # Test v1.0 with sample data
    python test_pillar_db.py v1.0 --create-dataset --days-back 100 --days-forward 10 --forecast-months 6
"""

import sys
import time
import argparse
import pandas as pd
from datetime import datetime, timedelta
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
parser = argparse.ArgumentParser(description='Test and manage the versioned pillars database')
parser.add_argument('version', nargs='?', default='v1.0', help='Version string (default: v1.0)')
parser.add_argument('--force', action='store_true', help='Force recalculation')
parser.add_argument('--remove-database', action='store_true', help='Remove the specified version from the database')
parser.add_argument('--create-dataset', action='store_true', help='Only create/update the dataset')
parser.add_argument('--test', action='store_true', help='Test the dataset with a sample date (default operation)')
parser.add_argument('--days-back', type=int, default=50, help='Number of days to look back from today (default: 50)')
parser.add_argument('--days-forward', type=int, default=2, help='Number of days to look forward from today (default: 2)')
parser.add_argument('--forecast-months', type=int, default=12, help='Number of months to include in the forecast (default: 12)')
args = parser.parse_args()

# Set default operation if none specified
if not (args.remove_database or args.create_dataset or args.test):
    args.test = True

# Import our helper module using direct import
try:
    from pillar_helper import get_pillars_dataset, logger
except ImportError as e:
    print(f"Error importing pillar_helper: {e}")
    print("Make sure pillar_helper.py is in the same directory as this script")
    sys.exit(1)

def remove_dataset_version(version):
    """Remove a specific version from the database"""
    try:
        from google.cloud import bigquery
        
        # Connect to BigQuery
        project_id = 'stock8word'
        dataset_name = 'GG88'
        table_name = 'thousand_year_current_pillars'
        
        client = bigquery.Client(project=project_id)
        
        # Execute deletion query
        delete_query = f"""
        DELETE FROM `{project_id}.{dataset_name}.{table_name}`
        WHERE version = '{version}'
        """
        
        print(f"Removing version {version} from database...")
        query_job = client.query(delete_query)
        query_job.result()  # Wait for query to complete
        
        # Also delete metadata if it exists
        try:
            metadata_table = f"{project_id}.{dataset_name}.thousand_year_current_pillars_metadata"
            # Check if metadata table exists first
            try:
                client.get_table(metadata_table)
                # If we get here, table exists
                metadata_delete_query = f"""
                DELETE FROM `{metadata_table}`
                WHERE version = '{version}'
                """
                client.query(metadata_delete_query).result()
                print(f"Removed metadata for version {version}")
            except Exception:
                print(f"Note: Metadata table does not exist yet")
        except Exception as e:
            print(f"Note: Could not remove metadata: {str(e)}")
        
        print(f"Successfully removed version {version} from the database.")
        return True
    except Exception as e:
        print(f"Error removing version {version} from database: {str(e)}")
        return False

def create_dataset(version, force_recalculate=False):
    """Create/update a dataset version in the database"""
    try:
        print(f"Creating/updating dataset version {version} in database...")
        print(f"Using date parameters: days_back={args.days_back}, days_forward={args.days_forward}, forecast_months={args.forecast_months}")
        
        start_time = time.time()
        
        # Get (and create) the dataset with our custom parameters
        dataset = get_pillars_dataset(
            version=version, 
            force_recalculate=force_recalculate,
            days_back=args.days_back,
            days_forward=args.days_forward,
            forecast_months=args.forecast_months
        )
        
        elapsed_time = time.time() - start_time
        
        # Display the results
        print(f"Successfully created dataset version {version} with {len(dataset)} rows in {elapsed_time:.2f} seconds")
        print(f"Date range: {dataset['time'].min()} to {dataset['time'].max()}")
        
        return True
    except Exception as e:
        print(f"Error creating dataset version {version}: {str(e)}")
        return False

def test_dataset(version, force_recalculate=False):
    """Test the dataset with a sample date"""
    # Test specific date
    stock_birthday_timestamp = datetime(1969, 11, 24, 9)
    
    # Import bazi module for pillar calculations
    try:
        from app import bazi
    except ImportError:
        print("Error importing bazi module. Make sure the app directory is in your Python path.")
        return False
    
    print("\nCalculating base 8 words for test date...")
    # Get base 8 words for test date
    base_8w = bazi.get_heavenly_branch_ymdh_pillars_current(stock_birthday_timestamp.year,
                                                        stock_birthday_timestamp.month,
                                                        stock_birthday_timestamp.day,
                                                        stock_birthday_timestamp.hour)
    print(f"\n{'='*80}")
    print(f"Testing pillars database with version: {version}, force_recalculate: {force_recalculate}")
    print(f"{'='*80}\n")
    
    # Time the operation
    start_time = time.time()
    
    try:
        # Try to fetch metadata
        try:
            from google.cloud import bigquery
            
            project_id = 'stock8word'
            dataset_name = 'GG88'
            table_name = 'thousand_year_current_pillars_metadata'
            
            client = bigquery.Client(project=project_id)
            
            query = f"""
            SELECT metadata
            FROM `{project_id}.{dataset_name}.{table_name}`
            WHERE version = '{version}'
            LIMIT 1
            """
            
            result = client.query(query).to_dataframe()
            if not result.empty:
                import json
                metadata = json.loads(result['metadata'].iloc[0])
                print("Dataset metadata:")
                print(f"  - Days back: {metadata.get('days_back', 'unknown')}")
                print(f"  - Days forward: {metadata.get('days_forward', 'unknown')}")
                print(f"  - Forecast months: {metadata.get('forecast_months', 'unknown')}")
                print(f"  - Creation date: {metadata.get('creation_date', 'unknown')}")
        except Exception as e:
            print(f"Note: Could not fetch metadata: {str(e)}")
        
        # Get the dataset using specified parameters
        dataset = get_pillars_dataset(
            version=version, 
            force_recalculate=force_recalculate
        )
        
        # Print statistics
        elapsed_time = time.time() - start_time
        
        # Create a small sample for testing
        sample_df = dataset.head(1).copy()
        sample_df['time'] = stock_birthday_timestamp
        
        # Add base 8 words columns from test date
        sample_df['本時'] = base_8w["時"]
        sample_df['本日'] = base_8w["日"] 
        sample_df['-本時'] = base_8w["-時"]
        sample_df['本月'] = base_8w["月"]
        sample_df['本年'] = base_8w["年"]
        sample_df['-本月'] = base_8w["-月"]
        
        print(f"\n{'='*80}")
        print(f"Test completed successfully in {elapsed_time:.2f} seconds")
        print(f"Retrieved dataset version {version} with {len(dataset)} rows")
        print(f"Date range: {dataset['time'].min()} to {dataset['time'].max()}")
        print(f"Test data sample:")
        print(sample_df[['time', '本時', '本日', '本月', '本年']])
        print(f"{'='*80}\n")
        
        # Test chengseng calculation
        print("\nTesting chengseng calculation on the sample data...")
        try:
            from app import chengseng
            sample_df = chengseng.create_chengseng_for_dataset(sample_df)
            print("Successfully calculated chengseng values")
            print("\nSample data with chengseng columns:")
            
            # Display the most relevant columns
            columns_to_display = ['time', '本時', '本日', '本月', '本年', '流時', '流日', '流月', '流年']
            available_columns = [col for col in columns_to_display if col in sample_df.columns]
            print(sample_df[available_columns])
            
            print("\nTesting month calculation for a specific date (2025-12-24)...")
            test_date = datetime(2025, 12, 24, 12)
            try:
                heavenly_stem, earthly_branch = bazi.calculate_month_heavenly_withSeason_for_current_time(
                    test_date.year, test_date.month, test_date.day, test_date.hour)
                print(f"Date: 2025-12-24")
                print(f"Heavenly Stem: {heavenly_stem}")
                print(f"Earthly Branch: {earthly_branch}")
            except Exception as e:
                print(f"Error calculating month for 2025-12-24: {str(e)}")
            
        except Exception as e:
            print(f"Error calculating chengseng: {str(e)}")
            
        return True
    except Exception as e:
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"Test failed after {elapsed_time:.2f} seconds")
        print(f"Error: {str(e)}")
        print(f"{'='*80}\n")
        
        return False

def main():
    """Main function to handle the different operations"""
    version = args.version
    force_recalculate = args.force
    
    if args.remove_database:
        print(f"Operation: REMOVE DATABASE VERSION {version}")
        if remove_dataset_version(version):
            return 0
        else:
            return 1
            
    elif args.create_dataset:
        print(f"Operation: CREATE DATASET VERSION {version}")
        if create_dataset(version, force_recalculate):
            return 0
        else:
            return 1
            
    elif args.test:
        print(f"Operation: TEST DATASET VERSION {version}")
        if test_dataset(version, force_recalculate):
            return 0
        else:
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 