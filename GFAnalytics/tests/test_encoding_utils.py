#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for encoding utilities module.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from sklearn.preprocessing import LabelEncoder

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GFAnalytics.utils.encoding_utils import (
    get_categorical_columns, 
    encode_column, 
    process_encode_data, 
    decode_prediction_data
)

class TestEncodingUtils(unittest.TestCase):
    """Test cases for encoding utilities."""
    
    def setUp(self):
        """Set up test data."""
        # Create test DataFrame with different types of columns
        self.test_data = pd.DataFrame({
            'time': pd.date_range(start='2023-01-01', periods=10),
            'stock_code': ['000001', '000002', '000003', '000004', '000005', 
                          '000006', '000007', '000008', '000009', '000010'],
            'open': np.random.random(10) * 100,
            'high': np.random.random(10) * 100,
            'low': np.random.random(10) * 100,
            'close': np.random.random(10) * 100,
            'volume': np.random.randint(1000, 10000, 10),
            'day_gan': ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'],
            'day_zhi': ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉'],
            'bazi_day': ['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉'],
            'wuxi': ['金', '木', '水', '火', '土', '金', '木', '水', '火', '土'],
            'cs_relation': ['比肩', '劫財', '食神', '傷官', '偏財', '正財', '七殺', '正官', '偏印', '正印']
        })
        
        # Add a column with missing values
        self.test_data_with_missing = self.test_data.copy()
        self.test_data_with_missing.loc[3:5, 'wuxi'] = np.nan
        
        # Setup existing encoder
        self.existing_encoder = LabelEncoder()
        self.existing_encoder.fit(['金', '木', '水', '火'])  # Deliberately missing '土'
        
    def test_get_categorical_columns(self):
        """Test identifying categorical columns."""
        cat_cols = get_categorical_columns(self.test_data)
        
        # Check the expected categorical columns are identified
        self.assertIn('day_gan', cat_cols)
        self.assertIn('day_zhi', cat_cols)
        self.assertIn('bazi_day', cat_cols)
        self.assertIn('wuxi', cat_cols)
        self.assertIn('cs_relation', cat_cols)
        
        # Check that numerical columns are not identified as categorical
        self.assertNotIn('open', cat_cols)
        self.assertNotIn('high', cat_cols)
        self.assertNotIn('low', cat_cols)
        self.assertNotIn('close', cat_cols)
        self.assertNotIn('volume', cat_cols)
        
        # Check that time and stock_code are not identified as categorical
        self.assertNotIn('time', cat_cols)
        self.assertNotIn('stock_code', cat_cols)
        
    def test_encode_column(self):
        """Test encoding a single column."""
        # Test with no existing encoder
        encoded_col, encoder = encode_column(self.test_data, 'wuxi')
        
        # Check the encoder and encoded values
        self.assertEqual(len(encoder.classes_), 5)  # 5 unique values
        self.assertTrue(all(isinstance(val, int) for val in encoded_col))
        
        # Test with existing encoder
        encoded_col, encoder = encode_column(self.test_data, 'wuxi', self.existing_encoder)
        
        # Check that the encoder has been updated with the new class
        self.assertEqual(len(encoder.classes_), 5)  # Should now include '土'
        self.assertTrue(all(isinstance(val, int) for val in encoded_col))
        
        # Test with missing values
        encoded_col, encoder = encode_column(self.test_data_with_missing, 'wuxi')
        
        # Check that missing values are handled
        self.assertEqual(len(encoder.classes_), 6)  # 5 unique values + 'unknown'
        self.assertTrue(all(isinstance(val, int) for val in encoded_col))
        
    def test_process_encode_data(self):
        """Test processing and encoding an entire DataFrame."""
        # Test with no existing encoders
        processed_data, encoders = process_encode_data(self.test_data)
        
        # Check that all categorical columns are encoded
        for col in ['day_gan', 'day_zhi', 'bazi_day', 'wuxi', 'cs_relation']:
            self.assertTrue(all(isinstance(val, int) for val in processed_data[col]))
            self.assertIn(col, encoders)
            
        # Check that non-categorical columns are unchanged
        for col in ['open', 'high', 'low', 'close', 'volume']:
            self.assertTrue(np.allclose(processed_data[col], self.test_data[col]))
            
        # Test with existing encoders
        existing_encoders = {'wuxi': self.existing_encoder}
        processed_data, encoders = process_encode_data(self.test_data, existing_encoders)
        
        # Check that the existing encoder was used and updated
        self.assertEqual(len(encoders['wuxi'].classes_), 5)
        
        # Test with missing values
        processed_data, encoders = process_encode_data(self.test_data_with_missing)
        
        # Check that missing values are handled
        self.assertTrue(all(isinstance(val, int) for val in processed_data['wuxi']))
        
    def test_decode_prediction_data(self):
        """Test decoding predicted values back to original categories."""
        # Encode a column to get an encoder
        _, encoder = encode_column(self.test_data, 'wuxi')
        
        # Create some test predictions
        predictions = np.array([0, 1, 2, 3, 4])
        
        # Decode the predictions
        decoded = decode_prediction_data(predictions, encoder)
        
        # Check that the predictions are decoded correctly
        expected = np.array(['金', '木', '水', '火', '土'])
        self.assertTrue(all(decoded == expected))
        
        # Test with no encoder
        decoded = decode_prediction_data(predictions)
        
        # Check that the predictions are returned as is
        self.assertTrue(all(decoded == predictions))
        
        # Test with error handling
        invalid_predictions = np.array([10, 11, 12])  # Invalid indices
        decoded = decode_prediction_data(invalid_predictions, encoder)
        
        # Check that the error is handled and predictions are returned as is
        self.assertTrue(all(decoded == invalid_predictions))

if __name__ == '__main__':
    unittest.main() 