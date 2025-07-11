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
from GFAnalytics.utils.csv_utils import logdf
from GFAnalytics.utils.data_utils import prepare_feature_data


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
            base_date = ensure_hk_timezone(datetime(2025, 1, 1))
        else:
            base_date = ensure_hk_timezone(base_date)
        
        # Get prediction days ahead from config
        days_ahead = self.config['date_range']['prediction']['days_ahead']
        
        # Generate future dates
        future_dates = self._generate_future_dates(base_date, days_ahead)
        
        # Log the generated future dates
        future_dates_df = pd.DataFrame({'future_dates': future_dates})
        logdf(future_dates_df, 'future_generator_dates')
        
        # Create empty dataframe for future data
        future_data = pd.DataFrame({
            'time': future_dates,
            'date': future_dates,
            'stock_code': self.config['stock']['code']
        })
        
        # Log the initial future data
        logdf(future_data, 'future_generator_initial_data')
        
        # Generate Bazi data for future dates
        future_bazi_data = self._generate_bazi_data(future_dates)
        
        # Log the Bazi data
        logdf(future_bazi_data, 'future_generator_bazi_data')
        
        # Merge with future data
        if 'time' in future_bazi_data.columns:
            future_data = pd.merge(future_data, future_bazi_data, on='time', how='left')
        else:
            future_data = pd.merge(future_data, future_bazi_data, on='date', how='left')
        
        # Log the merged data
        logdf(future_data, 'future_generator_merged_data')
        
        # Transform Bazi pillars to features if transformer is available
        if self.bazi_transformer:
            try:
                future_data = self.bazi_transformer.transform(future_data)
                self.logger.info("Applied Bazi feature transformation")
                
                # Log the data after Bazi transformation
                logdf(future_data, 'future_generator_bazi_transformed_data')
            except Exception as e:
                self.logger.error(f"Failed to apply Bazi transformation: {str(e)}")
                # Log the data that caused the error
                logdf(future_data, 'future_generator_bazi_transform_error_data')
        
        # Transform to ChengShen attributes if transformer is available
        if self.chengshen_transformer:
            try:
                future_data = self.chengshen_transformer.transform(future_data)
                self.logger.info("Applied ChengShen transformation")
                
                # Log the data after ChengShen transformation
                logdf(future_data, 'future_generator_chengshen_transformed_data')
            except Exception as e:
                self.logger.error(f"Failed to apply ChengShen transformation: {str(e)}")
                # Log the data that caused the error
                logdf(future_data, 'future_generator_chengshen_transform_error_data')
        
        # Add stock launch day Bazi if available
        if 'stock' in self.config and 'listing_date' in self.config['stock']:
            try:
                listing_date_str = self.config['stock']['listing_date']
                listing_date = datetime.strptime(listing_date_str, '%Y-%m-%d %H:%M:%S')
                listing_date = ensure_hk_timezone(listing_date)
                
                # Generate Bazi data for listing date
                listing_bazi = self.bazi_generator._generate_base_pillars(listing_date)
                
                # Add listing Bazi to each row
                for col, value in listing_bazi.items():
                    future_data[f'base_{col}'] = value
                    
                self.logger.info(f"Added listing date Bazi data from {listing_date_str}")
                
                # Log the data after adding listing Bazi
                logdf(future_data, 'future_generator_with_listing_bazi')
            except Exception as e:
                self.logger.error(f"Failed to add listing date Bazi data: {str(e)}")
                # Log the error state
                logdf(future_data, 'future_generator_listing_bazi_error_data')
        
        # Apply encoding to categorical features
        self.logger.info("Encoding categorical features for prediction")
        try:
            # If label_encoders provided, use them, otherwise create new ones
            encoded_data, new_encoders = process_encode_data(future_data, label_encoders=label_encoders)
            
            # Log the encoded data
            logdf(encoded_data, 'future_generator_encoded_data')
            
            # Log the encoders
            if new_encoders:
                encoders_info = pd.DataFrame({
                    'encoder_name': list(new_encoders.keys()),
                    'encoder_classes_count': [len(enc.classes_) for enc in new_encoders.values()]
                })
                logdf(encoders_info, 'future_generator_encoders_info')
            
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
            
            # Add placeholder stock features to match training data BEFORE feature preparation
            # These will be filled with zeros since we don't have actual stock data for future dates
            stock_features = ['Open_x', 'High_x', 'Low_x', 'Close_x', 'Volume_x', 'Dividends_x', 'Stock Splits_x']
            for feature in stock_features:
                if feature not in encoded_data.columns:
                    encoded_data[feature] = 0.0
                    self.logger.debug(f"Added placeholder feature: {feature}")
            
            self.logger.info(f"Added {len([f for f in stock_features if f not in encoded_data.columns])} placeholder stock features to match training")
            
            # Use prepare_feature_data to prepare features in a standardized way
            self.logger.info("Preparing features using the standardized utility")
            X_prepared, _ = prepare_feature_data(encoded_data, is_training=False, config=self.config)
            
            # Log the prepared features
            logdf(X_prepared, 'future_generator_prepared_features')
            
            self.logger.info(f"Generated future data with {len(X_prepared)} rows and {X_prepared.shape[1]} features")
            return X_prepared
            
        except Exception as e:
            self.logger.error(f"Failed to encode or prepare features: {str(e)}")
            self.logger.warning("Returning unencoded data, which may cause prediction issues")
            
            # Log the error state
            logdf(future_data, 'future_generator_encoding_error_data')
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
        
        # Log the generated dates
        dates_info = pd.DataFrame({
            'date': future_dates,
            'weekday': [d.strftime('%A') for d in future_dates]
        })
        logdf(dates_info, 'future_generator_dates_details')
        
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
            
            # Log the input dates
            logdf(date_df, 'future_generator_bazi_input_dates')
            
            # Generate Bazi data
            bazi_data = self.bazi_generator.generate(date_df)
            
            # Log the generated Bazi data
            logdf(bazi_data, 'future_generator_bazi_generated_data')
            
            self.logger.info(f"Generated Bazi data for {len(future_dates)} future dates")
            return bazi_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate Bazi data: {str(e)}")
            
            # Log the error state
            error_info = pd.DataFrame({
                'error': [str(e)],
                'dates_count': [len(future_dates)]
            })
            logdf(error_info, 'future_generator_bazi_error_info')
            
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
                
            # Log the fallback empty data
            logdf(empty_df, 'future_generator_bazi_fallback_data')
                
            return empty_df 