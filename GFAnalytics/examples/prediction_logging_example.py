#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example script demonstrating the use of the prediction module with DataFrame logging.
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import necessary modules
from GFAnalytics.prediction.future_data import FutureDataGenerator
from GFAnalytics.prediction.predictor import Predictor
from GFAnalytics.models.random_forest import RandomForestModel
from GFAnalytics.utils.csv_utils import configure as configure_csv_logging, logdf

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('PredictionExample')

def load_config():
    """Load the configuration file."""
    import yaml
    
    # Get the path to the configuration file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), 'config', 'config.yaml')
    
    # Load the configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config, config_path

def create_dummy_model(config):
    """Create a dummy model for testing."""
    # Create a RandomForestModel instance
    model = RandomForestModel(config)
    
    # Create a dummy DataFrame with some data for demonstration
    df = pd.DataFrame({
        'time': pd.date_range(start='2023-01-01', periods=100),
        'open': np.random.random(100) * 100,
        'high': np.random.random(100) * 100 + 5,
        'low': np.random.random(100) * 100 - 5,
        'close': np.random.random(100) * 100,
        'volume': np.random.randint(1000, 10000, 100),
        'wuxi': np.random.choice(['金', '木', '水', '火', '土'], 100),
        'day_gan': np.random.choice(['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'], 100),
        'target': np.random.random(100) * 100  # Target variable for training
    })
    
    # Log the training data
    logdf(df, 'prediction_example_training_data')
    
    # Create a dummy trained model (we don't actually train it for this example)
    model.model = None  # In reality, this would be the trained model
    model.label_encoders = {}  # In reality, this would contain the encoders
    
    # Create a simple mock predict method
    def mock_predict(data):
        # Create random predictions
        return np.random.random(len(data)) * 100
    
    # Add the mock predict method to the model
    model.predict = mock_predict
    
    return model

def main():
    """Main function demonstrating prediction with DataFrame logging."""
    print("Prediction with DataFrame Logging Example")
    print("========================================")
    
    # Load configuration
    config, config_path = load_config()
    
    # Configure DataFrame logging
    print(f"Configuring DataFrame logger with config from: {config_path}")
    configure_csv_logging(config_path)
    
    # Log the configuration
    config_df = pd.DataFrame([config])
    logdf(config_df, 'prediction_example_config')
    
    # Create the future data generator
    print("\nCreating FutureDataGenerator...")
    future_generator = FutureDataGenerator(config)
    
    # Generate future data for prediction
    print("\nGenerating future data...")
    future_data = future_generator.generate(
        base_date=datetime.now(),
        label_encoders=None  # Would usually come from the trained model
    )
    
    # Log the future data at this point
    logdf(future_data, 'prediction_example_future_data')
    
    # Create a dummy model for demonstration
    print("\nCreating a dummy model...")
    model = create_dummy_model(config)
    
    # Create the predictor
    print("\nCreating Predictor...")
    predictor = Predictor(config)
    
    # Make predictions
    print("\nMaking predictions...")
    try:
        predictions = predictor.predict(model, future_data)
        
        # Log the final predictions
        logdf(predictions, 'prediction_example_final_predictions')
        
        # Display some predictions
        print("\nSample predictions:")
        pd.set_option('display.max_rows', 10)
        print(predictions.head(10))
        
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        # Log the error
        error_df = pd.DataFrame({'error': [str(e)]})
        logdf(error_df, 'prediction_example_error')
    
    print("\nPrediction example complete.")
    print("Check the csv_logs directory for the logged DataFrames.")

if __name__ == "__main__":
    main() 