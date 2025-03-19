#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encoders Module for GFAnalytics

This module provides functionality to encode categorical features for machine learning,
including label encoding and one-hot encoding.
"""

import logging
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

# Set up logger
logger = logging.getLogger('GFAnalytics.encoders')


class FeatureEncoder:
    """
    Class for encoding categorical features for machine learning.
    """
    
    def __init__(self, config):
        """
        Initialize the FeatureEncoder.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.encoding_method = config['model']['features']['encoding']['method']
        self.label_encoders = {}
        self.onehot_encoders = {}
        logger.info(f"FeatureEncoder initialized with method: {self.encoding_method}")
    
    def fit_transform(self, data, categorical_columns=None):
        """
        Fit and transform the data using the specified encoding method.
        
        Args:
            data (pandas.DataFrame): The data to encode.
            categorical_columns (list, optional): List of categorical columns to encode.
                If None, all object and category columns will be encoded.
                
        Returns:
            pandas.DataFrame: The encoded data.
        """
        logger.info("Fitting and transforming data")
        
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # If categorical_columns is not provided, use all object and category columns
        if categorical_columns is None:
            categorical_columns = result.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Filter out columns that don't exist in the data
        categorical_columns = [col for col in categorical_columns if col in result.columns]
        
        logger.info(f"Encoding {len(categorical_columns)} categorical columns")
        
        # Apply the specified encoding method
        if self.encoding_method == 'label_encoding':
            result = self._apply_label_encoding(result, categorical_columns)
        elif self.encoding_method == 'one_hot_encoding':
            result = self._apply_onehot_encoding(result, categorical_columns)
        else:
            logger.warning(f"Unknown encoding method: {self.encoding_method}. Using label encoding.")
            result = self._apply_label_encoding(result, categorical_columns)
        
        logger.info("Data encoded successfully")
        return result
    
    def transform(self, data):
        """
        Transform the data using the fitted encoders.
        
        Args:
            data (pandas.DataFrame): The data to encode.
                
        Returns:
            pandas.DataFrame: The encoded data.
        """
        logger.info("Transforming data using fitted encoders")
        
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Apply the specified encoding method
        if self.encoding_method == 'label_encoding':
            result = self._transform_label_encoding(result)
        elif self.encoding_method == 'one_hot_encoding':
            result = self._transform_onehot_encoding(result)
        else:
            logger.warning(f"Unknown encoding method: {self.encoding_method}. Using label encoding.")
            result = self._transform_label_encoding(result)
        
        logger.info("Data transformed successfully")
        return result
    
    def _apply_label_encoding(self, data, categorical_columns):
        """
        Apply label encoding to the specified columns.
        
        Args:
            data (pandas.DataFrame): The data to encode.
            categorical_columns (list): List of categorical columns to encode.
                
        Returns:
            pandas.DataFrame: The encoded data.
        """
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Apply label encoding to each categorical column
        for col in categorical_columns:
            # Skip columns with all NaN values
            if result[col].isna().all():
                continue
            
            # Fill NaN values with a placeholder
            result[col] = result[col].fillna('unknown')
            
            # Create and fit a label encoder
            le = LabelEncoder()
            result[col] = le.fit_transform(result[col])
            
            # Store the encoder for later use
            self.label_encoders[col] = le
        
        return result
    
    def _transform_label_encoding(self, data):
        """
        Transform the data using the fitted label encoders.
        
        Args:
            data (pandas.DataFrame): The data to encode.
                
        Returns:
            pandas.DataFrame: The encoded data.
        """
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Transform each column that has a fitted encoder
        for col, le in self.label_encoders.items():
            if col in result.columns:
                # Fill NaN values with a placeholder
                result[col] = result[col].fillna('unknown')
                
                # Transform the column using the fitted encoder
                try:
                    result[col] = le.transform(result[col])
                except ValueError as e:
                    # Handle unseen categories
                    logger.warning(f"Error transforming column {col}: {str(e)}")
                    
                    # Create a mapping for unseen categories
                    unique_values = result[col].unique()
                    mapping = {val: i for i, val in enumerate(le.classes_)}
                    
                    # Assign a new index for unseen categories
                    next_index = len(mapping)
                    for val in unique_values:
                        if val not in mapping:
                            mapping[val] = next_index
                            next_index += 1
                    
                    # Apply the mapping
                    result[col] = result[col].map(mapping)
        
        return result
    
    def _apply_onehot_encoding(self, data, categorical_columns):
        """
        Apply one-hot encoding to the specified columns.
        
        Args:
            data (pandas.DataFrame): The data to encode.
            categorical_columns (list): List of categorical columns to encode.
                
        Returns:
            pandas.DataFrame: The encoded data.
        """
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Apply one-hot encoding to each categorical column
        for col in categorical_columns:
            # Skip columns with all NaN values
            if result[col].isna().all():
                continue
            
            # Fill NaN values with a placeholder
            result[col] = result[col].fillna('unknown')
            
            # Create and fit a one-hot encoder
            ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')
            encoded = ohe.fit_transform(result[[col]])
            
            # Create a DataFrame with the encoded values
            encoded_df = pd.DataFrame(
                encoded,
                columns=[f"{col}_{cat}" for cat in ohe.categories_[0]],
                index=result.index
            )
            
            # Store the encoder for later use
            self.onehot_encoders[col] = ohe
            
            # Drop the original column and add the encoded columns
            result = pd.concat([result.drop(col, axis=1), encoded_df], axis=1)
        
        return result
    
    def _transform_onehot_encoding(self, data):
        """
        Transform the data using the fitted one-hot encoders.
        
        Args:
            data (pandas.DataFrame): The data to encode.
                
        Returns:
            pandas.DataFrame: The encoded data.
        """
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Transform each column that has a fitted encoder
        for col, ohe in self.onehot_encoders.items():
            if col in result.columns:
                # Fill NaN values with a placeholder
                result[col] = result[col].fillna('unknown')
                
                # Transform the column using the fitted encoder
                encoded = ohe.transform(result[[col]])
                
                # Create a DataFrame with the encoded values
                encoded_df = pd.DataFrame(
                    encoded,
                    columns=[f"{col}_{cat}" for cat in ohe.categories_[0]],
                    index=result.index
                )
                
                # Drop the original column and add the encoded columns
                result = pd.concat([result.drop(col, axis=1), encoded_df], axis=1)
        
        return result
    
    def get_chengshen_encoding(self):
        """
        Get the ChengShen encoding mapping.
        
        Returns:
            dict: The ChengShen encoding mapping.
        """
        return {
            '長生': 1,  # Birth
            '沐浴': 2,  # Bath
            '冠帶': 3,  # Cap and Belt
            '臨官': 4,  # Official
            '帝旺': 5,  # Emperor
            '衰': 6,    # Decline
            '病': 7,    # Illness
            '死': 8,    # Death
            '墓庫': 9,  # Tomb
            '絕': 10,   # Cut off
            '胎': 11,   # Fetus
            '養': 12    # Nurture
        }
    
    def get_heavenly_stem_encoding(self):
        """
        Get the Heavenly Stem encoding mapping.
        
        Returns:
            dict: The Heavenly Stem encoding mapping.
        """
        return {
            '甲': 1,
            '乙': 2,
            '丙': 3,
            '丁': 4,
            '戊': 5,
            '己': 6,
            '庚': 7,
            '辛': 8,
            '壬': 9,
            '癸': 10
        }
    
    def get_earthly_branch_encoding(self):
        """
        Get the Earthly Branch encoding mapping.
        
        Returns:
            dict: The Earthly Branch encoding mapping.
        """
        return {
            '子': 1,
            '丑': 2,
            '寅': 3,
            '卯': 4,
            '辰': 5,
            '巳': 6,
            '午': 7,
            '未': 8,
            '申': 9,
            '酉': 10,
            '戌': 11,
            '亥': 12
        } 