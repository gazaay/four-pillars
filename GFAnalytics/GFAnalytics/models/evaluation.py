#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Model Evaluation Module

This module handles the evaluation of trained models.
It calculates various metrics to assess model performance.
"""

import pandas as pd
import numpy as np
import logging
from sklearn.metrics import (
    mean_squared_error, 
    r2_score, 
    median_absolute_error,
    mean_absolute_error,
    explained_variance_score
)
import matplotlib.pyplot as plt
import seaborn as sns

# Import data utilities
from GFAnalytics.utils.data_utils import prepare_feature_data, get_feature_importance as get_feature_importance_util
# Import encoding utilities
from GFAnalytics.utils.encoding_utils import process_encode_data


class ModelEvaluator:
    """
    Handles the evaluation of trained models.
    
    This class calculates various metrics to assess model performance,
    including MSE, RMSE, R2 score, and MedAE.
    """
    
    def __init__(self, config):
        """
        Initialize the ModelEvaluator.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger('GFAnalytics.ModelEvaluator')
        
        # Get evaluation metrics from config
        self.metrics = config['model']['evaluation']['metrics']
    
    def evaluate(self, model, data):
        """
        Evaluate the model performance.
        
        Args:
            model: Trained machine learning model.
            data (pandas.DataFrame): Data used for training and testing.
            
        Returns:
            dict: Evaluation results with various metrics.
        """
        self.logger.info("Evaluating model performance")
        
        # Log data columns for debugging
        self.logger.info("\nColumns in evaluation data:")
        for col in data.columns:
            self.logger.info(f"- {col}")
        
        # Create a copy to avoid modifying the original
        eval_data = data.copy()
        
        # First, encode the data just like in training
        self.logger.info("Encoding categorical features for evaluation")
        try:
            # Use existing encoders from the model if available
            encoded_data, _ = process_encode_data(
                eval_data, 
                label_encoders=model.label_encoders if hasattr(model, 'label_encoders') else None
            )
            self.logger.info("Data encoded successfully for evaluation")
        except Exception as e:
            self.logger.warning(f"Error encoding data: {e}. Continuing with original data.")
            encoded_data = eval_data
            
        # Use the shared data preparation utility to get test data
        self.logger.info("Preparing features using the standardized utility")
        X_test, y_test = prepare_feature_data(encoded_data, is_training=True, config=self.config)
        
        self.logger.info(f"Prepared evaluation data with {X_test.shape[1]} features and {len(y_test)} samples")
        
        # Ensure we have the right features if model has feature_names
        if hasattr(model, 'feature_names') and model.feature_names:
            missing_features = set(model.feature_names) - set(X_test.columns)
            extra_features = set(X_test.columns) - set(model.feature_names)
            
            if missing_features:
                self.logger.warning(f"Missing features in evaluation data: {missing_features}")
                # Add missing features with zeros
                for feature in missing_features:
                    X_test[feature] = 0
            
            if extra_features:
                self.logger.warning(f"Extra features in evaluation data: {extra_features}")
                # Keep only the features used in training
                X_test = X_test[model.feature_names]
        
        # Make predictions on test data
        y_pred = model.predict(X_test)  # Use the prepared X_test
        
        # Calculate metrics
        evaluation_results = self._calculate_metrics(y_test, y_pred)
        
        # Calculate feature importance if enabled
        if self.config['model']['evaluation']['feature_importance']:
            feature_importance = self._calculate_feature_importance(model)
            evaluation_results['feature_importance'] = feature_importance
        
        # Calculate correlation heatmap if enabled
        if self.config['model']['evaluation']['correlation_heatmap']:
            correlation_data = self._calculate_correlation(X_test, y_test)
            evaluation_results['correlation_data'] = correlation_data
        
        self.logger.info(f"Model evaluation completed with R2 score: {evaluation_results.get('R2', 'N/A')}")
        
        return evaluation_results
    
    def _calculate_metrics(self, y_true, y_pred):
        """
        Calculate evaluation metrics.
        
        Args:
            y_true (array-like): True target values.
            y_pred (array-like): Predicted target values.
            
        Returns:
            dict: Dictionary of calculated metrics.
        """
        results = {}
        
        # Calculate each metric specified in config
        for metric in self.metrics:
            if metric == 'MSE':
                results['MSE'] = mean_squared_error(y_true, y_pred)
            elif metric == 'RMSE':
                results['RMSE'] = np.sqrt(mean_squared_error(y_true, y_pred))
            elif metric == 'R2':
                results['R2'] = r2_score(y_true, y_pred)
            elif metric == 'MedAE':
                results['MedAE'] = median_absolute_error(y_true, y_pred)
            elif metric == 'MAE':
                results['MAE'] = mean_absolute_error(y_true, y_pred)
            elif metric == 'EVS':
                results['EVS'] = explained_variance_score(y_true, y_pred)
        
        return results
    
    def _calculate_feature_importance(self, model):
        """
        Calculate feature importance.
        
        Args:
            model: Trained machine learning model.
            
        Returns:
            pandas.DataFrame: Feature importance scores.
        """
        # Use the shared feature importance utility
        return get_feature_importance_util(model)
    
    def _calculate_correlation(self, X, y):
        """
        Calculate correlation between features and target.
        
        Args:
            X (pandas.DataFrame): Feature data.
            y (array-like): Target data.
            
        Returns:
            pandas.DataFrame: Correlation matrix.
        """
        # Combine features and target
        data = X.copy()
        data['target'] = y
        
        # Calculate correlation matrix
        correlation_matrix = data.corr()
        
        return correlation_matrix 