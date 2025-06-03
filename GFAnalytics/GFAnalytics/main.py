#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GFAnalytics Framework - Main Module

This module serves as the main entry point for the GFAnalytics framework,
which uses machine learning to predict stock market or indices pricing
based on Bazi (Chinese metaphysics) attributes.
"""

import os
import yaml
import logging
from datetime import datetime
import sys
import argparse
import pandas as pd
import numpy as np
# print(sys.path)

# Import modules from the framework
from GFAnalytics.data.stock_data import StockDataLoader
from GFAnalytics.data.bazi_data import BaziDataGenerator
from GFAnalytics.data.data_storage import BigQueryStorage
from GFAnalytics.features.bazi_features import BaziFeatureTransformer
from GFAnalytics.features.chengshen import ChengShenTransformer
from GFAnalytics.models.random_forest import RandomForestModel
from GFAnalytics.models.model_storage import GoogleDriveStorage
from GFAnalytics.models.evaluation import ModelEvaluator
from GFAnalytics.prediction.future_data import FutureDataGenerator
from GFAnalytics.prediction.predictor import Predictor
from GFAnalytics.visualization.plots import Plotter
from GFAnalytics.utils.time_utils import ensure_hk_timezone
from GFAnalytics.utils.gcp_utils import setup_gcp_credentials
from GFAnalytics.utils.csv_utils import configure as configure_csv_logging, logdf, list_runs, get_run_logs
from GFAnalytics.utils.global_run_id import generate_run_id, get_run_id


class GFAnalytics:
    """
    Main class for the GFAnalytics framework that orchestrates the entire pipeline.
    
    This class provides methods to:
    1. Load stock data from YFinance or other sources
    2. Generate Bazi attributes for the data
    3. Transform Bazi pillars to ChengShen attributes
    4. Train a machine learning model (Random Forest)
    5. Evaluate the model performance
    6. Generate predictions for future data
    7. Visualize the results
    
    All data is stored in BigQuery and the trained model is stored in Google Drive.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the GFAnalytics framework.
        
        Args:
            config_path (str): Path to the configuration file. If None, uses default path.
        """
        # Set default config path if not provided
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Generate a unique run ID for this execution
        self.run_id = generate_run_id()
        self.logger.info(f"Starting new run with ID: {self.run_id}")
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info("GFAnalytics framework initialized")
        
        # Configure DataFrame logging
        configure_csv_logging(config_path)
        
        # Data containers
        self.stock_data = None
        self.bazi_data = None
        self.training_data = None
        self.future_data = None
        self.predictions = None
        self.evaluation_results = None
    
    def _load_config(self, config_path):
        """
        Load configuration from YAML file.
        
        Args:
            config_path (str): Path to the configuration file.
            
        Returns:
            dict: Configuration dictionary.
        """
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            raise Exception(f"Failed to load configuration from {config_path}: {str(e)}")
    
    def _setup_logging(self):
        """Set up logging based on configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'gfanalytics.log')
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=log_file,
            filemode='a'
        )
        
        # Create a console handler
        console = logging.StreamHandler()
        console.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        
        self.logger = logging.getLogger('GFAnalytics')
    
    def _initialize_components(self):
        """Initialize all components of the framework."""
        # Setup GCP credentials
        setup_gcp_credentials(self.config['gcp']['credentials_path'])
        
        # Initialize data components
        self.stock_loader = StockDataLoader(self.config)
        self.bazi_generator = BaziDataGenerator(self.config)
        self.bq_storage = BigQueryStorage(self.config)
        
        # Initialize feature components
        self.bazi_transformer = BaziFeatureTransformer(self.config)
        self.chengshen_transformer = ChengShenTransformer(self.config)
        
        # Initialize model components
        self.model = RandomForestModel(self.config)
        self.model_storage = GoogleDriveStorage(self.config)
        self.evaluator = ModelEvaluator(self.config)
        
        # Initialize prediction components
        self.future_generator = FutureDataGenerator(self.config)
        self.predictor = Predictor(self.config)
        
        # Initialize visualization
        self.plotter = Plotter(self.config)
        
        # Data containers
        self.stock_data = None
        self.bazi_data = None
        self.training_data = None
        self.future_data = None
        self.predictions = None
        self.evaluation_results = None
    
    def run(self, show_plots=False):
        """
        Run the complete GFAnalytics pipeline.
        
        Args:
            show_plots (bool): Whether to display plots during execution.
            
        Returns:
            dict: Results containing evaluation metrics, predictions, and run ID.
        """
        self.logger.info("Starting GFAnalytics pipeline")
        
        # Execute each step of the pipeline
        self.load_data()
        self.create_features()
        self.train_model()
        self.evaluate_model()
        self.predict_future()
        self.visualize_results(show_plots=show_plots)
        
        self.logger.info("GFAnalytics pipeline completed successfully")
        
        return {
            'run_id': self.run_id,
            'evaluation': self.evaluation_results,
            'predictions': self.predictions
        }
    
    def load_data(self):
        """Load stock data and generate Bazi data."""
        self.logger.info("Loading stock data")
        self.stock_data = self.stock_loader.load()
        self.bq_storage.store_stock_data(self.stock_data)
        
        # Log stock data to CSV
        logdf(self.stock_data, 'stock_data')
        
        self.logger.info("Generating Bazi data")
        self.bazi_data = self.bazi_generator.generate(self.stock_data)
        self.bq_storage.store_bazi_data(self.bazi_data)
        
        # Log Bazi data to CSV
        logdf(self.bazi_data, 'bazi_data')
        
        # Log info about loaded data
        self.logger.info(f"Stock data shape: {self.stock_data.shape}")
        self.logger.info(f"Stock data columns: {self.stock_data.columns.tolist()}")
        self.logger.info(f"\nFirst few rows of stock data:\n{self.stock_data.head()}")
        
        self.logger.info(f"Bazi data shape: {self.bazi_data.shape}")
        self.logger.info(f"Bazi data columns: {self.bazi_data.columns.tolist()}")
        self.logger.info(f"\nFirst few rows of Bazi data:\n{self.bazi_data.head()}")
        return self.stock_data, self.bazi_data
    
    def create_features(self):
        """Create features for training by transforming Bazi data to ChengShen."""
        self.logger.info("Creating training features")
        
        # Log data shapes before transformation
        self.logger.info(f"Original Bazi data shape: {self.bazi_data.shape}")
        self.logger.info(f"Original stock data shape: {self.stock_data.shape}")
        
        # Transform Bazi pillars to features
        self.logger.info("Applying Bazi feature transformation...")
        bazi_features = self.bazi_transformer.transform(self.bazi_data)
        self.logger.info(f"Bazi features shape after transformation: {bazi_features.shape}")
        
        # Log intermediate bazi features
        logdf(bazi_features, 'bazi_features')
        
        # Transform to ChengShen attributes
        self.logger.info("Applying ChengShen transformation...")
        chengshen_features = self.chengshen_transformer.transform(bazi_features)
        self.logger.info(f"Features shape after ChengShen transformation: {chengshen_features.shape}")
        
        # Log chengshen features
        logdf(chengshen_features, 'chengshen_features')
        
        # Combine with stock data
        self.logger.info("Combining features with stock data...")
        self.training_data = self.bazi_transformer.combine_with_stock_data(
            chengshen_features, self.stock_data
        )
        self.logger.info(f"Final training data shape: {self.training_data.shape}")
        
        # Log columns in training data
        self.logger.info(f"Training data columns: {self.training_data.columns.tolist()}")
        
        # Check for target column
        if 'target' not in self.training_data.columns:
            self.logger.warning("No 'target' column found in training data!")
            self.logger.info("Creating target column as next day's close price...")
            if 'Close' in self.training_data.columns:
                self.training_data['target'] = self.training_data['Close'].shift(-1)
                self.training_data = self.training_data.dropna(subset=['target'])
                self.logger.info(f"Target column created. New shape: {self.training_data.shape}")
            else:
                self.logger.error("Cannot create target: 'Close' column not found")
        
        # Log final training data
        logdf(self.training_data, 'training_data')
        
        # Store training data
        self.bq_storage.store_training_data(self.training_data)
        self.logger.info("Training data stored in BigQuery")

        return self.training_data
    
    def train_model(self):
        """Train the Random Forest model."""
        self.logger.info("Training model")
        
        # Train the model
        self.model.train(self.training_data)
        
        # Get and log feature importance
        try:
            feature_importance = self.model.get_feature_importance()
            self.logger.info(f"Top 10 important features: {feature_importance.head(10)}")
            
            # Log feature importance to CSV
            logdf(feature_importance, 'feature_importance')
        except Exception as e:
            self.logger.error(f"Failed to get feature importance: {str(e)}")
        
        # Save the model with training date information
        try:
            # Get training dates from config
            training_start_date = self.config['date_range']['training']['start_date']
            training_end_date = self.config['date_range']['training']['end_date']
            
            model_path = self.model_storage.save_model(
                self.model, 
                training_start_date=training_start_date,
                training_end_date=training_end_date
            )
            self.logger.info(f"Model saved to {model_path}")
        except Exception as e:
            self.logger.error(f"Failed to save model: {str(e)}")
            
        return self.model
    
    def evaluate_model(self):
        """Evaluate the trained model."""
        self.logger.info("Evaluating model")
        
        # Evaluate model
        self.evaluation_results = self.evaluator.evaluate(self.model, self.training_data)
        
        # Log evaluation metrics
        metrics_dict = {k: v for k, v in self.evaluation_results.items() 
                        if k not in ['feature_importance', 'correlation_data']}
        metrics_df = pd.DataFrame([metrics_dict])
        logdf(metrics_df, 'evaluation_metrics')
        
        # Log correlation data if available
        if 'correlation_data' in self.evaluation_results:
            correlation_df = self.evaluation_results['correlation_data']
            logdf(correlation_df, 'correlation_matrix')
        
        # Log feature importance if available
        if 'feature_importance' in self.evaluation_results:
            feature_importance_df = self.evaluation_results['feature_importance']
            logdf(feature_importance_df, 'feature_importance_from_eval')
        
        # Print metrics
        self.logger.info("Model evaluation results:")
        for key, value in metrics_dict.items():
            self.logger.info(f"  {key}: {value}")
            
        return self.evaluation_results
    
    def predict_future(self):
        """Predict future data."""
        self.logger.info("Generating predictions for future data")
        
        # Generate future data
        self.future_data = self.future_generator.generate(
            label_encoders=getattr(self.model, 'label_encoders', None)
        )
        
        # Make predictions
        self.predictions = self.predictor.predict(self.model, self.future_data)
        
        # Log the future data used for prediction
        logdf(self.future_data, 'predictor_future_data')
        
        # Log the predictions
        logdf(self.predictions, 'final_predictions')
        
        self.logger.info(f"Made {len(self.predictions)} predictions")
        
        return self.predictions
    
    def visualize_results(self, show_plots=False):
        """Visualize the results with plots."""
        self.logger.info("Visualizing results")
        
        # Make sure we have required data
        if self.stock_data is None or self.predictions is None:
            self.logger.error("Cannot visualize results: missing stock data or predictions")
            return False
            
        # Make sure the model is trained
        if self.model is None:
            self.logger.error("Cannot visualize results: model not trained")
            return False
        
        # Create prediction plot
        try:
            if self.config['visualization']['plot_prediction']:
                self.logger.info("Creating prediction plot...")
                prediction_fig = self.plotter.plot_prediction(
                    self.stock_data, self.predictions, show=show_plots, model=self.model
                )
                self.logger.info("Prediction plot created")
            else:
                prediction_fig = None
        except Exception as e:
            self.logger.error(f"Failed to create prediction plot: {str(e)}")
            prediction_fig = None
            
        # Create feature importance plot
        try:
            if self.config['model']['evaluation']['feature_importance'] and hasattr(self.model, 'get_feature_importance'):
                self.logger.info("Creating feature importance plot...")
                importance_fig = self.plotter.plot_feature_importance(
                    self.model, self.training_data, show=show_plots
                )
                self.logger.info("Feature importance plot created")
            else:
                importance_fig = None
        except Exception as e:
            self.logger.error(f"Failed to create feature importance plot: {str(e)}")
            importance_fig = None
            
        # Create correlation heatmap
        try:
            if self.config['model']['evaluation']['correlation_heatmap']:
                self.logger.info("Creating correlation heatmap...")
                correlation_fig = self.plotter.plot_correlation_heatmap(
                    self.training_data, show=show_plots
                )
                self.logger.info("Correlation heatmap created")
            else:
                correlation_fig = None
        except Exception as e:
            self.logger.error(f"Failed to create correlation heatmap: {str(e)}")
            correlation_fig = None
            
        # Create Bazi predictions plot
        try:
            if hasattr(self.model, 'label_encoders'):
                self.logger.info("Creating Bazi predictions plot...")
                bazi_fig = self.plotter.plot_bazi_predictions(
                    self.predictions, self.model.label_encoders, show=show_plots
                )
                self.logger.info("Bazi predictions plot created")
            else:
                bazi_fig = None
        except Exception as e:
            self.logger.error(f"Failed to create Bazi predictions plot: {str(e)}")
            bazi_fig = None
            
        # If show_plots is False but we want to display them all at once
        if not show_plots and self.config['visualization'].get('display_plots_at_end', True):
            self.display_plots()
            
        self.logger.info("Visualization complete")
        
        return {
            'prediction_plot': prediction_fig,
            'importance_plot': importance_fig,
            'correlation_plot': correlation_fig,
            'bazi_plot': bazi_fig
        }
    
    def display_plots(self):
        """Display all generated plots."""
        if hasattr(self, 'plotter'):
            self.logger.info("Displaying all plots")
            return self.plotter.display_all_plots()
        else:
            self.logger.error("Plotter not initialized")
            return False

    def clean_tables(self):
        """Clean all tables in BigQuery."""
        self.logger.info("Cleaning all tables")
        self.bq_storage.clean_all_tables()
        self.logger.info("All tables cleaned successfully")
    
    def clean_table(self, table_name):
        """Clean specific table in BigQuery."""
        self.logger.info(f"Cleaning table: {table_name}")
        self.bq_storage.clean_table(table_name)
        self.logger.info(f"Table {table_name} cleaned successfully")

    def load_pretrained_model(self, model_path):
        """
        Load a pre-trained model and restore it to the model object.
        
        Args:
            model_path (str): Path to model file or Google Drive ID
        """
        self.logger.info(f"Loading pre-trained model from: {model_path}")
        
        # Load model data using model storage
        model_data = self.model_storage.load_model(model_path)
        
        # Restore the model components
        self.model.model = model_data['model']
        self.model.feature_names = model_data['feature_names']
        self.model.label_encoders = model_data['label_encoders']
        
        # Extract and store training metadata if available
        if 'training_metadata' in model_data:
            self.model.training_metadata = model_data['training_metadata']
            metadata = model_data['training_metadata']
            self.logger.info(f"Model trained on data from {metadata.get('training_start_date', 'Unknown')} to {metadata.get('training_end_date', 'Unknown')}")
        else:
            self.model.training_metadata = None
            self.logger.warning("No training metadata found in model file")
        
        self.logger.info("Pre-trained model loaded successfully")
        self.logger.info(f"Model has {len(self.model.feature_names)} features")
        self.logger.info(f"Model has {len(self.model.label_encoders)} label encoders")
        
        return self.model

    def run_with_pretrained_model(self, model_path, show_plots=False):
        """
        Run pipeline with pre-trained model with future-only plotting.
        
        Args:
            model_path (str): Path to model file or Google Drive ID
            show_plots (bool): Whether to display plots during execution
            
        Returns:
            dict: Results containing predictions and run ID
        """
        self.logger.info("Starting GFAnalytics pipeline with pre-trained model (prediction mode)")
        
        # Load the pre-trained model
        self.load_pretrained_model(model_path)
        
        # Generate future data and predictions (fast)
        self.logger.info("Generating future predictions (skipping all historical data processing)")
        
        try:
            # Generate future data directly
            self.future_data = self.future_generator.generate(
                label_encoders=getattr(self.model, 'label_encoders', None)
            )
            
            # Make predictions
            self.predictions = self.predictor.predict(self.model, self.future_data)
            
            # Log results to CSV only
            logdf(self.future_data, 'predictor_future_data')
            logdf(self.predictions, 'final_predictions')
            
            self.logger.info(f"✅ Successfully made {len(self.predictions)} predictions")
            
            # Create future-only plots
            if show_plots:
                self.create_future_only_plots(show_plots=True)
            
            # Print predictions summary
            self.print_prediction_summary()
            
        except Exception as e:
            self.logger.error(f"❌ Error in prediction generation: {str(e)}")
            raise
        
        self.logger.info("✅ GFAnalytics prediction pipeline completed successfully")
        
        return {
            'run_id': self.run_id,
            'predictions': self.predictions,
            'model_loaded': True,
            'mode': 'prediction_only',
            'plots_created': show_plots
        }

    def create_future_only_plots(self, show_plots=False):
        """
        Create plots focused only on future predictions with enhanced moving average analysis.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        from datetime import datetime, timedelta
        import pandas as pd
        
        self.logger.info("🎨 Creating future-only prediction plots with 21 vs 95 MA analysis")
        
        try:
            # Set up the plotting style
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Create figure with 2x4 grid for 8 plots (added 2 more)
            fig = plt.figure(figsize=(24, 15))  # Increased width for 4 columns
            
            # Generate main title with training information if available
            main_title = '🔮 Future Predictions Analysis with Moving Averages'
            if hasattr(self.model, 'training_metadata') and self.model.training_metadata:
                metadata = self.model.training_metadata
                start_date = metadata.get('training_start_date')
                end_date = metadata.get('training_end_date')
                if start_date and end_date:
                    main_title += f'\n(Model trained on: {start_date} to {end_date})'
            
            fig.suptitle(main_title, fontsize=16, fontweight='bold')
            
            # Create subplots (2x4 grid)
            ax1 = plt.subplot(2, 4, 1)  # Time series
            ax2 = plt.subplot(2, 4, 2)  # Distribution  
            ax3 = plt.subplot(2, 4, 3)  # Trend with MAs
            ax4 = plt.subplot(2, 4, 4)  # Statistics
            ax5 = plt.subplot(2, 4, 5)  # MA comparison
            ax6 = plt.subplot(2, 4, 6)  # MA signals
            ax7 = plt.subplot(2, 4, 7)  # NEW: 90-day view
            ax8 = plt.subplot(2, 4, 8)  # NEW: 21-day view
            
            # Prepare prediction data
            if hasattr(self.predictions, 'columns'):
                # DataFrame format
                pred_values = self.predictions.get('predicted_value', self.predictions.iloc[:, 0])
                dates = None
                if 'date' in self.predictions.columns:
                    dates = pd.to_datetime(self.predictions['date'])
                elif 'time' in self.predictions.columns:
                    dates = pd.to_datetime(self.predictions['time'])
            else:
                # Array format
                pred_values = self.predictions
                dates = None
            
            # Generate date range for x-axis if not available (but log this as it indicates the time column issue)
            if dates is None:
                self.logger.warning("⚠️ No time/date column found in predictions! Using fallback dates from current time.")
                start_date = datetime.now()
                dates = [start_date + timedelta(hours=i) for i in range(len(pred_values))]
            
            # Convert to pandas Series for easier filtering
            dates_series = pd.Series(dates)
            pred_values_series = pd.Series(pred_values)
            current_time = datetime.now()
            
            # Plot 1: Time Series of Predictions
            ax1.plot(dates, pred_values, marker='o', linewidth=2, markersize=4, color='blue', alpha=0.8)
            ax1.set_title('📈 Future Price Predictions Over Time')
            ax1.set_xlabel('Date/Time')
            ax1.set_ylabel('Predicted Price')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.tick_params(axis='x', rotation=45)
            
            # Plot 2: Prediction Distribution
            ax2.hist(pred_values, bins=20, alpha=0.7, color='green', edgecolor='black')
            ax2.axvline(pred_values.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {pred_values.mean():.2f}')
            ax2.set_title('📊 Distribution of Predicted Values')
            ax2.set_xlabel('Predicted Price')
            ax2.set_ylabel('Frequency')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Plot 3: Prediction Trend Analysis with 21 vs 95 period moving averages
            if len(pred_values) > 1:
                # Calculate 21-period and 95-period moving averages
                pred_series = pd.Series(pred_values)
                
                # Only calculate moving averages if we have enough data points
                ma_21 = None
                ma_95 = None
                
                if len(pred_values) >= 21:
                    ma_21 = pred_series.rolling(window=21, center=True).mean()
                
                if len(pred_values) >= 95:
                    ma_95 = pred_series.rolling(window=95, center=True).mean()
                
                # Plot the predictions
                ax3.plot(dates, pred_values, 'o-', alpha=0.6, label='Predictions', 
                         color='blue', linewidth=1, markersize=3)
                
                # Plot moving averages if available
                if ma_21 is not None:
                    ax3.plot(dates, ma_21, '--', linewidth=2, label='21-Period MA (Monthly)', 
                            color='orange', alpha=0.8)
                
                if ma_95 is not None:
                    ax3.plot(dates, ma_95, '-', linewidth=3, label='95-Period MA (Quarterly)', 
                            color='red', alpha=0.9)
                
                # Add crossover analysis if both MAs are available
                if ma_21 is not None and ma_95 is not None:
                    # Find crossover points
                    crossovers = []
                    for i in range(1, len(ma_21)):
                        if not (pd.isna(ma_21.iloc[i]) or pd.isna(ma_95.iloc[i]) or 
                               pd.isna(ma_21.iloc[i-1]) or pd.isna(ma_95.iloc[i-1])):
                            # Bullish crossover (21 MA crosses above 95 MA)
                            if ma_21.iloc[i-1] <= ma_95.iloc[i-1] and ma_21.iloc[i] > ma_95.iloc[i]:
                                ax3.scatter(dates[i], ma_21.iloc[i], color='green', s=100, 
                                          marker='^', label='Bullish Crossover' if not crossovers else "", zorder=5)
                                crossovers.append('bullish')
                            # Bearish crossover (21 MA crosses below 95 MA)
                            elif ma_21.iloc[i-1] >= ma_95.iloc[i-1] and ma_21.iloc[i] < ma_95.iloc[i]:
                                ax3.scatter(dates[i], ma_21.iloc[i], color='red', s=100, 
                                          marker='v', label='Bearish Crossover' if 'bearish' not in crossovers else "", zorder=5)
                                crossovers.append('bearish')
                
                ax3.set_title('📉 Predictions with 21-Period vs 95-Period Moving Averages')
                ax3.set_xlabel('Date/Time')
                ax3.set_ylabel('Predicted Price')
                ax3.legend(loc='upper left')
                ax3.grid(True, alpha=0.3)
                ax3.tick_params(axis='x', rotation=45)
                
                # Add info text about data sufficiency
                info_text = f"Data points: {len(pred_values)}"
                if len(pred_values) < 21:
                    info_text += " (Need 21+ for Monthly MA)"
                elif len(pred_values) < 95:
                    info_text += " (Need 95+ for Quarterly MA)"
                else:
                    info_text += " (Both MAs available)"
                
                ax3.text(0.02, 0.98, info_text, transform=ax3.transAxes, 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                        verticalalignment='top', fontsize=8)
            
            else:
                # Single prediction fallback
                ax3.bar(['Prediction'], [pred_values[0]], color='blue', alpha=0.7)
                ax3.set_title('📊 Single Prediction Value')
                ax3.set_ylabel('Predicted Price')
            
            # Plot 4: Prediction Statistics
            stats_data = {
                'Min': pred_values.min(),
                'Max': pred_values.max(), 
                'Mean': pred_values.mean(),
                'Median': pd.Series(pred_values).median(),
                'Std': pd.Series(pred_values).std()
            }
            
            bars = ax4.bar(stats_data.keys(), stats_data.values(), 
                          color=['red', 'green', 'blue', 'orange', 'purple'], alpha=0.7)
            ax4.set_title('📋 Prediction Statistics Summary')
            ax4.set_ylabel('Value')
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, value in zip(bars, stats_data.values()):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
            
            # Plot 5: Moving Average Comparison
            if len(pred_values) >= 21:
                pred_series = pd.Series(pred_values)
                ma_21 = pred_series.rolling(window=21, center=True).mean()
                
                if len(pred_values) >= 95:
                    ma_95 = pred_series.rolling(window=95, center=True).mean()
                    
                    # Plot MA difference using dates on x-axis
                    ma_diff = ma_21 - ma_95
                    colors = ['red' if x < 0 else 'green' for x in ma_diff]
                    
                    # ✅ FIXED: Use dates instead of array indices, add proper width
                    ax5.bar(dates[:len(ma_diff)], ma_diff, color=colors, alpha=0.6, width=1)
                    ax5.axhline(y=0, color='black', linestyle='-', linewidth=1)
                    ax5.set_title('📊 21-MA vs 95-MA Difference\n(Green=Bullish, Red=Bearish)')
                    ax5.set_xlabel('Date/Time')  # ✅ ADDED: Proper x-axis label
                    ax5.set_ylabel('MA Difference')
                    ax5.tick_params(axis='x', rotation=45)  # ✅ ADDED: Rotate dates for better readability
                    ax5.grid(True, alpha=0.3)
                    
                    # Add summary stats
                    bullish_periods = sum(1 for x in ma_diff if x > 0)
                    bearish_periods = sum(1 for x in ma_diff if x < 0)
                    ax5.text(0.02, 0.98, f"Bullish: {bullish_periods}\nBearish: {bearish_periods}", 
                            transform=ax5.transAxes, bbox=dict(boxstyle="round", facecolor="lightblue"),
                            verticalalignment='top')
                else:
                    # ✅ FIXED: Use dates for single MA plot
                    ax5.plot(dates[:len(ma_21)], ma_21, color='orange', linewidth=2)
                    ax5.set_title('📈 21-Period Moving Average\n(Need 95+ points for comparison)')
                    ax5.set_xlabel('Date/Time')  # ✅ ADDED: Proper x-axis label
                    ax5.set_ylabel('Price')      # ✅ ADDED: Proper y-axis label
                    ax5.tick_params(axis='x', rotation=45)  # ✅ ADDED: Rotate dates for better readability
                    ax5.grid(True, alpha=0.3)
            else:
                ax5.text(0.5, 0.5, 'Need 21+ data points\nfor Moving Average analysis', 
                        ha='center', va='center', transform=ax5.transAxes,
                        bbox=dict(boxstyle="round", facecolor="lightyellow"))
                ax5.set_title('📊 Moving Average Analysis')
            
            # Plot 6: Trading Signals
            if len(pred_values) >= 95:
                # Generate trading signals based on MA crossovers
                signals = []
                signal_dates = []
                signal_values = []
                
                for i in range(1, len(ma_21)):
                    if not (pd.isna(ma_21.iloc[i]) or pd.isna(ma_95.iloc[i]) or 
                           pd.isna(ma_21.iloc[i-1]) or pd.isna(ma_95.iloc[i-1])):
                        
                        # Bullish signal
                        if ma_21.iloc[i-1] <= ma_95.iloc[i-1] and ma_21.iloc[i] > ma_95.iloc[i]:
                            signals.append('BUY')
                            signal_dates.append(dates[i])
                            signal_values.append(pred_values[i])
                        # Bearish signal  
                        elif ma_21.iloc[i-1] >= ma_95.iloc[i-1] and ma_21.iloc[i] < ma_95.iloc[i]:
                            signals.append('SELL')
                            signal_dates.append(dates[i])
                            signal_values.append(pred_values[i])
                
                # Plot signals using proper dates
                ax6.plot(dates, pred_values, alpha=0.5, color='blue', label='Predictions')
                
                # Create buy/sell signal lists with proper date formatting
                buy_signals = [(d, v) for d, v, s in zip(signal_dates, signal_values, signals) if s == 'BUY']
                sell_signals = [(d, v) for d, v, s in zip(signal_dates, signal_values, signals) if s == 'SELL']
                
                if buy_signals:
                    buy_x, buy_y = zip(*buy_signals)
                    ax6.scatter(buy_x, buy_y, color='green', s=100, marker='^', 
                               label=f'BUY Signals ({len(buy_signals)})', zorder=5)
                
                if sell_signals:
                    sell_x, sell_y = zip(*sell_signals)
                    ax6.scatter(sell_x, sell_y, color='red', s=100, marker='v', 
                               label=f'SELL Signals ({len(sell_signals)})', zorder=5)
                
                ax6.set_title(f'🎯 Trading Signals\n({len(signals)} total signals)')
                ax6.set_xlabel('Date/Time')
                ax6.set_ylabel('Price')
                ax6.tick_params(axis='x', rotation=45)
                ax6.legend()
                ax6.grid(True, alpha=0.3)
            
            else:
                ax6.text(0.5, 0.5, 'Need 95+ data points\nfor Trading Signals', 
                        ha='center', va='center', transform=ax6.transAxes,
                        bbox=dict(boxstyle="round", facecolor="lightyellow"))
                ax6.set_title('🎯 Trading Signals')
            
            # NEW Plot 7: 90-Day View from Current Time
            cutoff_90_days = current_time + timedelta(days=90)
            mask_90 = dates_series <= cutoff_90_days
            
            if mask_90.any():
                dates_90 = dates_series[mask_90]
                pred_90 = pred_values_series[mask_90]
                
                ax7.plot(dates_90, pred_90, marker='o', linewidth=2, markersize=3, 
                        color='purple', alpha=0.8, label=f'{len(pred_90)} predictions')
                
                # Add moving average for 90-day view if enough data
                if len(pred_90) >= 21:
                    ma_21_90 = pred_90.rolling(window=21, center=True).mean()
                    ax7.plot(dates_90, ma_21_90, '--', linewidth=2, 
                            color='orange', alpha=0.8, label='21-Day MA')
                
                ax7.set_title(f'📅 Next 90 Days Predictions\n({current_time.strftime("%Y-%m-%d")} to {cutoff_90_days.strftime("%Y-%m-%d")})')
                ax7.set_xlabel('Date/Time')
                ax7.set_ylabel('Predicted Price')
                ax7.grid(True, alpha=0.3, linestyle='--')
                ax7.tick_params(axis='x', rotation=45)
                ax7.legend()
                
                # Add statistics text
                stats_text = f"Min: {pred_90.min():.2f}\nMax: {pred_90.max():.2f}\nMean: {pred_90.mean():.2f}"
                ax7.text(0.02, 0.98, stats_text, transform=ax7.transAxes, 
                        bbox=dict(boxstyle="round", facecolor="plum", alpha=0.7),
                        verticalalignment='top', fontsize=8)
            else:
                ax7.text(0.5, 0.5, 'No predictions within\n90 days from current time', 
                        ha='center', va='center', transform=ax7.transAxes,
                        bbox=dict(boxstyle="round", facecolor="lightyellow"))
                ax7.set_title('📅 Next 90 Days Predictions')
            
            # NEW Plot 8: 21-Day View from Current Time
            cutoff_21_days = current_time + timedelta(days=21)
            mask_21 = dates_series <= cutoff_21_days
            
            if mask_21.any():
                dates_21 = dates_series[mask_21]
                pred_21 = pred_values_series[mask_21]
                
                ax8.plot(dates_21, pred_21, marker='o', linewidth=2, markersize=4, 
                        color='darkgreen', alpha=0.8, label=f'{len(pred_21)} predictions')
                
                # Add trend line for 21-day view
                if len(pred_21) >= 5:
                    z = np.polyfit(range(len(pred_21)), pred_21, 1)
                    trend_line = np.poly1d(z)
                    ax8.plot(dates_21, trend_line(range(len(pred_21))), 
                            'r--', alpha=0.8, linewidth=2, label='Trend Line')
                    
                    # Calculate trend direction
                    trend_direction = "📈 Rising" if z[0] > 0 else "📉 Falling"
                    trend_text = f"Trend: {trend_direction}\nSlope: {z[0]:.3f}"
                else:
                    trend_text = "Need 5+ points\nfor trend analysis"
                
                ax8.set_title(f'📅 Next 21 Days Predictions\n({current_time.strftime("%Y-%m-%d")} to {cutoff_21_days.strftime("%Y-%m-%d")})')
                ax8.set_xlabel('Date/Time')
                ax8.set_ylabel('Predicted Price')
                ax8.grid(True, alpha=0.3, linestyle='--')
                ax8.tick_params(axis='x', rotation=45)
                ax8.legend()
                
                # Add trend and statistics text
                stats_text = f"Min: {pred_21.min():.2f}\nMax: {pred_21.max():.2f}\nMean: {pred_21.mean():.2f}\n{trend_text}"
                ax8.text(0.02, 0.98, stats_text, transform=ax8.transAxes, 
                        bbox=dict(boxstyle="round", facecolor="lightcyan", alpha=0.7),
                        verticalalignment='top', fontsize=8)
            else:
                ax8.text(0.5, 0.5, 'No predictions within\n21 days from current time', 
                        ha='center', va='center', transform=ax8.transAxes,
                        bbox=dict(boxstyle="round", facecolor="lightyellow"))
                ax8.set_title('📅 Next 21 Days Predictions')
            
            # Adjust layout for the new 2x4 grid
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plots_dir = self.config.get('visualization', {}).get('plots_dir', 'plots')
            os.makedirs(plots_dir, exist_ok=True)
            filename = f"{plots_dir}/future_predictions_enhanced_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            self.logger.info(f"💾 Enhanced future prediction plots saved to {filename}")
            
            # Show plots if requested
            if show_plots:
                plt.show()
                self.logger.info("🖼️  Enhanced future prediction plots displayed")
            
            # Create a simple feature importance plot if available
            if hasattr(self.model, 'get_feature_importance'):
                self.create_feature_importance_plot(show_plots)
            
            return filename
            
        except Exception as e:
            self.logger.error(f"❌ Error creating enhanced future-only plots: {str(e)}")
            return None

    def create_feature_importance_plot(self, show_plots=False):
        """Create feature importance plot without training data."""
        try:
            self.logger.info("📊 Creating feature importance plot")
            
            # Get feature importance from the model
            feature_importance = self.model.get_feature_importance()
            
            if feature_importance is not None:
                # Create feature importance plot
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Take top 20 features
                top_features = feature_importance.head(20)
                
                # Create horizontal bar plot
                bars = ax.barh(range(len(top_features)), top_features['importance'], color='skyblue', alpha=0.8)
                ax.set_yticks(range(len(top_features)))
                ax.set_yticklabels(top_features['feature'])
                ax.set_xlabel('Importance Score')
                ax.set_title('🏆 Top 20 Most Important Features (from Loaded Model)')
                ax.grid(True, alpha=0.3, axis='x')
                
                # Add value labels
                for i, (bar, importance) in enumerate(zip(bars, top_features['importance'])):
                    width = bar.get_width()
                    ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                           f'{importance:.3f}', ha='left', va='center', fontsize=8)
                
                plt.tight_layout()
                
                # Save plot
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                plots_dir = self.config.get('visualization', {}).get('plots_dir', 'plots')
                filename = f"{plots_dir}/feature_importance_{timestamp}.png"
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                self.logger.info(f"🏆 Feature importance plot saved to {filename}")
                
                if show_plots:
                    plt.show()
                
            else:
                self.logger.warning("⚠️  Could not get feature importance from model")
            
        except Exception as e:
            self.logger.error(f"❌ Error creating feature importance plot: {str(e)}")

    def print_prediction_summary(self):
        """Print a comprehensive summary of predictions."""
        print("\n" + "="*70)
        print("🎯 FUTURE PREDICTIONS SUMMARY")
        print("="*70)
        
        if hasattr(self.predictions, 'shape'):
            print(f"📊 Total predictions generated: {len(self.predictions)}")
            
            if hasattr(self.predictions, 'describe'):
                pred_col = 'predicted_value' if 'predicted_value' in self.predictions.columns else self.predictions.columns[0]
                stats = self.predictions[pred_col].describe()
                
                print(f"\n📈 Prediction Statistics:")
                print(f"   Count: {stats['count']:.0f}")
                print(f"   Mean:  {stats['mean']:.2f}")
                print(f"   Std:   {stats['std']:.2f}")
                print(f"   Min:   {stats['min']:.2f}")
                print(f"   25%:   {stats['25%']:.2f}")
                print(f"   50%:   {stats['50%']:.2f}")
                print(f"   75%:   {stats['75%']:.2f}")
                print(f"   Max:   {stats['max']:.2f}")
                
            print(f"\n🔍 Sample Predictions:")
            if hasattr(self.predictions, 'head'):
                print(self.predictions.head(10).to_string())
            
        print(f"\n💾 Results saved to: csv_logs/{self.run_id}/")
        print("="*70)

    def quick_predict(self, model_path, num_predictions=30):
        """
        Ultra-fast prediction mode - minimal processing.
        
        Args:
            model_path (str): Path to model file
            num_predictions (int): Number of future predictions to make
            
        Returns:
            dict: Predictions and metadata
        """
        self.logger.info(f"🚀 Quick prediction mode: loading model and generating {num_predictions} predictions")
        
        # Load model
        self.load_pretrained_model(model_path)
        
        # Generate minimal future data
        self.future_data = self.future_generator.generate_minimal(num_predictions)
        
        # Make predictions
        self.predictions = self.predictor.predict(self.model, self.future_data)
        
        print(f"⚡ Quick predictions completed: {len(self.predictions)} predictions generated")
        
        return {
            'predictions': self.predictions,
            'model_loaded': True,
            'mode': 'quick_predict'
        }


def main():
    """Main entry point for the GFAnalytics framework."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='GFAnalytics Framework')
    parser.add_argument('--clean', action='store_true', help='Clean all tables')
    parser.add_argument('--clean-table', type=str, help='Clean specific table')
    parser.add_argument('--show-plots', action='store_true', help='Show plots during pipeline execution')
    parser.add_argument('--display-plots', action='store_true', help='Only display previously generated plots')
    parser.add_argument('--list-runs', action='store_true', help='List all available runs')
    parser.add_argument('--run-logs', type=str, help='Show logs for a specific run ID')
    parser.add_argument('--load-model', type=str, help='Load pre-trained model and make predictions (fast mode)')
    parser.add_argument('--quick-predict', type=str, help='Ultra-fast prediction with specified model (minimal processing)')
    parser.add_argument('--list-models', action='store_true', help='List all available saved models')
    
    args = parser.parse_args()
    
    # Handle command-line arguments for run management
    if args.list_runs:
        runs = list_runs()
        if len(runs) == 0:
            print("No runs found.")
        else:
            print(f"Found {len(runs)} runs:")
            # Format timestamp nicely
            runs['timestamp_str'] = runs['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            print(runs[['run_id', 'timestamp_str', 'logs_count']].to_string(index=False))
        return runs
    
    if args.run_logs:
        logs = get_run_logs(args.run_logs)
        if len(logs) == 0:
            print(f"No logs found for run ID: {args.run_logs}")
        else:
            print(f"Found {len(logs)} logs for run ID: {args.run_logs}")
            # Format size and timestamp nicely
            logs['size_kb'] = (logs['size'] / 1024).round(2)
            logs['modified_time_str'] = logs['modified_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            print(logs[['filename', 'size_kb', 'modified_time_str']].to_string(index=False))
        return logs
    
    # Create an instance of the GFAnalytics framework
    gf = GFAnalytics()
    
    if args.quick_predict:
        # Ultra-fast prediction mode
        results = gf.quick_predict(args.quick_predict)
        print(f"🎯 Quick prediction completed!")
        return results
    elif args.load_model:
        # Fast prediction mode (current implementation)
        results = gf.run_with_pretrained_model(args.load_model, show_plots=args.show_plots)
        print(f"✅ Prediction completed. Run ID: {results['run_id']}")
        return results
    elif args.list_models:
        models = list_models(gf)
        if len(models) == 0:
            print("No saved models found.")
        else:
            print(f"Found {len(models)} saved models:")
            for model in models:
                print(f"  {model['type']}: {model['name']} ({model['size_mb']} MB) - {model['modified']}")
                if model['type'] == 'local':
                    print(f"    Path: {model['path']}")
        return models
    elif args.clean:
        gf.clean_tables()
    elif args.clean_table:
        gf.clean_table(args.clean_table)
    elif args.display_plots:
        # Just display plots without running the pipeline
        return gf.display_plots()
    else:
        # Run the complete pipeline (including training)
        results = gf.run(show_plots=args.show_plots)
        print(f"\nCompleted run with ID: {results['run_id']}")
        print(f"CSV logs are stored in: {os.path.join('csv_logs', results['run_id'])}")
        return results

def list_models(gf_instance):
    """List all available models."""
    models = []
    
    # List local models
    local_models_dir = gf_instance.model_storage.local_backup_dir
    if os.path.exists(local_models_dir):
        local_files = [f for f in os.listdir(local_models_dir) if f.endswith('.pkl')]
        for file in local_files:
            file_path = os.path.join(local_models_dir, file)
            stat = os.stat(file_path)
            models.append({
                'type': 'local',
                'name': file,
                'path': file_path,
                'size_mb': round(stat.st_size / (1024*1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return models

if __name__ == "__main__":
    main() 