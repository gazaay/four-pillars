#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChengShen Transformation Module for GFAnalytics

This module provides functionality to transform Bazi pillars to ChengShen (長生) attributes,
leveraging the existing ChengShen functionality in the codebase.
"""

import logging
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import ChengShen functionality from the existing codebase
from app import chengseng

# Set up logger
logger = logging.getLogger('GFAnalytics.chengshen')


class ChengShenTransformer:
    """
    Class for transforming Bazi pillars to ChengShen attributes.
    """
    
    def __init__(self, config):
        """
        Initialize the ChengShenTransformer.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        logger.info("ChengShenTransformer initialized")
    
    def transform(self, data):
        """
        Transform Bazi pillars to ChengShen attributes.
        
        Args:
            data (pandas.DataFrame): The data with Bazi pillars.
            
        Returns:
            pandas.DataFrame: The data with added ChengShen attributes.
        """
        logger.info("Transforming Bazi pillars to ChengShen attributes")
        
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        try:
            # Use the existing chengseng module to create ChengShen attributes
            result = self._create_chengshen_for_dataset(result)
            
            logger.info("ChengShen attributes created successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to transform Bazi pillars to ChengShen attributes: {str(e)}")
            
            # Return the original data if transformation fails
            return data
    
    def _create_chengshen_for_dataset(self, data):
        """
        Create ChengShen attributes for the dataset.
        
        Args:
            data (pandas.DataFrame): The data with Bazi pillars.
            
        Returns:
            pandas.DataFrame: The data with added ChengShen attributes.
        """
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Define the base and current sets
        base_sets = {
            'base_hour_pillar': 'base_hour',
            'base_day_pillar': 'base_day',
            'base_hour_pillar_minus': 'base_hour_minus',
            'base_month_pillar': 'base_month',
            'base_year_pillar': 'base_year',
            'base_month_pillar_minus': 'base_month_minus'
        }
        
        current_sets = {
            'current_hour_pillar': 'current_hour',
            'current_day_pillar': 'current_day',
            'current_hour_pillar_minus': 'current_hour_minus',
            'current_month_pillar': 'current_month',
            'current_year_pillar': 'current_year',
            'current_month_pillar_minus': 'current_month_minus'
        }
        
        # Create ChengShen attributes for each combination of base and current sets
        for base_col, base_name in base_sets.items():
            for current_col, current_name in current_sets.items():
                # Create column name for the ChengShen attribute
                col_name = f"cs_{base_name}_{current_name}"
                
                # Extract heavenly stem from base pillar
                base_heavenly = result[base_col].apply(self._get_heavenly)
                
                # Extract earthly branch from current pillar
                current_earthly = result[current_col].apply(self._get_earthly)
                
                # Combine heavenly stem and earthly branch
                result[col_name] = base_heavenly + current_earthly
                
                # Apply ChengShen transformation
                result[col_name] = result[col_name].apply(self._get_cheung_sheng)
        
        return result
    
    def _get_heavenly(self, input_string):
        """
        Get the heavenly stem (first character) from a Chinese string.
        
        Args:
            input_string (str): The input string.
            
        Returns:
            str: The heavenly stem (first character).
        """
        if pd.isna(input_string) or not isinstance(input_string, str):
            return ''
        elif len(input_string) >= 1:
            return input_string[0]
        else:
            return ''
    
    def _get_earthly(self, input_string):
        """
        Get the earthly branch (second character) from a Chinese string.
        
        Args:
            input_string (str): The input string.
            
        Returns:
            str: The earthly branch (second character).
        """
        if pd.isna(input_string) or not isinstance(input_string, str):
            return ''
        elif len(input_string) >= 2:
            return input_string[1]
        else:
            return ''
    
    def _get_cheung_sheng(self, stem_branch):
        """
        Get the ChengShen attribute for a stem-branch combination.
        
        Args:
            stem_branch (str): The stem-branch combination.
            
        Returns:
            str: The ChengShen attribute.
        """
        # Use the existing chengseng module to get the ChengShen attribute
        try:
            return chengseng.get_cheung_sheng(stem_branch)
        except Exception as e:
            logger.error(f"Failed to get ChengShen attribute for {stem_branch}: {str(e)}")
            return ''
    
    def encode_chengshen(self, data):
        """
        Encode ChengShen attributes to numeric values.
        
        Args:
            data (pandas.DataFrame): The data with ChengShen attributes.
            
        Returns:
            pandas.DataFrame: The data with encoded ChengShen attributes.
        """
        logger.info("Encoding ChengShen attributes")
        
        # Make a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Define the ChengShen encoding mapping
        chengshen_encoding = {
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
        
        # Find all ChengShen columns
        chengshen_columns = [col for col in result.columns if col.startswith('cs_')]
        
        # Encode each ChengShen column
        for col in chengshen_columns:
            # Create a new column for the encoded value
            encoded_col = f"encoded_{col}"
            
            # Encode the ChengShen attribute
            result[encoded_col] = result[col].map(chengshen_encoding)
            
            # Fill NaN values with 0
            result[encoded_col] = result[encoded_col].fillna(0).astype(int)
        
        logger.info("ChengShen attributes encoded successfully")
        return result 