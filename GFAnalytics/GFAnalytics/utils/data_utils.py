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
    Prepare feature data for model training or prediction by removing 
    non-feature columns and handling missing values.
    
    Args:
        data (pandas.DataFrame): The data to prepare.
        is_training (bool): Whether the data is for training (includes target column).
        
    Returns:
        tuple: A tuple containing (X, y) if is_training is True, otherwise (X, None).
    """
    # Create a copy of the data to avoid modifying the original
    df = data.copy()
    
    # Drop non-feature columns
    columns_to_drop = ['time', 'uuid', 'last_modified_date', 'batch_id']
    if is_training:
        columns_to_drop.append('target')
    
    # Drop columns that exist in the DataFrame
    columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    
    # Drop batch_id if it exists
    if 'batch_id' in df.columns:
        df = df.drop('batch_id', axis=1)
    
    # Drop stock code and RIC code columns, including variants like stock_code_x
    for col in df.columns:
        if 'stock_code' in col or 'ric_code' in col or 'uuid' in col or 'last_modified_date' in col:
            columns_to_drop.append(col)
    
    # Drop original categorical features that have been encoded
    encoded_columns = [col for col in df.columns if col.startswith('encoded_')]
    original_encoded = [col.replace('encoded_', '') for col in encoded_columns]
    
    # Only drop original columns if they have encoded versions
    for col in original_encoded:
        if col in df.columns:
            columns_to_drop.append(col)
    
    # Drop columns that end with _y (usually duplicates from merges)
    y_columns = [col for col in df.columns if col.endswith('_y')]
    columns_to_drop.extend(y_columns)
    
    # Drop non-numeric columns
    non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    for col in non_numeric_cols:
        if col not in columns_to_drop and col != 'target':
            columns_to_drop.append(col)
    
    # Remove duplicates from columns_to_drop
    columns_to_drop = list(set(columns_to_drop))
    
    # Prepare features (X)
    X = df.drop(columns_to_drop, axis=1, errors='ignore')
    
    # Replace any infinities with NaNs, then fill NaNs with 0
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0)
    
    # Log feature information
    logger.info(f"Using {X.shape[1]} features for {'training' if is_training else 'prediction'}")
    logger.debug(f"Feature dtypes:\n{X.dtypes}")
    
    # Prepare target (y) if training
    y = None
    if is_training and 'target' in df.columns:
        y = df['target']
        logger.debug(f"Target shape: {y.shape}")
    
    return X, y

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