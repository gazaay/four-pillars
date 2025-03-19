#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Predictor Module

This module handles predictions using the trained model.
It takes future data and generates predictions for stock prices.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime

from GFAnalytics.utils.time_utils import ensure_hk_timezone


class Predictor:
    """
    Handles predictions using the trained model.
    
    This class takes future data and generates predictions for stock prices
    using the trained machine learning model.
    """
    
    def __init__(self, config):
        """
        Initialize the Predictor.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger('GFAnalytics.Predictor')
    
    def predict(self, model, future_data):
        """
        Generate predictions using the trained model.
        
        Args:
            model: Trained machine learning model.
            future_data (pandas.DataFrame): Future data prepared for prediction.
            
        Returns:
            pandas.DataFrame: Predictions with dates and predicted values.
        """
        self.logger.info("Generating predictions")
        
        # Make a copy of future data to avoid modifying the original
        prediction_data = future_data.copy()
        
        # Extract features for prediction
        X_pred = self._prepare_features(prediction_data)
        
        # Generate predictions
        try:
            y_pred = model.predict(X_pred)
            
            # Create prediction dataframe
            predictions = pd.DataFrame({
                'date': prediction_data['date'],
                'predicted_value': y_pred
            })
            
            # Add confidence intervals if available
            if hasattr(model, 'predict_with_confidence'):
                y_pred_lower, y_pred_upper = model.predict_with_confidence(X_pred)
                predictions['predicted_lower'] = y_pred_lower
                predictions['predicted_upper'] = y_pred_upper
            
            self.logger.info(f"Generated {len(predictions)} predictions")
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error generating predictions: {str(e)}")
            raise
    
    def _prepare_features(self, data):
        """
        Prepare features for prediction.
        
        Args:
            data (pandas.DataFrame): Data to prepare features from.
            
        Returns:
            pandas.DataFrame: Features ready for prediction.
        """
        # Get feature columns from config
        feature_cols = self._get_feature_columns()
        
        # Check if all required features are present
        missing_features = [col for col in feature_cols if col not in data.columns]
        if missing_features:
            self.logger.warning(f"Missing features for prediction: {missing_features}")
            
            # Try to handle missing features
            for feature in missing_features:
                data[feature] = 0  # Default value
        
        # Select only the required features
        X = data[feature_cols].copy()
        
        return X
    
    def _get_feature_columns(self):
        """
        Get feature columns for prediction from config.
        
        Returns:
            list: List of feature column names.
        """
        # This should be aligned with the features used during training
        # For now, we'll use a simple approach
        
        feature_cols = []
        
        # Add Bazi features if enabled
        if self.config['model']['features']['use_bazi']:
            feature_cols.extend([
                'year_stem_encoded', 'year_branch_encoded',
                'month_stem_encoded', 'month_branch_encoded',
                'day_stem_encoded', 'day_branch_encoded',
                'hour_stem_encoded', 'hour_branch_encoded'
            ])
        
        # Add ChengShen features if enabled
        if self.config['model']['features']['use_chengshen']:
            feature_cols.extend([
                'year_stem_chengshen', 'year_branch_chengshen',
                'month_stem_chengshen', 'month_branch_chengshen',
                'day_stem_chengshen', 'day_branch_chengshen',
                'hour_stem_chengshen', 'hour_branch_chengshen'
            ])
        
        # Add technical indicators if enabled
        if self.config['model']['features']['use_technical_indicators']:
            for indicator in self.config['model']['features']['technical_indicators']:
                feature_cols.append(f'{indicator}_encoded')
        
        return feature_cols 