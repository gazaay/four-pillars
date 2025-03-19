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
        
        # Get test data
        X_test = data['X_test']
        y_test = data['y_test']
        
        # Make predictions on test data
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        evaluation_results = self._calculate_metrics(y_test, y_pred)
        
        # Calculate feature importance if enabled
        if self.config['model']['evaluation']['feature_importance']:
            feature_importance = self._calculate_feature_importance(model, data['feature_names'])
            evaluation_results['feature_importance'] = feature_importance
        
        # Calculate correlation heatmap if enabled
        if self.config['model']['evaluation']['correlation_heatmap']:
            correlation_data = self._calculate_correlation(data['X_train'], data['y_train'])
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
    
    def _calculate_feature_importance(self, model, feature_names):
        """
        Calculate feature importance.
        
        Args:
            model: Trained machine learning model.
            feature_names (list): Names of features.
            
        Returns:
            pandas.DataFrame: Feature importance scores.
        """
        # Check if model has feature_importances_ attribute
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            # Create DataFrame with feature names and importance scores
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            })
            
            # Sort by importance
            feature_importance = feature_importance.sort_values('importance', ascending=False)
            
            return feature_importance
        else:
            self.logger.warning("Model does not have feature_importances_ attribute")
            return None
    
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