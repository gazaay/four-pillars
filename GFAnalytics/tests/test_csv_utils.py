#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for CSV utilities module.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
import tempfile
import shutil
import yaml

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GFAnalytics.utils.csv_utils import (
    DataFrameLogger,
    logdf,
    configure,
    get_logger
)

class TestCSVUtils(unittest.TestCase):
    """Test cases for CSV utilities."""
    
    def setUp(self):
        """Set up test data and temporary directory."""
        # Create a temporary directory for test output
        self.test_dir = tempfile.mkdtemp()
        
        # Create test DataFrame
        self.test_df = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=10),
            'id': range(10),
            'value': np.random.random(10),
            'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'A', 'B', 'C']
        })
        
        # Create a temporary config file
        self.config_path = os.path.join(self.test_dir, 'test_config.yaml')
        self.test_config = {
            'csv_logging': {
                'enabled': True,
                'output_dir': os.path.join(self.test_dir, 'csv_logs'),
                'include_timestamp': False,  # Disable timestamp for easier testing
                'max_rows': 5,
                'index': False,
                'compression': None,
                'float_format': '%.2f',
                'encoding': 'utf-8'
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.test_dir)
    
    def test_dataframe_logger_init(self):
        """Test initializing DataFrameLogger."""
        logger = DataFrameLogger(self.config_path)
        
        # Check that config was loaded correctly
        self.assertEqual(logger.config['output_dir'], self.test_config['csv_logging']['output_dir'])
        self.assertEqual(logger.config['max_rows'], self.test_config['csv_logging']['max_rows'])
        
        # Check that output directory was created
        self.assertTrue(os.path.exists(logger.output_dir))
    
    def test_log_df(self):
        """Test logging a DataFrame."""
        logger = DataFrameLogger(self.config_path)
        
        # Log the DataFrame
        csv_path = logger.log_df(self.test_df, 'test_df')
        
        # Check that file was created
        self.assertTrue(os.path.exists(csv_path))
        
        # Read back the CSV and check the contents
        df_read = pd.read_csv(csv_path)
        
        # Should be limited to max_rows (5)
        self.assertEqual(len(df_read), 5)
        
        # Column count should match (minus index since we specified index=False)
        self.assertEqual(len(df_read.columns), len(self.test_df.columns))
    
    def test_log_df_with_custom_options(self):
        """Test logging a DataFrame with custom options."""
        logger = DataFrameLogger(self.config_path)
        
        # Log with custom options
        csv_path = logger.log_df(self.test_df, 'test_df_custom', 
                                index=True, 
                                float_format='%.4f',
                                max_rows=10)  # Override max_rows
        
        # Read back the CSV
        df_read = pd.read_csv(csv_path)
        
        # Should have all rows (override max_rows)
        self.assertEqual(len(df_read), 10)
        
        # Should have index column
        self.assertTrue('Unnamed: 0' in df_read.columns)
    
    def test_global_logdf(self):
        """Test the global logdf function."""
        # Configure with our test config
        configure(self.config_path)
        
        # Log the DataFrame
        csv_path = logdf(self.test_df, 'global_test')
        
        # Check that file was created
        self.assertTrue(os.path.exists(csv_path))
        
        # Read back the CSV and check the contents
        df_read = pd.read_csv(csv_path)
        
        # Should be limited to max_rows (5)
        self.assertEqual(len(df_read), 5)
    
    def test_disabled_logging(self):
        """Test that logging is skipped when disabled."""
        # Create a config with logging disabled
        disabled_config = {
            'csv_logging': {
                'enabled': False,
                'output_dir': os.path.join(self.test_dir, 'disabled_logs')
            }
        }
        
        disabled_config_path = os.path.join(self.test_dir, 'disabled_config.yaml')
        with open(disabled_config_path, 'w') as f:
            yaml.dump(disabled_config, f)
        
        # Configure with disabled config
        logger = DataFrameLogger(disabled_config_path)
        
        # Try to log
        csv_path = logger.log_df(self.test_df, 'should_not_exist')
        
        # Path should be None
        self.assertIsNone(csv_path)
        
        # Directory should still be created but file should not exist
        self.assertTrue(os.path.exists(logger.output_dir))
        expected_path = os.path.join(logger.output_dir, 'should_not_exist.csv')
        self.assertFalse(os.path.exists(expected_path))
    
    def test_compressed_output(self):
        """Test logging with compression."""
        # Create a config with compression
        compressed_config = {
            'csv_logging': {
                'enabled': True,
                'output_dir': os.path.join(self.test_dir, 'compressed_logs'),
                'include_timestamp': False,
                'compression': 'gzip',
                'index': False
            }
        }
        
        compressed_config_path = os.path.join(self.test_dir, 'compressed_config.yaml')
        with open(compressed_config_path, 'w') as f:
            yaml.dump(compressed_config, f)
        
        # Configure with compressed config
        logger = DataFrameLogger(compressed_config_path)
        
        # Log the DataFrame
        csv_path = logger.log_df(self.test_df, 'compressed_test')
        
        # Check that file was created
        self.assertTrue(os.path.exists(csv_path))
        
        # Read back the CSV with compression
        df_read = pd.read_csv(csv_path, compression='gzip')
        
        # Check the contents
        self.assertEqual(len(df_read), len(self.test_df))
        
    def test_empty_dataframe(self):
        """Test logging an empty DataFrame."""
        logger = DataFrameLogger(self.config_path)
        
        # Create empty DataFrame
        empty_df = pd.DataFrame()
        
        # Log the empty DataFrame
        csv_path = logger.log_df(empty_df, 'empty_df')
        
        # Should still create the file
        self.assertTrue(os.path.exists(csv_path))
        
        # File should be essentially empty (just a header row)
        with open(csv_path, 'r') as f:
            content = f.read().strip()
        
        # Should be empty or just a header
        self.assertTrue(content == '' or len(content.split('\n')) == 1)
    
    def test_get_logger(self):
        """Test the get_logger singleton function."""
        # Get a logger
        logger1 = get_logger(self.config_path)
        
        # Get another logger - should be the same instance
        logger2 = get_logger()
        
        # Should be the same object
        self.assertIs(logger1, logger2)
        
        # Now configure a new logger
        logger3 = configure(self.config_path)
        
        # Should be a new instance
        self.assertIsNot(logger1, logger3)
        
        # But get_logger should now return the new one
        logger4 = get_logger()
        self.assertIs(logger3, logger4)

if __name__ == '__main__':
    unittest.main() 