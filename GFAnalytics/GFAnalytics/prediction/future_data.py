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
import os

from GFAnalytics.utils.time_utils import ensure_hk_timezone
from GFAnalytics.data.bazi_data import BaziDataGenerator
from GFAnalytics.features.bazi_features import BaziFeatureTransformer
from GFAnalytics.features.chengshen import ChengShenTransformer
from GFAnalytics.utils.encoding_utils import process_encode_data


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
        
    def generate(self, base_date=None, label_encoders=None):
        """
        Generate future data for prediction.
        
        Args:
            base_date (datetime, optional): Base date for prediction. 
                                           If None, uses current date.
            label_encoders (dict, optional): Dictionary of label encoders to use for encoding.
                                           If None, new encoders will be created.
        
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
            'time': future_dates,
            'date': future_dates,
            'stock_code': self.config['stock']['code']
        })
        
        # Generate Bazi data for future dates
        future_bazi_data = self._generate_bazi_data(future_dates)
        
        # Merge with future data
        if 'time' in future_bazi_data.columns:
            future_data = pd.merge(future_data, future_bazi_data, on='time', how='left')
        else:
            future_data = pd.merge(future_data, future_bazi_data, on='date', how='left')
        
        # Transform Bazi pillars to features if transformer is available
        if self.bazi_transformer:
            try:
                future_data = self.bazi_transformer.transform(future_data)
                self.logger.info("Applied Bazi feature transformation")
            except Exception as e:
                self.logger.error(f"Failed to apply Bazi transformation: {str(e)}")
        
        # Transform to ChengShen attributes if transformer is available
        if self.chengshen_transformer:
            try:
                future_data = self.chengshen_transformer.transform(future_data)
                self.logger.info("Applied ChengShen transformation")
            except Exception as e:
                self.logger.error(f"Failed to apply ChengShen transformation: {str(e)}")
        
        # Add stock launch day Bazi if available
        if 'stock' in self.config and 'listing_date' in self.config['stock']:
            try:
                listing_date_str = self.config['stock']['listing_date']
                listing_date = datetime.strptime(listing_date_str, '%Y-%m-%d')
                listing_date = ensure_hk_timezone(listing_date)
                
                # Generate Bazi data for listing date
                listing_bazi = self.bazi_generator._generate_base_pillars(listing_date)
                
                # Add listing Bazi to each row
                for col, value in listing_bazi.items():
                    future_data[f'base_{col}'] = value
                    
                self.logger.info(f"Added listing date Bazi data from {listing_date_str}")
            except Exception as e:
                self.logger.error(f"Failed to add listing date Bazi data: {str(e)}")
        
        # Apply encoding to categorical features
        self.logger.info("Encoding categorical features for prediction")
        try:
            # If label_encoders provided, use them, otherwise create new ones
            encoded_data, new_encoders = process_encode_data(future_data, label_encoders=label_encoders)
            
            # If new encoders were created and we didn't have any before, store them
            if label_encoders is None and new_encoders:
                self.logger.info(f"Created {len(new_encoders)} new label encoders for categorical features")
                label_encoders = new_encoders
                
                # Save encoders for future use if directory exists
                models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
                if os.path.exists(models_dir):
                    import joblib
                    encoders_path = os.path.join(models_dir, 'future_data_encoders.pkl')
                    joblib.dump(label_encoders, encoders_path)
                    self.logger.info(f"Saved label encoders to {encoders_path}")
            
            self.logger.info(f"Generated future data with {len(encoded_data)} rows")
            return encoded_data
            
        except Exception as e:
            self.logger.error(f"Failed to encode categorical features: {str(e)}")
            self.logger.warning("Returning unencoded data, which may cause prediction issues")
            return future_data
    
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
        
    def _generate_bazi_data(self, future_dates):
        """
        Generate Bazi data for a list of future dates.
        
        Args:
            future_dates (list): List of future dates.
            
        Returns:
            pandas.DataFrame: Bazi data for the future dates.
        """
        try:
            # Create a dataframe with the dates
            date_df = pd.DataFrame({'time': future_dates})
            
            # Generate Bazi data
            bazi_data = self.bazi_generator.generate(date_df)
            
            self.logger.info(f"Generated Bazi data for {len(future_dates)} future dates")
            return bazi_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate Bazi data: {str(e)}")
            
            # Create an empty DataFrame with the same columns as would be expected
            empty_df = pd.DataFrame({'time': future_dates})
            
            # Add empty columns for expected Bazi data
            bazi_columns = [
                'current_year_pillar', 'current_month_pillar', 'current_day_pillar', 'current_hour_pillar',
                'current_year_pillar_minus', 'current_month_pillar_minus', 'current_day_pillar_minus', 'current_hour_pillar_minus',
                'current_wuxi_hour', 'current_wuxi_day', 'current_wuxi_month', 'current_wuxi_year'
            ]
            
            for col in bazi_columns:
                empty_df[col] = ''
                
            return empty_df 