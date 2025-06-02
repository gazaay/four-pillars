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
from bazi import bazi

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
        logger.debug(f"Adding base pillars to data. Base pillars: {base_pillars}")
        for key, value in base_pillars.items():
            column_name = f'base_{key}'
            if column_name in data.columns:
                logger.warning(f"Column '{column_name}' already exists, overwriting...")
            logger.info(f"Added column '{column_name}' with value '{value}'")
            data[column_name] = value
        
        # Add stock code and UUID columns if they don't exist
        if 'stock_code' not in data.columns:
            data['stock_code'] = self.config['stock']['code']
        
        if 'uuid' not in data.columns:
            data['uuid'] = pd.util.hash_pandas_object(data).astype(str)
        
        # Add last modified date if it doesn't exist
        if 'last_modified_date' not in data.columns:
            data['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
        
        # Final validation to ensure no duplicate columns
        duplicate_cols = data.columns[data.columns.duplicated()].tolist()
        if duplicate_cols:
            logger.error(f"Duplicate columns found in final Bazi data: {duplicate_cols}")
            # Remove duplicates by keeping the first occurrence
            data = data.loc[:, ~data.columns.duplicated()]
            logger.info(f"Removed duplicate columns. Final data shape: {data.shape}")
        
        logger.info(f"Generated Bazi data with {len(data)} records and {len(data.columns)} columns")
        logger.info(f"Final Bazi data columns: {data.columns.tolist()}")
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
            base_pillars = bazi.get_ymdh_base(
                listing_date.year,
                listing_date.month,
                listing_date.day,
                listing_date.hour
            )
            
            # Update 時運 to 大時運 if present
            if '時運' in base_pillars:
                base_pillars['大時運'] = base_pillars.pop('時運')
            
            # Map the keys to more descriptive names
            key_mapping = {
                '年': 'year_pillar',
                '月': 'month_pillar',
                '日': 'day_pillar',
                '時': 'hour_pillar',
                '-月': 'month_pillar_minus',
                '-時': 'hour_pillar_minus',
                '-年': 'year_pillar_minus',
                '-日': 'day_pillar_minus',
                # '大運': 'current_daiyun',
                # '大時運': 'current_siyun'
            }
            # Create a new dictionary with the mapped keys
            mapped_pillars = {v: base_pillars[k] for k, v in key_mapping.items() if k in base_pillars}
            
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
                'hour_pillar_minus': '',
                'year_pillar_minus': '',
                'day_pillar_minus': '',
                # 'current_daiyun': '',
                # 'current_siyun': ''
            }
    
    def _generate_current_pillars(self, data):
        """
        Generate current Bazi pillars for each timestamp in the data.
        
        Args:
            data (pandas.DataFrame): The data with timestamps.
            
        Returns:
            pandas.DataFrame: The data with added current Bazi pillars.
        """
        logger.debug("Generating current Bazi pillars for each timestamp")
        
        # Create a copy of the data to avoid modifying the original
        result = data.copy()
        
        # Define a function to generate pillars for a single timestamp
        def generate_pillars_for_timestamp(row):
            try:
                # Get the timestamp
                timestamp = row['time']
                logger.debug(f"Processing row: {row}")
                logger.debug(f"Processing Bazi pillars for timestamp: {timestamp}")
                # Ensure the timestamp is in Hong Kong timezone
                timestamp = ensure_hk_timezone(timestamp)
                logger.debug(f"Converted timestamp to HK timezone: {timestamp}")
                
                # Generate current Bazi pillars using the existing bazi module
                current_pillars = bazi.get_ymdh_current(
                    timestamp.year,
                    timestamp.month,
                    timestamp.day,
                    timestamp.hour,
                    # auto_adjust=True,
                    # progress=False  # This helped avoid JSON decode errors
                )
                # Update 時運 to 大時運
                if '時運' in current_pillars:
                    current_pillars['大時運'] = current_pillars.pop('時運')

                # Generate current wuxi pillars
                wuxi_pillars = bazi.get_wuxi_current(
                    timestamp.year,
                    timestamp.month, 
                    timestamp.day,
                    timestamp.hour
                )
                
                # Map the keys to more descriptive names
                key_mapping = {
                    '年': 'current_year_pillar',
                    '月': 'current_month_pillar', 
                    '日': 'current_day_pillar',
                    '時': 'current_hour_pillar',
                    '-年': 'current_year_pillar_minus',
                    '-月': 'current_month_pillar_minus',
                    '-日': 'current_day_pillar_minus', 
                    '-時': 'current_hour_pillar_minus',
                    # '大運': 'current_daiyun',
                    # '大時運': 'current_siyun',
                    # Add wuxi mappings
                    '時運': 'current_wuxi_hour',
                    '日運': 'current_wuxi_day',
                    '月運': 'current_wuxi_month',
                    '年運': 'current_wuxi_year'
                }
                
                # Create a new dictionary with only the mapped keys
                mapped_pillars = {key_mapping[k]: v for k, v in current_pillars.items() if k in key_mapping}
                # Add mapped wuxi pillars
                mapped_wuxi = {key_mapping.get(k, k): v for k, v in wuxi_pillars.items()}
                mapped_pillars.update(mapped_wuxi)
                
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
                    'current_hour_pillar_minus': '',
                    'current_wuxi_hour': '',
                    'current_wuxi_day': '',
                    'current_wuxi_month': '',
                    'current_wuxi_year': ''
                })
        
        # Apply the function to each row
        pillars_df = result.apply(generate_pillars_for_timestamp, axis=1)
        
        # Check for overlapping columns between result and pillars_df
        overlapping_cols = set(result.columns).intersection(set(pillars_df.columns))
        if overlapping_cols:
            logger.warning(f"Found overlapping columns: {overlapping_cols}")
            # Drop overlapping columns from pillars_df to avoid duplicates
            pillars_df = pillars_df.drop(columns=list(overlapping_cols))
        
        # Concatenate the original data with the generated pillars (now safe from duplicates)
        result = pd.concat([result, pillars_df], axis=1)
        
        # Final check for duplicate columns
        duplicate_cols = result.columns[result.columns.duplicated()].tolist()
        if duplicate_cols:
            logger.error(f"Duplicate columns detected after concatenation: {duplicate_cols}")
            # Remove duplicate columns by keeping only the first occurrence
            result = result.loc[:, ~result.columns.duplicated()]
            logger.info(f"Removed duplicate columns. Final shape: {result.shape}")
        
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