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
from GFAnalytics.utils.translation_service import TranslationService


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
    
    def plot_prediction(self, stock_data, predictions, show=False, model=None):
        """
        Plot stock price predictions with both full view and zoomed view.
        
        Args:
            stock_data (pandas.DataFrame): Historical stock data.
            predictions (pandas.DataFrame): Predicted stock prices.
            show (bool): Whether to display the plot immediately.
            model: The trained model (optional, used to get training metadata).
            
        Returns:
            matplotlib.figure.Figure: The generated plot.
        """
        self.logger.info("Plotting predictions")
        
        # Import date formatting utilities
        from matplotlib.dates import DateFormatter, DayLocator, MonthLocator, WeekdayLocator
        import matplotlib.dates as mdates
        
        # Create figure with 2 subplots (full view and zoomed view)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
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
        
        # Generate base title with training information if available
        base_title = f"Stock Price Prediction for {self.config['stock']['code']}"
        training_info = ""
        
        if model and hasattr(model, 'training_metadata') and model.training_metadata:
            metadata = model.training_metadata
            start_date = metadata.get('training_start_date')
            end_date = metadata.get('training_end_date')
            if start_date and end_date:
                training_info = f"\n(Model trained on data: {start_date} to {end_date})"
        
    # Plot confidence intervals function
    def plot_confidence_intervals(ax, predictions, pred_date_col):
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
        
        # Function to format axes with better date formatting and dotted grid
        def format_axis(ax, is_zoomed=False):
            # Set date formatters
            if is_zoomed:
                # For zoomed view: show every day or every few days
                ax.xaxis.set_major_locator(DayLocator(interval=7))  # Major ticks every week
                ax.xaxis.set_minor_locator(DayLocator(interval=1))  # Minor ticks every day
                ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))  # Month-Day format for zoomed view
            else:
                # For full view: show months more clearly
                ax.xaxis.set_major_locator(MonthLocator(interval=1))  # Major ticks every month
                ax.xaxis.set_minor_locator(WeekdayLocator(interval=1))   # Minor ticks every week
                ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))  # Year-Month format
            
            # Add dotted grid lines
            ax.grid(True, linestyle=':', linewidth=0.8, alpha=0.7, color='gray')
            ax.grid(True, which='minor', linestyle=':', linewidth=0.4, alpha=0.4, color='lightgray')
            
            # Rotate date labels for better readability
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # ===== SUBPLOT 1: FULL VIEW =====
        # Plot historical data
        ax1.plot(pd.to_datetime(stock_data[stock_date_col]), stock_data[close_col], 
                label='Historical Close Price', color='blue', linewidth=1.5)
        
        # Plot predictions
        ax1.plot(pd.to_datetime(predictions[pred_date_col]), predictions[pred_col], 
                label='Predicted Price', color='red', linewidth=1.5, marker='o', markersize=4)
        
        # Plot confidence intervals
        plot_confidence_intervals(ax1, predictions, pred_date_col)
        
        # Set labels and title for full view
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.set_title(f"{base_title} - Full View{training_info}")
        ax1.legend()
        
        # Format full view axis
        format_axis(ax1, is_zoomed=False)
        
        # ===== SUBPLOT 2: ZOOMED VIEW - REWRITTEN =====
        # Create a focused view showing recent historical data + all predictions
        if len(predictions) > 0:
            # Convert to datetime once
            stock_dates = pd.to_datetime(stock_data[stock_date_col])
            pred_dates = pd.to_datetime(predictions[pred_date_col])
            
            # Get prediction date range
            first_pred_date = pred_dates.iloc[0]
            last_pred_date = pred_dates.iloc[-1]
            
            # Define zoom window: show last 30 days of historical data + all predictions
            zoom_start = first_pred_date - pd.Timedelta(days=30)
            zoom_end = last_pred_date + pd.Timedelta(days=5)  # Small padding
            
            self.logger.info(f"Zoomed view: {zoom_start.strftime('%Y-%m-%d')} to {zoom_end.strftime('%Y-%m-%d')}")
            
            # Filter historical data for the zoom period
            hist_mask = (stock_dates >= zoom_start) & (stock_dates <= first_pred_date)
            hist_subset = stock_data[hist_mask].copy()
            hist_dates_subset = stock_dates[hist_mask]
            
            self.logger.info(f"Zoomed view data: {len(hist_subset)} historical points, {len(predictions)} predictions")
        
            # Plot historical data
            if len(hist_subset) > 0:
                ax2.plot(hist_dates_subset, hist_subset[close_col], 
                        label='Historical Close Price', color='blue', linewidth=2, 
                        marker='o', markersize=3, alpha=0.8)
                self.logger.info("✅ Plotted historical data in zoomed view")
            else:
                self.logger.warning("⚠️ No historical data in zoom window")
        
            # Plot ALL predictions (they are future data)
            ax2.plot(pred_dates, predictions[pred_col], 
                    label='Predicted Price', color='red', linewidth=2, 
                    marker='s', markersize=4, alpha=0.9)
            self.logger.info("✅ Plotted all predictions in zoomed view")
            
            # Plot confidence intervals if available
            plot_confidence_intervals(ax2, predictions, pred_date_col)
        
            # Add vertical line at prediction start
            ax2.axvline(x=first_pred_date, color='green', linestyle='--', linewidth=2, 
                       label='Prediction Start', alpha=0.7)
            
            # Set labels and title
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Price')
            zoomed_title = f"Recent Data + Predictions: {zoom_start.strftime('%Y-%m-%d')} to {zoom_end.strftime('%Y-%m-%d')}"
            if training_info:
                zoomed_title += training_info
            ax2.set_title(zoomed_title)
            ax2.legend()
            
            # Format zoomed view axis with daily ticks
            format_axis(ax2, is_zoomed=True)
            
        else:
            # No predictions available
            self.logger.warning("No predictions available for zoomed view")
            ax2.text(0.5, 0.5, 'No prediction data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
            ax2.set_title("Zoomed View - No Data Available")
        
        # Adjust layout to prevent overlap
        plt.tight_layout()
        
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
        
        # Translate feature names
        feature_importance['feature'] = TranslationService.translate_feature_names(feature_importance['feature'])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot feature importance
        sns.barplot(x='importance', y='feature', data=feature_importance, ax=ax)
        
        # Get translations for labels
        translations = TranslationService.translate_plot_labels()
        
        # Set labels and title
        ax.set_xlabel(translations['Importance'])
        ax.set_ylabel(translations['Feature'])
        ax.set_title(translations['Feature Importance (Top 30 Features)'])
        
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
            # prepare_feature_data returns (X, y) tuple for training
            X, y = prepare_feature_data(training_data, is_training=True, config=self.config)
            
            if X is None or X.empty or y is None:
                self.logger.error("Could not prepare data for correlation heatmap")
                return None
                
            # Select a reasonable number of features to avoid overcrowding
            # Focus on the most important features if we have too many
            if X.shape[1] > 20:
                # Just take the first 20 feature columns
                X = X.iloc[:, :20]
            
            # Translate feature names
            X.columns = TranslationService.translate_feature_names(X.columns)
            
            # Combine features and target for correlation analysis
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
            
            # Get translations for labels
            translations = TranslationService.translate_plot_labels()
            
            # Set title
            ax.set_title(translations['Feature Correlation Heatmap'])
            
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