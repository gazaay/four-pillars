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
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info("GFAnalytics framework initialized")
    
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
            dict: Results containing evaluation metrics and predictions.
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
            'evaluation': self.evaluation_results,
            'predictions': self.predictions
        }
    
    def load_data(self):
        """Load stock data and generate Bazi data."""
        self.logger.info("Loading stock data")
        self.stock_data = self.stock_loader.load()
        self.bq_storage.store_stock_data(self.stock_data)
        
        self.logger.info("Generating Bazi data")
        self.bazi_data = self.bazi_generator.generate(self.stock_data)
        self.bq_storage.store_bazi_data(self.bazi_data)
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
        
        # Transform to ChengShen attributes
        self.logger.info("Applying ChengShen transformation...")
        chengshen_features = self.chengshen_transformer.transform(bazi_features)
        self.logger.info(f"Features shape after ChengShen transformation: {chengshen_features.shape}")
        
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
        
        # Store training data
        self.bq_storage.store_training_data(self.training_data)
        self.logger.info("Training data stored in BigQuery")

        return self.training_data
    
    def train_model(self):
        """Train the machine learning model."""
        self.logger.info("Training model")
        
        # Print first 2 rows of training data
        self.logger.info(f"\nFirst 2 rows of training data:\n{self.training_data.head(2)}")
        # Remove duplicate stock code and RIC code columns
        # if 'stock_code_y' in self.training_data.columns:
        #     self.training_data = self.training_data.drop('stock_code_y', axis=1)
        # if 'ric_code_y' in self.training_data.columns:
        #     self.training_data = self.training_data.drop('ric_code_y', axis=1)
        # Train the model
        self.model.train(self.training_data)
        
        # Save the model to Google Drive
        self.model_storage.save_model(self.model)
        
        return self.model
    
    def evaluate_model(self):
        """Evaluate the model performance."""
        self.logger.info("Evaluating model")
        
        # Make sure we're using the same training data for evaluation
        if self.training_data is None:
            self.logger.error("Training data not available for evaluation")
            return None
            
        # Copy the training data to avoid modifying it
        evaluation_data = self.training_data.copy()
        
        # Log training data shape
        self.logger.info(f"Evaluation data shape: {evaluation_data.shape}")
        self.logger.info(f"Evaluation data columns: {evaluation_data.columns[:5]}...")
        
        # Evaluate the model using the training data
        self.evaluation_results = self.evaluator.evaluate(self.model, evaluation_data)
        
        # Store evaluation results in BigQuery
        metrics_dict = {
            'model_id': f"rf_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'stock_code': self.config['stock']['code'],
            'training_start_date': self.config['date_range']['training']['start_date'],
            'training_end_date': self.config['date_range']['training']['end_date'],
            'timestamp': datetime.now()
        }
        
        # Add evaluation metrics to the dict
        for metric, value in self.evaluation_results.items():
            if isinstance(value, (int, float)):
                metrics_dict[metric.lower()] = value
            elif metric == 'feature_importance' and value is not None:
                # Convert top 20 features to JSON
                try:
                    metrics_dict['feature_importance'] = value.head(20).to_json()
                except:
                    self.logger.warning("Could not convert feature importance to JSON")
        
        # Store metrics in BigQuery
        self.bq_storage.store_model_metrics(metrics_dict)
        
        return self.evaluation_results
    
    def predict_future(self):
        """Generate predictions for future data."""
        self.logger.info("Generating future predictions")
        
        # Generate future data
        self.future_data = self.future_generator.generate()
        
        # Make predictions
        self.predictions = self.predictor.predict(self.model, self.future_data)
        
        # Store predictions
        self.bq_storage.store_prediction_data(self.predictions)
        
        return self.predictions
    
    def visualize_results(self, show_plots=False):
        """
        Visualize the results.
        
        Args:
            show_plots (bool): Whether to display the plots immediately.
        
        Returns:
            bool: True if visualization was successful, False otherwise.
        """
        self.logger.info("Visualizing results")
        
        # Make sure we have required data
        if self.stock_data is None or self.predictions is None:
            self.logger.error("Cannot visualize results: missing stock data or predictions")
            return False
            
        # Make sure the model is trained
        if self.model is None:
            self.logger.error("Cannot visualize results: model not trained")
            return False
        
        # Plot predictions
        if self.config['visualization']['plot_prediction']:
            self.logger.info("Creating prediction plot...")
            self.plotter.plot_prediction(self.stock_data, self.predictions, show=show_plots)
        
        # Plot feature importance
        if self.config['model']['evaluation']['feature_importance']:
            self.logger.info("Creating feature importance plot...")
            # Use the training data directly
            self.plotter.plot_feature_importance(self.model, self.training_data, show=show_plots)
        
        # Plot correlation heatmap
        if self.config['model']['evaluation']['correlation_heatmap']:
            self.logger.info("Creating correlation heatmap...")
            # Use the training data directly
            self.plotter.plot_correlation_heatmap(self.training_data, show=show_plots)
            
        # Plot Bazi element predictions if we have encoders from the model
        if hasattr(self.model, 'label_encoders') and self.model.label_encoders:
            self.logger.info("Creating Bazi predictions plot...")
            # Pass the encoders for decoding Bazi elements
            self.plotter.plot_bazi_predictions(self.predictions, self.model.label_encoders, show=show_plots)
        
        # If show_plots is False but we want to display them all at once
        if not show_plots and self.config['visualization'].get('display_plots_at_end', True):
            self.display_plots()
            
        self.logger.info("Visualization completed")
        return True
        
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


def main():
    """Main entry point for the GFAnalytics framework."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='GFAnalytics Framework')
    parser.add_argument('--clean', action='store_true', help='Clean all tables')
    parser.add_argument('--clean-table', type=str, help='Clean specific table')
    parser.add_argument('--show-plots', action='store_true', help='Show plots during pipeline execution')
    parser.add_argument('--display-plots', action='store_true', help='Only display previously generated plots')
    args = parser.parse_args()
    
    # Create an instance of the GFAnalytics framework
    gf = GFAnalytics()
    
    if args.clean:
        gf.clean_tables()
    elif args.clean_table:
        gf.clean_table(args.clean_table)
    elif args.display_plots:
        # Just display plots without running the pipeline
        return gf.display_plots()
    else:
        # Run the complete pipeline
        results = gf.run(show_plots=args.show_plots)
        
        # We don't need to call display_plots here since we're passing show_plots to run()
        return results

if __name__ == "__main__":
    main() 