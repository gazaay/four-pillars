#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bazi Data Generation Module for GFAnalytics

This module provides functionality to generate Bazi (八字) data based on stock data timestamps,
leveraging the existing Bazi functionality in the codebase.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import Bazi functionality from the existing codebase
from app import bazi

# Import utilities
from GFAnalytics.utils.time_utils import ensure_hk_timezone, convert_df_timestamps_to_hk

# Set up logger
logger = logging.getLogger('GFAnalytics.bazi_data')


class BaziDataGenerator:
    """
    Class for generating Bazi data based on stock data timestamps.
    """
    
    def __init__(self, config):
        """
        Initialize the BaziDataGenerator.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        logger.info("BaziDataGenerator initialized")
    
    def generate(self, stock_data):
        """
        Generate Bazi data for the given stock data.
        
        Args:
            stock_data (pandas.DataFrame): The stock data with timestamps.
            
        Returns:
            pandas.DataFrame: The generated Bazi data.
        """
        logger.info("Generating Bazi data")
        
        # Make a copy of the stock data to avoid modifying the original
        data = stock_data.copy()
        
        # Ensure the time column is in Hong Kong timezone
        data = convert_df_timestamps_to_hk(data, 'time')
        
        # Get the stock's listing date
        from GFAnalytics.data.stock_data import StockDataLoader
        stock_loader = StockDataLoader(self.config)
        listing_date = stock_loader.get_listing_date()
        
        # Generate base Bazi pillars for the stock's listing date
        base_pillars = self._generate_base_pillars(listing_date)
        
        # Generate current Bazi pillars for each timestamp in the stock data
        data = self._generate_current_pillars(data)
        
        # Add base pillars to the data
        for key, value in base_pillars.items():
            column_name = f'base_{key}'
            data[column_name] = value
        
        # Add stock code and UUID columns if they don't exist
        if 'stock_code' not in data.columns:
            data['stock_code'] = self.config['stock']['code']
        
        if 'uuid' not in data.columns:
            data['uuid'] = pd.util.hash_pandas_object(data).astype(str)
        
        # Add last modified date if it doesn't exist
        if 'last_modified_date' not in data.columns:
            data['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
        
        logger.info(f"Generated Bazi data with {len(data)} records")
        return data
    
    def _generate_base_pillars(self, listing_date):
        """
        Generate base Bazi pillars for the stock's listing date.
        
        Args:
            listing_date (datetime): The listing date of the stock.
            
        Returns:
            dict: A dictionary of base Bazi pillars.
        """
        logger.info(f"Generating base Bazi pillars for listing date: {listing_date}")
        
        # Ensure the listing date is in Hong Kong timezone
        listing_date = ensure_hk_timezone(listing_date)
        
        try:
            # Generate base Bazi pillars using the existing bazi module
            base_pillars = bazi.get_heavenly_branch_ymdh_pillars_base(
                listing_date.year,
                listing_date.month,
                listing_date.day,
                listing_date.hour
            )
            
            # Map the keys to more descriptive names
            key_mapping = {
                '年': 'year_pillar',
                '月': 'month_pillar',
                '日': 'day_pillar',
                '時': 'hour_pillar',
                '-月': 'month_pillar_minus',
                '-時': 'hour_pillar_minus'
            }
            
            # Create a new dictionary with the mapped keys
            mapped_pillars = {key_mapping.get(k, k): v for k, v in base_pillars.items()}
            
            logger.info(f"Base Bazi pillars generated: {mapped_pillars}")
            return mapped_pillars
        except Exception as e:
            logger.error(f"Failed to generate base Bazi pillars: {str(e)}")
            
            # Return empty pillars if generation fails
            return {
                'year_pillar': '',
                'month_pillar': '',
                'day_pillar': '',
                'hour_pillar': '',
                'month_pillar_minus': '',
                'hour_pillar_minus': ''
            }
    
    def _generate_current_pillars(self, data):
        """
        Generate current Bazi pillars for each timestamp in the data.
        
        Args:
            data (pandas.DataFrame): The data with timestamps.
            
        Returns:
            pandas.DataFrame: The data with added current Bazi pillars.
        """
        logger.info("Generating current Bazi pillars for each timestamp")
        
        # Create a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Define a function to generate pillars for a single timestamp
        def generate_pillars_for_timestamp(row):
            try:
                # Get the timestamp
                timestamp = row['time']
                logger.info(f"Processing row: {row}")
                logger.info(f"Processing Bazi pillars for timestamp: {timestamp}")
                # Ensure the timestamp is in Hong Kong timezone
                timestamp = ensure_hk_timezone(timestamp)
                logger.info(f"Converted timestamp to HK timezone: {timestamp}")
                
                # Generate current Bazi pillars using the existing bazi module
                current_pillars = bazi.get_heavenly_branch_ymdh_pillars_current_flip_Option_2(
                    timestamp.year,
                    timestamp.month,
                    timestamp.day,
                    timestamp.hour,
                    auto_adjust=True,
                    progress=False  # This helped avoid JSON decode errors
                )
                
                # Map the keys to more descriptive names
                key_mapping = {
                    '年': 'current_year_pillar',
                    '月': 'current_month_pillar',
                    '日': 'current_day_pillar',
                    '時': 'current_hour_pillar',
                    '-月': 'current_month_pillar_minus',
                    '-時': 'current_hour_pillar_minus'
                }
                
                # Create a new dictionary with the mapped keys
                mapped_pillars = {key_mapping.get(k, k): v for k, v in current_pillars.items()}
                
                return pd.Series(mapped_pillars)
            except Exception as e:
                logger.error(f"Failed to generate current Bazi pillars for timestamp {timestamp}: {str(e)}")
                
                # Return empty pillars if generation fails
                return pd.Series({
                    'current_year_pillar': '',
                    'current_month_pillar': '',
                    'current_day_pillar': '',
                    'current_hour_pillar': '',
                    'current_month_pillar_minus': '',
                    'current_hour_pillar_minus': ''
                })
        
        # Apply the function to each row
        pillars_df = result.apply(generate_pillars_for_timestamp, axis=1)
        
        # Concatenate the original data with the generated pillars
        result = pd.concat([result, pillars_df], axis=1)
        
        logger.info("Current Bazi pillars generated for all timestamps")
        return result
    
    def get_bazi_for_date(self, date):
        """
        Get Bazi pillars for a specific date.
        
        Args:
            date (datetime): The date to get Bazi pillars for.
            
        Returns:
            dict: A dictionary of Bazi pillars.
        """
        # Ensure the date is in Hong Kong timezone
        date = ensure_hk_timezone(date)
        
        try:
            # Generate Bazi pillars using the existing bazi module
            pillars = bazi.get_heavenly_branch_ymdh_pillars_current_flip_Option_2(
                date.year,
                date.month,
                date.day,
                date.hour,
                is_current=True
            )
            
            # Map the keys to more descriptive names
            key_mapping = {
                '年': 'year_pillar',
                '月': 'month_pillar',
                '日': 'day_pillar',
                '時': 'hour_pillar',
                '-月': 'month_pillar_minus',
                '-時': 'hour_pillar_minus'
            }
            
            # Create a new dictionary with the mapped keys
            mapped_pillars = {key_mapping.get(k, k): v for k, v in pillars.items()}
            
            return mapped_pillars
        except Exception as e:
            logger.error(f"Failed to get Bazi pillars for date {date}: {str(e)}")
            
            # Return empty pillars if generation fails
            return {
                'year_pillar': '',
                'month_pillar': '',
                'day_pillar': '',
                'hour_pillar': '',
                'month_pillar_minus': '',
                'hour_pillar_minus': ''
            } 