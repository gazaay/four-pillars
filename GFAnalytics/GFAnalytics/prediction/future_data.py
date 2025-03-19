#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Future Data Generator Module

This module generates future data for prediction based on the configuration.
It creates Bazi attributes for future dates and prepares them for prediction.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from GFAnalytics.utils.time_utils import ensure_hk_timezone
from GFAnalytics.data.bazi_data import BaziDataGenerator
from GFAnalytics.features.bazi_features import BaziFeatureTransformer
from GFAnalytics.features.chengshen import ChengShenTransformer


class FutureDataGenerator:
    """
    Generates future data for prediction.
    
    This class creates a dataset for future dates based on the configuration,
    including Bazi attributes and ChengShen transformations.
    """
    
    def __init__(self, config):
        """
        Initialize the FutureDataGenerator.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger('GFAnalytics.FutureDataGenerator')
        
        # Initialize required components
        self.bazi_generator = BaziDataGenerator(config)
        self.bazi_transformer = BaziFeatureTransformer(config)
        self.chengshen_transformer = ChengShenTransformer(config)
        
    def generate(self, base_date=None):
        """
        Generate future data for prediction.
        
        Args:
            base_date (datetime, optional): Base date for prediction. 
                                           If None, uses current date.
        
        Returns:
            pandas.DataFrame: Future data prepared for prediction.
        """
        self.logger.info("Generating future data for prediction")
        
        # Set base date if not provided
        if base_date is None:
            base_date = ensure_hk_timezone(datetime.now())
        else:
            base_date = ensure_hk_timezone(base_date)
        
        # Get prediction days ahead from config
        days_ahead = self.config['date_range']['prediction']['days_ahead']
        
        # Generate future dates
        future_dates = self._generate_future_dates(base_date, days_ahead)
        
        # Create empty dataframe for future data
        future_data = pd.DataFrame({
            'date': future_dates,
            'stock_code': self.config['stock']['code']
        })
        
        # Generate Bazi data for future dates
        future_bazi_data = self.bazi_generator.generate_for_dates(future_dates)
        
        # Merge with future data
        future_data = pd.merge(future_data, future_bazi_data, on='date', how='left')
        
        # Transform Bazi pillars to features
        bazi_features = self.bazi_transformer.transform(future_data)
        
        # Transform to ChengShen attributes
        chengshen_features = self.chengshen_transformer.transform(bazi_features)
        
        # Add stock launch day Bazi if available
        if 'stock_launch_date' in self.config['stock']:
            launch_date = self.config['stock']['stock_launch_date']
            launch_bazi = self.bazi_generator.generate_for_date(launch_date)
            
            # Add launch Bazi to each row
            for col in launch_bazi.columns:
                if col != 'date':
                    chengshen_features[f'launch_{col}'] = launch_bazi[col].iloc[0]
        
        self.logger.info(f"Generated future data with {len(chengshen_features)} rows")
        
        return chengshen_features
    
    def _generate_future_dates(self, base_date, days_ahead):
        """
        Generate a list of future dates.
        
        Args:
            base_date (datetime): Base date to start from.
            days_ahead (int): Number of days to generate ahead.
            
        Returns:
            list: List of future dates.
        """
        future_dates = []
        current_date = base_date
        
        # Get period from config
        period = self.config['period']
        
        # Generate dates based on period
        if period == '1D':
            # Daily data
            for i in range(days_ahead):
                current_date = current_date + timedelta(days=1)
                # Skip weekends if trading data
                if current_date.weekday() < 5:  # Monday to Friday
                    future_dates.append(current_date)
        elif period == '1H':
            # Hourly data
            trading_hours = range(9, 17)  # 9 AM to 4 PM
            for i in range(days_ahead):
                for hour in trading_hours:
                    current_datetime = base_date.replace(hour=hour) + timedelta(days=i)
                    if current_datetime.weekday() < 5:  # Monday to Friday
                        future_dates.append(current_datetime)
        else:
            # Default to daily
            for i in range(days_ahead):
                current_date = current_date + timedelta(days=1)
                if current_date.weekday() < 5:  # Monday to Friday
                    future_dates.append(current_date)
        
        return future_dates 