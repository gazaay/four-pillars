#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for standardized feature preparation.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from sklearn.preprocessing import LabelEncoder

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GFAnalytics.utils.data_utils import prepare_feature_data
from GFAnalytics.utils.encoding_utils import process_encode_data

class TestFeaturePreparation(unittest.TestCase):
    """Test cases for standardized feature preparation."""
    
    def setUp(self):
        """Set up test data."""
        # Create test DataFrame with different types of columns
        self.test_data = pd.DataFrame({
            'time': pd.date_range(start='2023-01-01', periods=10),
            'date': pd.date_range(start='2023-01-01', periods=10),
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
            'cs_relation': ['比肩', '劫財', '食神', '傷官', '偏財', '正財', '七殺', '正官', '偏印', '正印'],
            'last_modified_date': pd.date_range(start='2023-01-02', periods=10),
            'batch_id': np.arange(1001, 1011)
        })
        
        # Add target column for training data
        self.test_data_with_target = self.test_data.copy()
        self.test_data_with_target['target'] = np.random.random(10) * 20
        
        # Test data with encoded columns
        self.encoded_data = self.test_data.copy()
        self.encoded_data['encoded_day_gan'] = np.arange(10)
        self.encoded_data['encoded_day_zhi'] = np.arange(10)
        self.encoded_data['encoded_wuxi'] = np.arange(5).tolist() + np.arange(5).tolist()
        
        # Test data with _y columns from a merge
        self.merge_data = self.test_data.copy()
        self.merge_data['close_y'] = np.random.random(10) * 100
        self.merge_data['volume_y'] = np.random.randint(1000, 10000, 10)
    
    def test_prepare_features_training_mode(self):
        """Test prepare_feature_data in training mode."""
        # First encode the categorical columns
        encoded_data, _ = process_encode_data(self.test_data_with_target)
        
        # Now prepare features for training
        X, y = prepare_feature_data(encoded_data, is_training=True)
        
        # Check X is a DataFrame and y is a Series
        self.assertIsInstance(X, pd.DataFrame)
        self.assertIsInstance(y, pd.Series)
        
        # Check non-feature columns are removed
        self.assertNotIn('time', X.columns)
        self.assertNotIn('date', X.columns)
        self.assertNotIn('stock_code', X.columns)
        self.assertNotIn('batch_id', X.columns)
        self.assertNotIn('last_modified_date', X.columns)
        
        # Check that unencoded categorical columns are removed
        self.assertNotIn('day_gan', X.columns)
        self.assertNotIn('day_zhi', X.columns)
        self.assertNotIn('bazi_day', X.columns)
        self.assertNotIn('wuxi', X.columns)
        
        # Check numerical features are present
        self.assertIn('open', X.columns)
        self.assertIn('high', X.columns)
        self.assertIn('low', X.columns)
        self.assertIn('close', X.columns)
        self.assertIn('volume', X.columns)
        
        # Check target is correct
        self.assertTrue(np.array_equal(y, encoded_data['target']))
        
        # Check X has no NaN values
        self.assertFalse(X.isna().any().any())
    
    def test_prepare_features_prediction_mode(self):
        """Test prepare_feature_data in prediction mode."""
        # First encode the categorical columns
        encoded_data, _ = process_encode_data(self.test_data)
        
        # Now prepare features for prediction
        X, y = prepare_feature_data(encoded_data, is_training=False)
        
        # Check X is a DataFrame and y is None
        self.assertIsInstance(X, pd.DataFrame)
        self.assertIsNone(y)
        
        # Check non-feature columns are removed
        self.assertNotIn('time', X.columns)
        self.assertNotIn('date', X.columns)
        self.assertNotIn('stock_code', X.columns)
        self.assertNotIn('batch_id', X.columns)
        self.assertNotIn('last_modified_date', X.columns)
        
        # Check that unencoded categorical columns are removed
        self.assertNotIn('day_gan', X.columns)
        self.assertNotIn('day_zhi', X.columns)
        self.assertNotIn('bazi_day', X.columns)
        self.assertNotIn('wuxi', X.columns)
        
        # Check numerical features are present
        self.assertIn('open', X.columns)
        self.assertIn('high', X.columns)
        self.assertIn('low', X.columns)
        self.assertIn('close', X.columns)
        self.assertIn('volume', X.columns)
        
        # Check X has no NaN values
        self.assertFalse(X.isna().any().any())
    
    def test_prepare_features_with_encoded_columns(self):
        """Test prepare_feature_data with already encoded columns."""
        # Prepare features directly from data with encoded columns
        X, y = prepare_feature_data(self.encoded_data, is_training=False)
        
        # Check encoded columns are preserved
        self.assertIn('encoded_day_gan', X.columns)
        self.assertIn('encoded_day_zhi', X.columns)
        self.assertIn('encoded_wuxi', X.columns)
        
        # Check original columns are dropped
        self.assertNotIn('day_gan', X.columns)
        self.assertNotIn('day_zhi', X.columns)
        self.assertNotIn('wuxi', X.columns)
    
    def test_prepare_features_with_merge_columns(self):
        """Test prepare_feature_data with _y columns from merges."""
        # Prepare features from merged data
        X, y = prepare_feature_data(self.merge_data, is_training=False)
        
        # Check _y columns are removed
        self.assertNotIn('close_y', X.columns)
        self.assertNotIn('volume_y', X.columns)
        
        # But regular columns are kept
        self.assertIn('close', X.columns)
        self.assertIn('volume', X.columns)
    
    def test_prepare_features_with_infinity(self):
        """Test prepare_feature_data with infinity values."""
        # Create data with infinity
        inf_data = self.test_data.copy()
        inf_data['open'][0] = np.inf
        inf_data['high'][1] = -np.inf
        
        # Prepare features
        X, y = prepare_feature_data(inf_data, is_training=False)
        
        # Check infinity was replaced
        self.assertFalse(np.isinf(X['open'][0]))
        self.assertFalse(np.isinf(X['high'][1]))
        
        # Should be replaced with 0
        self.assertEqual(X['open'][0], 0)
        self.assertEqual(X['high'][1], 0)
    
    def test_prepare_features_with_nan(self):
        """Test prepare_feature_data with NaN values."""
        # Create data with NaN
        nan_data = self.test_data.copy()
        nan_data['open'][2] = np.nan
        nan_data['high'][3] = np.nan
        
        # Prepare features
        X, y = prepare_feature_data(nan_data, is_training=False)
        
        # Check NaN was replaced
        self.assertFalse(np.isnan(X['open'][2]))
        self.assertFalse(np.isnan(X['high'][3]))
        
        # Should be replaced with 0
        self.assertEqual(X['open'][2], 0)
        self.assertEqual(X['high'][3], 0)
    
    def test_integration_with_encoding(self):
        """Test the full integration of encoding and feature preparation."""
        # Start with raw data including target
        raw_data = self.test_data_with_target.copy()
        
        # Step 1: Encode categorical columns
        encoded_data, encoders = process_encode_data(raw_data)
        
        # Check encoding worked
        self.assertTrue(any(col for col in encoded_data.columns if col.startswith('encoded_') or 
                             (col in raw_data.columns and pd.api.types.is_numeric_dtype(encoded_data[col]))))
        
        # Step 2: Prepare features for training
        X_train, y_train = prepare_feature_data(encoded_data, is_training=True)
        
        # Check feature preparation worked
        self.assertGreater(len(X_train.columns), 0)
        self.assertEqual(len(y_train), len(raw_data))
        
        # All columns should be numeric
        self.assertTrue(all(pd.api.types.is_numeric_dtype(X_train[col]) for col in X_train.columns))
        
        # Create new prediction data
        pred_data = raw_data.copy().iloc[:5].reset_index(drop=True)
        
        # Step 3: Encode prediction data with the same encoders
        encoded_pred, _ = process_encode_data(pred_data, label_encoders=encoders)
        
        # Step 4: Prepare features for prediction
        X_pred, _ = prepare_feature_data(encoded_pred, is_training=False)
        
        # Should have the same columns as training data
        extra_cols = set(X_pred.columns) - set(X_train.columns)
        missing_cols = set(X_train.columns) - set(X_pred.columns)
        
        # Log different columns if any
        if extra_cols:
            print(f"Extra columns in prediction data: {extra_cols}")
        if missing_cols:
            print(f"Missing columns in prediction data: {missing_cols}")
        
        # Final columns should match (or prediction data should be a subset)
        self.assertTrue(all(col in X_train.columns for col in X_pred.columns))


if __name__ == '__main__':
    unittest.main() 