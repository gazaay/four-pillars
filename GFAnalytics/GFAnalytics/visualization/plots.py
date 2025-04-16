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

# Import data utilities for consistency
from GFAnalytics.utils.data_utils import prepare_feature_data, get_feature_importance
from GFAnalytics.utils.encoding_utils import process_encode_data, decode_prediction_data


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
            
        # Store created figures for later display
        self.figures = {
            'prediction': None,
            'feature_importance': None,
            'correlation_heatmap': None,
            'bazi_predictions': None
        }
    
    def plot_prediction(self, stock_data, predictions, show=False):
        """
        Plot stock price predictions.
        
        Args:
            stock_data (pandas.DataFrame): Historical stock data.
            predictions (pandas.DataFrame): Predicted stock prices.
            show (bool): Whether to display the plot immediately.
            
        Returns:
            matplotlib.figure.Figure: The generated plot.
        """
        self.logger.info("Plotting predictions")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Ensure we have proper date columns
        stock_date_col = self._get_date_column(stock_data)
        pred_date_col = self._get_date_column(predictions)
        
        if not stock_date_col or not pred_date_col:
            self.logger.error("Cannot plot predictions: date columns not found")
            return None
        
        # Determine close price column
        close_col = self._get_close_column(stock_data)
        if not close_col:
            self.logger.warning("Close price column not found, using first numeric column")
            numeric_cols = stock_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                close_col = numeric_cols[0]
            else:
                self.logger.error("No numeric columns found in stock data")
                return None
        
        # Plot historical data
        ax.plot(stock_data[stock_date_col], stock_data[close_col], 
                label='Historical Close Price', color='blue', linewidth=1.5)
        
        # Determine prediction column
        pred_col = 'predicted_value'
        if pred_col not in predictions.columns:
            # Try to find any prediction-like column
            for col in predictions.columns:
                if 'predict' in col.lower():
                    pred_col = col
                    break
            else:
                self.logger.error("Prediction column not found")
                return None
        
        # Plot predictions
        ax.plot(predictions[pred_date_col], predictions[pred_col], 
                label='Predicted Price', color='red', linewidth=1.5, marker='o', markersize=4)
        
        # Plot confidence intervals if available
        lower_col = self._find_column(predictions, ['predicted_lower', 'lower_bound', 'lower'])
        upper_col = self._find_column(predictions, ['predicted_upper', 'upper_bound', 'upper'])
        
        if lower_col and upper_col:
            ax.fill_between(
                predictions[pred_date_col],
                predictions[lower_col],
                predictions[upper_col],
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
            
        # Store the figure
        self.figures['prediction'] = fig
        
        # Show the plot if requested
        if show:
            plt.show()
        
        return fig
    
    def plot_feature_importance(self, model, training_data, show=False):
        """
        Plot feature importance.
        
        Args:
            model: Trained machine learning model.
            training_data (pandas.DataFrame): Training data.
            show (bool): Whether to display the plot immediately.
            
        Returns:
            matplotlib.figure.Figure: The generated plot.
        """
        self.logger.info("Plotting feature importance")
        
        # Use the shared get_feature_importance utility
        feature_importance_df = get_feature_importance(model)
        
        if feature_importance_df is None:
            self.logger.error("Could not get feature importance")
            return None
        
        # Take top 30 features for better visualization
        feature_importance = feature_importance_df.head(30)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot feature importance
        sns.barplot(x='importance', y='feature', data=feature_importance, ax=ax)
        
        # Set labels and title
        ax.set_xlabel('Importance')
        ax.set_ylabel('Feature')
        ax.set_title('Feature Importance (Top 30 Features)')
        
        # Add grid
        ax.grid(True, axis='x', alpha=0.3)
        
        # Save plot if enabled
        if self.save_plots:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.plots_dir}/feature_importance_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Feature importance plot saved to {filename}")
            
        # Store the figure
        self.figures['feature_importance'] = fig
        
        # Show the plot if requested
        if show:
            plt.show()
        
        return fig
    
    def plot_correlation_heatmap(self, training_data, show=False):
        """
        Plot correlation heatmap.
        
        Args:
            training_data (pandas.DataFrame): Training data DataFrame.
            show (bool): Whether to display the plot immediately.
            
        Returns:
            matplotlib.figure.Figure: The generated plot.
        """
        self.logger.info("Plotting correlation heatmap")
        
        # Process data to get features
        try:
            X, y = prepare_feature_data(training_data, is_training=True)
            
            if X is None or y is None:
                self.logger.error("Could not prepare data for correlation heatmap")
                return None
                
            # Select a reasonable number of features to avoid overcrowding
            # Focus on the most important features if we have too many
            if X.shape[1] > 20:
                try:
                    if 'model' in locals() and hasattr(model, 'feature_names') and model.feature_names:
                        # Use feature importance to select top features
                        feature_importance = get_feature_importance(model)
                        top_features = feature_importance.head(20)['feature'].tolist()
                        X = X[top_features]
                    else:
                        # Just take the first 20 columns
                        X = X.iloc[:, :20]
                except:
                    # Just take the first 20 columns if there's an error
                    X = X.iloc[:, :20]
            
            # Combine features and target
            data = X.copy()
            data['target'] = y
            
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
            
            # Store the figure
            self.figures['correlation_heatmap'] = fig
            
            # Show the plot if requested
            if show:
                plt.show()
            
            return fig
        except Exception as e:
            self.logger.error(f"Error creating correlation heatmap: {str(e)}")
            return None
    
    def plot_bazi_predictions(self, predictions, encoders=None, show=False):
        """
        Plot predictions grouped by Bazi elements to visualize their impact.
        
        Args:
            predictions (pandas.DataFrame): Prediction data with encoded Bazi elements.
            encoders (dict, optional): Dictionary of label encoders for decoding.
            show (bool): Whether to display the plot immediately.
            
        Returns:
            matplotlib.figure.Figure: The generated plot.
        """
        self.logger.info("Plotting predictions by Bazi elements")
        
        # Make a copy to avoid modifying original data
        pred_data = predictions.copy()
        
        # Check if we need to decode Bazi columns
        bazi_cols = self._find_bazi_columns(pred_data)
        if not bazi_cols:
            self.logger.warning("No Bazi columns found in prediction data")
            return None
            
        # Decode Bazi columns if encoders are available
        if encoders:
            for col in bazi_cols:
                if col in encoders:
                    try:
                        # Get encoded column (with or without 'encoded_' prefix)
                        encoded_col = col
                        if not encoded_col.startswith('encoded_') and f'encoded_{col}' in pred_data.columns:
                            encoded_col = f'encoded_{col}'
                            
                        # Decode the column
                        pred_data[f'decoded_{col}'] = decode_prediction_data(
                            pred_data[encoded_col].values, encoders[col]
                        )
                    except Exception as e:
                        self.logger.warning(f"Error decoding column {col}: {str(e)}")
        
        # Find the target column
        target_col = self._find_column(pred_data, ['predicted_value', 'prediction', 'target'])
        if not target_col:
            self.logger.error("No prediction/target column found")
            return None
            
        # Create a figure with subplots for each Bazi element
        num_elements = len(bazi_cols)
        fig, axes = plt.subplots(figsize=(15, 5 * num_elements), 
                                 nrows=num_elements, ncols=1, 
                                 sharex=True)
        
        # Ensure axes is always a list even with one subplot
        if num_elements == 1:
            axes = [axes]
        
        # Plot predictions grouped by each Bazi element
        for i, col in enumerate(bazi_cols):
            ax = axes[i]
            
            # Determine which column to use for grouping
            group_col = col
            if f'decoded_{col}' in pred_data.columns:
                group_col = f'decoded_{col}'
            
            # Group by the Bazi element and calculate mean prediction
            if pd.api.types.is_numeric_dtype(pred_data[group_col]):
                # For numeric columns, bin them into intervals
                pred_data[f'{group_col}_bin'] = pd.cut(pred_data[group_col], bins=5)
                group_col = f'{group_col}_bin'
            
            try:
                # Group and plot
                grouped = pred_data.groupby(group_col)[target_col].mean().reset_index()
                sns.barplot(x=group_col, y=target_col, data=grouped, ax=ax)
                
                # Set title and labels
                ax.set_title(f'Average Prediction by {col}')
                ax.set_xlabel(col)
                ax.set_ylabel('Average Prediction')
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                ax.grid(axis='y', alpha=0.3)
            except Exception as e:
                self.logger.warning(f"Error plotting for column {col}: {str(e)}")
                ax.text(0.5, 0.5, f"Error plotting: {str(e)}", 
                      horizontalalignment='center', verticalalignment='center',
                      transform=ax.transAxes)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save plot if enabled
        if self.save_plots:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.plots_dir}/bazi_predictions_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"Bazi predictions plot saved to {filename}")
            
        # Store the figure
        self.figures['bazi_predictions'] = fig
        
        # Show the plot if requested
        if show:
            plt.show()
        
        return fig
    
    def display_all_plots(self):
        """
        Display all generated plots.
        
        Returns:
            bool: True if at least one plot was displayed, False otherwise.
        """
        self.logger.info("Displaying all plots")
        
        # Check if we have any plots to display
        if not any(self.figures.values()):
            self.logger.warning("No plots have been generated yet")
            return False
        
        # Display each plot
        for plot_name, fig in self.figures.items():
            if fig is not None:
                plt.figure(fig.number)
                self.logger.info(f"Displaying {plot_name} plot")
        
        # Show all plots
        plt.show()
        return True
    
    def _get_date_column(self, df):
        """Find the date column in a DataFrame."""
        # Look for common date column names
        date_columns = ['date', 'time', 'timestamp', 'datetime']
        for col in date_columns:
            if col in df.columns:
                return col
                
        # Look for datetime-like columns
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col
                
        return None
    
    def _get_close_column(self, df):
        """Find the close price column in a DataFrame."""
        # Look for common close price column names
        close_columns = ['close', 'Close', 'close_price', 'Close_price']
        for col in close_columns:
            if col in df.columns:
                return col
        return None
    
    def _find_column(self, df, possible_names):
        """Find a column in a DataFrame from a list of possible names."""
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    def _find_bazi_columns(self, df):
        """Find Bazi-related columns in the DataFrame."""
        bazi_keywords = ['gan', 'zhi', 'wuxi', 'pillar', 'bazi']
        bazi_cols = []
        
        for col in df.columns:
            # Check if any keyword is in the column name
            if any(keyword in col.lower() for keyword in bazi_keywords):
                bazi_cols.append(col)
                
        return bazi_cols 