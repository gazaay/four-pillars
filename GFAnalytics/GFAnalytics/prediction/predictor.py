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
from datetime import datetime, timedelta

from GFAnalytics.utils.time_utils import ensure_hk_timezone
from GFAnalytics.utils.csv_utils import logdf
from GFAnalytics.utils.data_utils import prepare_feature_data


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
        
        # Preserve time/date information before feature preparation
        if 'date' in prediction_data.columns:
            date_info = prediction_data['date'].copy()
        elif 'time' in prediction_data.columns:
            date_info = prediction_data['time'].copy()
        else:
            # Create a default date range if no date column exists
            date_info = pd.date_range(start=datetime.now(), periods=len(prediction_data), freq='D')
        
        # Log the raw future data
        logdf(prediction_data, 'predictor_raw_future_data')
        
        # Extract features for prediction using the shared utility
        X_pred, _ = prepare_feature_data(prediction_data, is_training=False, config=self.config)
        
        # Log the derived feature columns for reference
        feature_cols = self._get_feature_columns()
        feature_cols_df = pd.DataFrame({'expected_feature': feature_cols})
        logdf(feature_cols_df, 'predictor_expected_features')
        
        # Ensure all required features from the model are present
        if hasattr(model, 'feature_names') and model.feature_names:
            missing_features = [col for col in model.feature_names if col not in X_pred.columns]
            if missing_features:
                self.logger.warning(f"Missing features for prediction: {missing_features}")
                # Log the missing features
                missing_features_df = pd.DataFrame({'missing_features': missing_features})
                logdf(missing_features_df, 'predictor_missing_features')
                
                # Add missing features with default values
                for feature in missing_features:
                    X_pred[feature] = 0  # Default value
            
            # Ensure we use only the features the model was trained with AND in the same order
            extra_features = [col for col in X_pred.columns if col not in model.feature_names]
            if extra_features:
                self.logger.info(f"Removing {len(extra_features)} extra features not used in training")
            
            # Reorder columns to match the exact order from training
            X_pred = X_pred[model.feature_names]
            self.logger.info(f"Reordered features to match training order: {len(model.feature_names)} features")
        
        # Log the prepared features
        logdf(X_pred, 'predictor_prepared_features')
        
        # Generate predictions
        try:
            y_pred = model.predict(X_pred)
            
            # Create prediction dataframe using preserved date information
            predictions = pd.DataFrame({
                'date': date_info,
                'predicted_value': y_pred
            })
            
            # Log the predictions
            logdf(predictions, 'predictor_predictions')
            
            # Print out all predicted values
            self.logger.info("Predicted values:")
            for idx, row in predictions.iterrows():
                self.logger.info(f"Date: {row['date']}, Predicted: {row['predicted_value']:.2f}")
            
            # Add confidence intervals if available
            if hasattr(model, 'predict_with_confidence'):
                y_pred_lower, y_pred_upper = model.predict_with_confidence(X_pred)
                predictions['predicted_lower'] = y_pred_lower
                predictions['predicted_upper'] = y_pred_upper
                
                # Log the predictions with confidence intervals
                logdf(predictions, 'predictor_predictions_with_confidence')
            
            self.logger.info(f"Generated {len(predictions)} predictions")
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error generating predictions: {str(e)}")
            # Log the prediction data that caused the error
            logdf(prediction_data, 'predictor_error_data')
            raise

    def _get_feature_columns(self):
        """
        Get feature columns for prediction from config.
        
        Returns:
            list: List of feature column names.
        """
        # This function is kept for logging purposes, but its output is no longer
        # directly used for feature selection as we now use prepare_feature_data()
        
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
        
        # Log the feature columns we're expecting from the config
        feature_cols_df = pd.DataFrame({'feature_column': feature_cols})
        logdf(feature_cols_df, 'predictor_derived_feature_columns')
        
        return feature_cols 