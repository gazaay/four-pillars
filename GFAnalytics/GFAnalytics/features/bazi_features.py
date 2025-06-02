#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bazi Feature Transformer Module for GFAnalytics

This module provides functionality to transform Bazi data into features for machine learning,
including combining with stock data.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# Import utilities
from GFAnalytics.utils.time_utils import ensure_hk_timezone, convert_df_timestamps_to_hk

# Set up logger
logger = logging.getLogger('GFAnalytics.bazi_features')


class BaziFeatureTransformer:
    """
    Class for transforming Bazi data into features for machine learning.
    """
    
    def __init__(self, config):
        """
        Initialize the BaziFeatureTransformer.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        logger.info("BaziFeatureTransformer initialized")
    
    def transform(self, data):
        """
        Transform Bazi data into features for machine learning.
        
        Args:
            data (pandas.DataFrame): The Bazi data to transform.
            
        Returns:
            pandas.DataFrame: The transformed data.
        """
        logger.info("Transforming Bazi data into features")
        
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Ensure the time column is in Hong Kong timezone
        result = convert_df_timestamps_to_hk(result, 'time')
        
        # Add time-based features
        result = self._add_time_features(result)
        
        # Add cyclical features for Bazi pillars
        result = self._add_cyclical_features(result)
        
        logger.info("Bazi data transformed into features successfully")
        return result
    
    def _add_time_features(self, data):
        """
        Add time-based features to the data.
        
        Args:
            data (pandas.DataFrame): The data to add features to.
            
        Returns:
            pandas.DataFrame: The data with added time-based features.
        """
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Extract time components
        result['year'] = result['time'].dt.year
        result['month'] = result['time'].dt.month
        result['day'] = result['time'].dt.day
        result['hour'] = result['time'].dt.hour
        result['dayofweek'] = result['time'].dt.dayofweek
        result['quarter'] = result['time'].dt.quarter
        result['is_month_start'] = result['time'].dt.is_month_start
        result['is_month_end'] = result['time'].dt.is_month_end
        result['is_quarter_start'] = result['time'].dt.is_quarter_start
        result['is_quarter_end'] = result['time'].dt.is_quarter_end
        result['is_year_start'] = result['time'].dt.is_year_start
        result['is_year_end'] = result['time'].dt.is_year_end
        
        # Add day of year
        result['dayofyear'] = result['time'].dt.dayofyear
        
        # Add week of year
        result['weekofyear'] = result['time'].dt.isocalendar().week
        
        return result
    
    def _add_cyclical_features(self, data):
        """
        Add cyclical features for Bazi pillars.
        
        Args:
            data (pandas.DataFrame): The data to add features to.
            
        Returns:
            pandas.DataFrame: The data with added cyclical features.
        """
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Define the heavenly stems and earthly branches
        heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # Find all Bazi pillar columns
        pillar_columns = [col for col in result.columns if 'pillar' in col]
        
        # Add cyclical features for each pillar
        for col in pillar_columns:
            # Extract heavenly stem and earthly branch
            result[f'{col}_heavenly'] = result[col].apply(lambda x: x[0] if isinstance(x, str) and len(x) > 0 else '')
            result[f'{col}_earthly'] = result[col].apply(lambda x: x[1] if isinstance(x, str) and len(x) > 1 else '')
            
            # Create cyclical features for heavenly stems
            result[f'{col}_heavenly_sin'] = result[f'{col}_heavenly'].apply(
                lambda x: np.sin(2 * np.pi * heavenly_stems.index(x) / len(heavenly_stems)) if x in heavenly_stems else 0
            )
            result[f'{col}_heavenly_cos'] = result[f'{col}_heavenly'].apply(
                lambda x: np.cos(2 * np.pi * heavenly_stems.index(x) / len(heavenly_stems)) if x in heavenly_stems else 0
            )
            
            # Create cyclical features for earthly branches
            result[f'{col}_earthly_sin'] = result[f'{col}_earthly'].apply(
                lambda x: np.sin(2 * np.pi * earthly_branches.index(x) / len(earthly_branches)) if x in earthly_branches else 0
            )
            result[f'{col}_earthly_cos'] = result[f'{col}_earthly'].apply(
                lambda x: np.cos(2 * np.pi * earthly_branches.index(x) / len(earthly_branches)) if x in earthly_branches else 0
            )
        
        return result
    
    def combine_with_stock_data(self, bazi_features, stock_data):
        """
        Combine Bazi features with stock data.
        
        Args:
            bazi_features (pandas.DataFrame): The Bazi features.
            stock_data (pandas.DataFrame): The stock data.
            
        Returns:
            pandas.DataFrame: The combined data.
        """
        logger.info("Combining Bazi features with stock data")
        
        # Make copies of the data to avoid modifying the originals
        bazi_df = bazi_features.copy()
        stock_df = stock_data.copy()
        
        # Ensure both DataFrames have the time column in Hong Kong timezone
        bazi_df = convert_df_timestamps_to_hk(bazi_df, 'time')
        stock_df = convert_df_timestamps_to_hk(stock_df, 'time')
        
        # Merge the DataFrames on the time column
        merged_df = pd.merge(bazi_df, stock_df, on='time', how='inner')
        
        # Add target variable (next day's close price)
        merged_df = self._add_target_variable(merged_df)
        
        logger.info(f"Combined data has {len(merged_df)} rows")
        return merged_df
    
    def _add_target_variable(self, data):
        """
        Add target variable to the data.
        
        Args:
            data (pandas.DataFrame): The data to add the target variable to.
            
        Returns:
            pandas.DataFrame: The data with added target variable.
        """
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Sort by time
        result = result.sort_values('time')
        # Print results and check columns
        logger.info(f"Data shape before target: {result.shape}")
        logger.info(f"Columns in dataset: {result.columns.tolist()}")
        logger.debug(f"First few rows:\n{result.head()}")
        
        # Check for any missing values
        missing_values = result.isnull().sum()
        if missing_values.any():
            logger.warning(f"Missing values found:\n{missing_values[missing_values > 0]}")
        
        # FIXED: Use Close_y (actual HSI stock values) instead of Close_x (wrong Bazi values)
        # Close_x contains wrong values (~150-160), Close_y contains correct HSI values (~16,000-17,000)
        result['target'] = result['Close_y'].shift(-1)
        
        # Drop the last row (which has NaN target)
        result = result.dropna(subset=['target'])
        
        return result
    
    def create_training_dataset(self, data):
        """
        Create a training dataset from the combined data.
        
        Args:
            data (pandas.DataFrame): The combined data.
            
        Returns:
            tuple: A tuple containing (X_train, X_test, y_train, y_test).
        """
        logger.info("Creating training dataset")
        
        # Make a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Define features and target
        features = df.drop(['time', 'target', 'uuid', 'last_modified_date'], axis=1, errors='ignore')
        target = df['target']
        
        # Split the data into training and testing sets
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=0.2, random_state=42
        )
        
        logger.info(f"Training dataset created with {len(X_train)} training samples and {len(X_test)} testing samples")
        return X_train, X_test, y_train, y_test 