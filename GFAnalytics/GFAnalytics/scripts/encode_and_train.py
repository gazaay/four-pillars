#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to demonstrate encoding and training workflow for GFAnalytics.

This script shows how to:
1. Load stock and bazi data
2. Encode categorical features
3. Train a random forest model
4. Save the model and encoders
5. Load the model and make predictions
"""

import os
import logging
import pandas as pd
import yaml
from datetime import datetime
import pytz

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GFAnalytics.encode_and_train')

# Import GFAnalytics modules
from GFAnalytics.data.data_storage import BigQueryStorage
from GFAnalytics.data.stock_data import StockDataLoader
from GFAnalytics.data.bazi_data import BaziDataGenerator
from GFAnalytics.models.random_forest import RandomForestModel
from GFAnalytics.utils.encoding_utils import process_encode_data

def load_config(config_path='config/config.yaml'):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise

def main():
    """Main function to demonstrate encoding and training workflow."""
    try:
        # Get the current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the config file
        config_path = os.path.join(os.path.dirname(script_dir), 'config', 'config.yaml')
        
        # Load configuration
        config = load_config(config_path)
        
        # Initialize BigQueryStorage
        storage = BigQueryStorage(config)
        
        # Create a batch for this run
        batch_id = storage.create_batch(
            description="Encoding and training demonstration",
            process_type="demo",
            parameters=config
        )
        logger.info(f"Created batch with ID: {batch_id}")
        
        # Load stock data
        stock_loader = StockDataLoader(config)
        stock_data = stock_loader.load_data(
            start_date=config['date_range']['training']['start_date'],
            end_date=config['date_range']['training']['end_date']
        )
        logger.info(f"Loaded {len(stock_data)} stock data records")
        
        # Generate Bazi data
        bazi_generator = BaziDataGenerator(config)
        bazi_data = bazi_generator.generate(stock_data)
        logger.info(f"Generated {len(bazi_data)} Bazi data records")
        
        # Store the data with batch_id
        storage.store_stock_data(stock_data)
        storage.store_bazi_data(bazi_data)
        
        # Merge stock and Bazi data
        merged_data = pd.merge(stock_data, bazi_data, on='time')
        logger.info(f"Merged data shape: {merged_data.shape}")
        
        # Add target variable (next day's close price)
        merged_data['target'] = merged_data['Close_x'].shift(-1)
        # Drop rows with NaN target (last row)
        merged_data = merged_data.dropna(subset=['target'])
        logger.info(f"Data with target shape: {merged_data.shape}")
        
        # Encode the categorical features
        logger.info("Encoding categorical features")
        encoded_data, label_encoders = process_encode_data(merged_data)
        logger.info(f"Encoded data shape: {encoded_data.shape}")
        
        # Initialize and train the model
        logger.info("Initializing and training the model")
        model = RandomForestModel(config)
        model.train(encoded_data)
        
        # Get feature importance
        feature_importance = model.get_feature_importance()
        logger.info(f"Feature importance top 10:\n{feature_importance.head(10)}")
        
        # Save the model
        model_dir = os.path.join(os.path.dirname(script_dir), 'models')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f'rf_model_{datetime.now(pytz.timezone("Asia/Hong_Kong")).strftime("%Y%m%d%H%M%S")}.pkl')
        model.save(model_path)
        
        # Make predictions for demonstration
        predictions = model.predict(encoded_data.head(10))
        logger.info(f"Sample predictions: {predictions}")
        
        # Create a prediction dataframe
        prediction_df = pd.DataFrame({
            'time': encoded_data.head(10)['time'],
            'stock_code': config['stock']['code'],
            'predicted_value': predictions,
            'confidence': 0.95,  # Placeholder confidence value
        })
        
        # Store predictions
        storage.store_prediction_data(prediction_df)
        
        # Store model metrics
        metrics = {
            'model_id': f"rf_{datetime.now(pytz.timezone('Asia/Hong_Kong')).strftime('%Y%m%d%H%M%S')}",
            'stock_code': config['stock']['code'],
            'training_start_date': config['date_range']['training']['start_date'],
            'training_end_date': config['date_range']['training']['end_date'],
            'mse': 0.0,  # Placeholder, should calculate actual metrics
            'rmse': 0.0,
            'r2': model.model.score(encoded_data.drop(['target'], axis=1, errors='ignore'), encoded_data['target']),
            'medae': 0.0,
            'feature_importance': feature_importance.head(20).to_json()
        }
        storage.store_model_metrics(metrics)
        
        # Complete the batch
        storage.complete_batch(batch_id)
        logger.info(f"Completed batch with ID: {batch_id}")
        
    except Exception as e:
        logger.error(f"Error in encoding and training workflow: {str(e)}")
        if 'storage' in locals() and 'batch_id' in locals():
            storage.complete_batch(batch_id, status='failed')
            logger.info(f"Marked batch {batch_id} as failed")
        raise

if __name__ == "__main__":
    main() 