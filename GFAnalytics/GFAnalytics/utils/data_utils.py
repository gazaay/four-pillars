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


def apply_column_filtering(data, config):
    """
    Apply simple column filtering based on configuration.
    
    Args:
        data (pandas.DataFrame): Input data to filter
        config (dict): Configuration dictionary with filtering settings
        
    Returns:
        pandas.DataFrame: Filtered data
    """
    if not config.get('model', {}).get('features', {}).get('filtering', {}).get('enabled', False):
        logger.debug("Column filtering is disabled")
        return data
    
    logger.info("🔧 Applying column filtering...")
    filtered_data = data.copy()
    filtering_config = config['model']['features']['filtering']
    
    initial_columns = len(filtered_data.columns)
    columns_to_drop = set()
    
    # Apply base pillars filtering
    base_config = filtering_config.get('base_pillars', {})
    if base_config.get('include_patterns') or base_config.get('exclude_patterns'):
        columns_to_drop.update(_filter_by_patterns(filtered_data, base_config, 'base_'))
    
    # Apply current pillars filtering  
    current_config = filtering_config.get('current_pillars', {})
    if current_config.get('include_patterns') or current_config.get('exclude_patterns'):
        columns_to_drop.update(_filter_by_patterns(filtered_data, current_config, 'current_'))
    
    # Apply ChengShen filtering
    cs_config = filtering_config.get('chengshen', {})
    if cs_config.get('include_patterns') or cs_config.get('exclude_patterns'):
        columns_to_drop.update(_filter_chengshen_columns(filtered_data, cs_config))
    
    # Apply custom filtering (applies to all columns)
    custom_config = filtering_config.get('custom', {})
    if custom_config.get('include_patterns') or custom_config.get('exclude_patterns'):
        columns_to_drop.update(_filter_by_patterns(filtered_data, custom_config, ''))
    
    # Remove the columns
    if columns_to_drop:
        filtered_data = filtered_data.drop(columns=list(columns_to_drop))
        logger.info(f"📊 Filtered {len(columns_to_drop)} columns ({initial_columns} -> {len(filtered_data.columns)})")
        logger.info(f"   Dropped columns: {sorted(list(columns_to_drop))[:10]}{'...' if len(columns_to_drop) > 10 else ''}")
    else:
        logger.info("📊 No columns filtered")
    
    return filtered_data


def _filter_by_patterns(data, config, prefix):
    """Filter columns by include/exclude patterns with optional prefix."""
    columns_to_drop = set()
    include_patterns = config.get('include_patterns', [])
    exclude_patterns = config.get('exclude_patterns', [])
    
    # Get columns that match the prefix (if any)
    if prefix:
        relevant_columns = [col for col in data.columns if col.startswith(prefix)]
    else:
        relevant_columns = list(data.columns)
    
    for col in relevant_columns:
        # Check exclude patterns first
        should_exclude = any(pattern in col for pattern in exclude_patterns)
        
        # If include patterns specified, column must match at least one
        if include_patterns:
            should_include = any(pattern in col for pattern in include_patterns)
            if not should_include:
                should_exclude = True
        
        if should_exclude:
            columns_to_drop.add(col)
    
    return columns_to_drop


def _filter_chengshen_columns(data, config):
    """Filter ChengShen columns specifically."""
    columns_to_drop = set()
    include_patterns = config.get('include_patterns', [])
    exclude_patterns = config.get('exclude_patterns', [])
    
    # Find ChengShen related columns
    cs_keywords = ['chengshen', '生', '克', '泄', '耗']
    cs_columns = [col for col in data.columns if any(keyword in col for keyword in cs_keywords)]
    
    for col in cs_columns:
        # Check exclude patterns first
        should_exclude = any(pattern in col for pattern in exclude_patterns)
        
        # If include patterns specified, column must match at least one
        if include_patterns:
            should_include = any(pattern in col for pattern in include_patterns)
            if not should_include:
                should_exclude = True
        
        if should_exclude:
            columns_to_drop.add(col)
    
    return columns_to_drop


def prepare_feature_data(data, is_training=True, config=None):
    """
    Prepare feature data for training or prediction.
    
    Args:
        data (pandas.DataFrame): Input data
        is_training (bool): Whether this is training data
        config (dict, optional): Configuration dictionary for filtering
        
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
        
        # STEP 1: Apply dataset filtering if config is provided
        if config is not None:
            df = apply_column_filtering(df, config)
        
        # STEP 2: List of specific columns to drop
        columns_to_drop = [
            # Time-related columns (comprehensive list)
            'year', 'time',  'datetime', 'timestamp', 'month', 'day', 'hour', 
            'dayofweek', 'dayofyear', 'weekofyear', 'quarter',
            'is_year_start', 'is_year_end', 'is_quarter_start', 'is_quarter_end', 
            'is_month_start', 'is_month_end',
            # Stock price data columns that can cause data leakage
            'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits',
            # Also drop _x and _y variants
            'Open_x', 'High_x', 'Low_x', 'Close_x', 'Volume_x', 'Dividends_x', 'Stock Splits_x',
            'Open_y', 'High_y', 'Low_y', 'Close_y', 'Volume_y', 'Dividends_y', 'Stock Splits_y',
            # Additional metadata columns
            'uuid', 'uuid_x', 'uuid_y', 'last_modified_date', 'last_modified_date_x', 'last_modified_date_y',
            'stock_code', 'stock_code_x', 'stock_code_y', 'ric_code', 'ric_code_x', 'ric_code_y'
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