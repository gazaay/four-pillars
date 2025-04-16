#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoding Utilities Module

This module provides utilities for encoding categorical features in DataFrames.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import logging

logger = logging.getLogger('GFAnalytics.EncodingUtils')

def get_categorical_columns(df):
    """
    Identify categorical columns in a DataFrame.
    
    Args:
        df (pandas.DataFrame): The DataFrame to analyze.
        
    Returns:
        list: A list of column names that are likely categorical.
    """
    categorical_cols = []
    
    for col in df.columns:
        # Skip columns that are likely not categorical
        if col in ['time', 'date', 'stock_code', 'open', 'high', 'low', 'close', 'volume']:
            continue
            
        # Skip numerical columns
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
            
        # If column contains string data or has few unique values relative to total rows
        # (less than 5% of total rows), consider it categorical
        if (pd.api.types.is_string_dtype(df[col]) or 
            (df[col].nunique() < max(20, len(df) * 0.05))):
            categorical_cols.append(col)
    
    return categorical_cols

def encode_column(data, column, encoder=None):
    """
    Encode a single categorical column using LabelEncoder.
    
    Args:
        data (pandas.DataFrame): The DataFrame containing the column to encode.
        column (str): The name of the column to encode.
        encoder (sklearn.preprocessing.LabelEncoder, optional): An existing encoder to use.
            If None, a new encoder will be created.
            
    Returns:
        tuple: 
            - pandas.Series: The encoded column.
            - sklearn.preprocessing.LabelEncoder: The encoder used.
    """
    # Create a copy of the data to avoid modifying the original
    values = data[column].astype(str).copy()
    
    # Handle NaN values
    values = values.fillna('unknown')
    
    # Create or use the encoder
    if encoder is None:
        encoder = LabelEncoder()
        encoder.fit(values)
    
    # Transform the values, handling any new categories
    try:
        encoded_values = encoder.transform(values)
    except ValueError as e:
        # Handle new categories not seen during fitting
        logger.warning(f"New categories found in column '{column}'. Adding them to encoder.")
        # Get current classes
        current_classes = set(encoder.classes_)
        # Get all unique values in the column
        all_values = set(values.unique())
        # Find new classes
        new_classes = all_values - current_classes
        
        # Refit the encoder with all classes
        encoder = LabelEncoder()
        encoder.fit(list(current_classes) + list(new_classes))
        
        # Transform the values
        encoded_values = encoder.transform(values)
    
    return pd.Series(encoded_values, index=data.index), encoder

def process_encode_data(data, label_encoders=None):
    """
    Process and encode categorical features in a DataFrame.
    
    Args:
        data (pandas.DataFrame): The DataFrame to process.
        label_encoders (dict, optional): Dictionary mapping column names to LabelEncoders.
            If None, new encoders will be created.
            
    Returns:
        tuple:
            - pandas.DataFrame: The processed DataFrame with encoded categorical features.
            - dict: Dictionary mapping column names to LabelEncoders used.
    """
    # Create a copy of the data to avoid modifying the original
    processed_data = data.copy()
    
    # Initialize encoders dictionary if not provided
    if label_encoders is None:
        label_encoders = {}
    
    # Get categorical columns
    cat_columns = get_categorical_columns(data)
    
    # Encode each categorical column
    for col in cat_columns:
        # Skip columns that should not be encoded
        if col in ['time', 'date']:
            continue
            
        try:
            # Use existing encoder if available
            encoder = label_encoders.get(col)
            
            # Encode the column
            encoded_col, encoder = encode_column(processed_data, col, encoder)
            
            # Store the encoder
            label_encoders[col] = encoder
            
            # Replace the original column with the encoded version
            processed_data[col] = encoded_col
            
        except Exception as e:
            logger.error(f"Error encoding column '{col}': {str(e)}")
            # Keep the original column unchanged
    
    return processed_data, label_encoders

def decode_prediction_data(predictions, target_encoder=None):
    """
    Decode prediction data back to original categories.
    
    Args:
        predictions (numpy.ndarray): Predicted values from a model.
        target_encoder (sklearn.preprocessing.LabelEncoder, optional): The encoder used for the target variable.
            If None, the predictions are returned as is.
            
    Returns:
        numpy.ndarray: Decoded predictions.
    """
    if target_encoder is None:
        return predictions
        
    try:
        return target_encoder.inverse_transform(predictions.astype(int))
    except Exception as e:
        logger.error(f"Error decoding predictions: {str(e)}")
        return predictions 