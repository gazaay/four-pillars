#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Utilities Module

This module provides shared functions for data preparation and transformation
that can be used across different parts of the codebase.
"""

import pandas as pd
import numpy as np
import logging

# Set up logger
logger = logging.getLogger('GFAnalytics.DataUtils')


def prepare_feature_data(data, is_training=True):
    """
    Prepare feature data for training or prediction.
    
    Args:
        data (pandas.DataFrame): Input data
        is_training (bool): Whether this is training data
        
    Returns:
        tuple: (X, y) if is_training=True, (X, None) if is_training=False
               where X is features DataFrame and y is target Series
    """
    if data is None or data.empty:
        if is_training:
            return pd.DataFrame(), pd.Series(dtype=float)
        else:
            return pd.DataFrame(), None
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create a copy to avoid modifying original data
        df = data.copy()
        
        # List of specific columns to drop
        columns_to_drop = [
            'year', 'time'  # Year column (user doesn't want)
            'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits',  # Stock price data
            # Also drop _x and _y variants
            'Open_x', 'High_x', 'Low_x', 'Close_x', 'Volume_x', 'Dividends_x', 'Stock Splits_x',
            'Open_y', 'High_y', 'Low_y', 'Close_y', 'Volume_y', 'Dividends_y', 'Stock Splits_y'
        ]
        
        # Filter out columns that don't exist in dataframe
        columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        
        if columns_to_drop:
            logger.info(f"Dropping columns: {columns_to_drop}")
            df = df.drop(columns=columns_to_drop)
        
        # Handle Chinese characters by encoding them to numbers
        for col in df.columns:
            if col != 'target':  # Don't convert target column
                try:
                    # If column contains Chinese characters, try to encode them
                    if df[col].dtype == 'object':
                        # Check if it contains Chinese characters
                        sample_values = df[col].dropna().head(5)
                        has_chinese = any(
                            isinstance(val, str) and any('\u4e00' <= char <= '\u9fff' for char in val)
                            for val in sample_values
                        )
                        
                        if has_chinese:
                            # Try to convert Chinese characters to numeric codes
                            df[col] = df[col].astype(str).apply(
                                lambda x: hash(x) % 10000 if isinstance(x, str) and any('\u4e00' <= c <= '\u9fff' for c in x) else x
                            )
                    
                    # Convert to numeric
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Could not process column {col}: {e}")
        
        # Drop columns with all NaN values
        df = df.dropna(axis=1, how='all')
        
        if is_training:
            # For training, separate features and target
            if 'target' not in df.columns:
                logger.error("No target column found in training data")
                return pd.DataFrame(), pd.Series(dtype=float)
            
            # Separate features (X) and target (y)
            X = df.drop('target', axis=1)
            y = df['target']
            
            logger.info(f"Prepared training data: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y
        else:
            # For prediction, return only features (no target expected)
            X = df
            logger.info(f"Prepared prediction data: {X.shape[0]} samples, {X.shape[1]} features")
            return X, None
        
    except Exception as e:
        logger.error(f"Error in prepare_feature_data: {e}")
        if is_training:
            return pd.DataFrame(), pd.Series(dtype=float)
        else:
            return pd.DataFrame(), None
    

def get_feature_importance(model, feature_names=None):
    """
    Get feature importance from a trained model.
    
    Args:
        model: The trained model with feature_importances_ attribute.
        feature_names (list, optional): List of feature names. If None, will use 
                                        model.feature_names_in_ if available.
    
    Returns:
        pandas.DataFrame: DataFrame with feature names and importance scores, 
                         sorted by importance.
    """
    logger.info("Calculating feature importance")
    
    # Check if model is a wrapper (like RandomForestModel) or the actual model
    if hasattr(model, 'model') and model.model is not None:
        actual_model = model.model
    else:
        actual_model = model
    
    # Check if model has feature_importances_ attribute
    if not hasattr(actual_model, 'feature_importances_'):
        logger.warning("Model does not have feature_importances_ attribute")
        return None
    
    # Get feature importance
    importance = actual_model.feature_importances_
    
    # Use appropriate feature names
    if feature_names is None:
        if hasattr(model, 'feature_names') and model.feature_names is not None:
            feature_names = model.feature_names
        elif hasattr(actual_model, 'feature_names_in_'):
            feature_names = actual_model.feature_names_in_
        else:
            feature_names = [f"feature_{i}" for i in range(len(importance))]
    
    # Create a DataFrame with feature names and importance
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    })
    
    # Sort by importance
    feature_importance = feature_importance.sort_values('importance', ascending=False)
    
    return feature_importance 