#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plotting Module

This module handles the visualization of predictions and model evaluation.
It provides functions to plot predictions, feature importance, and correlation heatmaps.
"""

import os
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


class Plotter:
    """
    Handles visualization of predictions and model evaluation.
    
    This class provides functions to plot predictions, feature importance,
    and correlation heatmaps.
    """
    
    def __init__(self, config):
        """
        Initialize the Plotter.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger('GFAnalytics.Plotter')
        
        # Get visualization configuration
        self.save_plots = config['visualization']['save_plots']
        self.plots_dir = config['visualization']['plots_dir']
        
        # Create plots directory if it doesn't exist
        if self.save_plots:
            os.makedirs(self.plots_dir, exist_ok=True)
    
    def plot_prediction(self, stock_data, predictions):
        """
        Plot stock price predictions.
        
        Args:
            stock_data (pandas.DataFrame): Historical stock data.
            predictions (pandas.DataFrame): Predicted stock prices.
            
        Returns:
            matplotlib.figure.Figure: The generated plot.
        """
        self.logger.info("Plotting predictions")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot historical data
        if 'close' in stock_data.columns:
            ax.plot(stock_data['date'], stock_data['close'], label='Historical Close Price', color='blue')
        
        # Plot predictions
        ax.plot(predictions['date'], predictions['predicted_value'], label='Predicted Price', color='red')
        
        # Plot confidence intervals if available
        if 'predicted_lower' in predictions.columns and 'predicted_upper' in predictions.columns:
            ax.fill_between(
                predictions['date'],
                predictions['predicted_lower'],
                predictions['predicted_upper'],
                color='red',
                alpha=0.2,
                label='Prediction Interval'
            )
        
        # Set labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title(f"Stock Price Prediction for {self.config['stock']['code']}")
        
        # Add legend
        ax.legend()
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Save plot if enabled
        if self.save_plots:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.plots_dir}/prediction_{self.config['stock']['code']}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Prediction plot saved to {filename}")
        
        return fig
    
    def plot_feature_importance(self, model, training_data):
        """
        Plot feature importance.
        
        Args:
            model: Trained machine learning model.
            training_data (dict): Training data dictionary with feature names.
            
        Returns:
            matplotlib.figure.Figure: The generated plot.
        """
        self.logger.info("Plotting feature importance")
        
        # Check if model has feature_importances_ attribute
        if not hasattr(model, 'feature_importances_'):
            self.logger.warning("Model does not have feature_importances_ attribute")
            return None
        
        # Get feature names and importance scores
        feature_names = training_data['feature_names']
        importances = model.feature_importances_
        
        # Create DataFrame for plotting
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        })
        
        # Sort by importance
        feature_importance = feature_importance.sort_values('importance', ascending=False)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot feature importance
        sns.barplot(x='importance', y='feature', data=feature_importance, ax=ax)
        
        # Set labels and title
        ax.set_xlabel('Importance')
        ax.set_ylabel('Feature')
        ax.set_title('Feature Importance')
        
        # Add grid
        ax.grid(True, axis='x', alpha=0.3)
        
        # Save plot if enabled
        if self.save_plots:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.plots_dir}/feature_importance_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Feature importance plot saved to {filename}")
        
        return fig
    
    def plot_correlation_heatmap(self, training_data):
        """
        Plot correlation heatmap.
        
        Args:
            training_data (dict): Training data dictionary.
            
        Returns:
            matplotlib.figure.Figure: The generated plot.
        """
        self.logger.info("Plotting correlation heatmap")
        
        # Get training data
        X_train = training_data['X_train']
        y_train = training_data['y_train']
        
        # Combine features and target
        data = X_train.copy()
        data['target'] = y_train
        
        # Calculate correlation matrix
        correlation_matrix = data.corr()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 12))
        
        # Plot heatmap
        sns.heatmap(
            correlation_matrix,
            annot=True,
            cmap='coolwarm',
            fmt='.2f',
            linewidths=0.5,
            ax=ax
        )
        
        # Set title
        ax.set_title('Feature Correlation Heatmap')
        
        # Save plot if enabled
        if self.save_plots:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.plots_dir}/correlation_heatmap_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Correlation heatmap saved to {filename}")
        
        return fig 