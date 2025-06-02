#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example script demonstrating the use of encoding utilities.
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GFAnalytics.utils.encoding_utils import (
    get_categorical_columns,
    process_encode_data,
    decode_prediction_data
)

def main():
    """Main function demonstrating encoding utilities workflow."""
    print("Creating sample stock data...")
    
    # Create sample data
    np.random.seed(42)  # For reproducibility
    
    # Sample size
    n_samples = 1000
    
    # Generate Chinese zodiac signs and elements
    gan_list = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    zhi_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    wuxi_list = ['金', '木', '水', '火', '土']
    
    # Generate sample data
    data = pd.DataFrame({
        'date': pd.date_range(start='2020-01-01', periods=n_samples),
        'stock_code': np.random.choice(['000001', '000002', '000003', '000004', '000005'], n_samples),
        'open': np.random.random(n_samples) * 100,
        'high': np.random.random(n_samples) * 100,
        'low': np.random.random(n_samples) * 100,
        'close': np.random.random(n_samples) * 100,
        'volume': np.random.randint(1000, 10000, n_samples),
        'day_gan': np.random.choice(gan_list, n_samples),
        'day_zhi': np.random.choice(zhi_list, n_samples),
        'wuxi': np.random.choice(wuxi_list, n_samples),
        # Create some missing values
        'sector': np.random.choice(['Technology', 'Finance', 'Healthcare', 'Energy', None], n_samples, 
                                  p=[0.3, 0.3, 0.2, 0.1, 0.1])
    })
    
    # Add a derived column
    data['bazi_day'] = data['day_gan'] + data['day_zhi']
    
    # Add a target variable (simplified for demonstration)
    # In this example, we're predicting if a stock will go up based on its features
    data['target'] = np.where(
        (data['wuxi'] == '金') & (data['day_gan'].isin(['甲', '乙'])) |
        (data['wuxi'] == '木') & (data['day_gan'].isin(['丙', '丁'])) |
        (data['wuxi'] == '水') & (data['day_gan'].isin(['戊', '己'])) |
        (data['wuxi'] == '火') & (data['day_gan'].isin(['庚', '辛'])) |
        (data['wuxi'] == '土') & (data['day_gan'].isin(['壬', '癸'])),
        1, 0
    )
    
    print(f"Generated {len(data)} rows of sample data")
    print("\nSample of the data:")
    print(data.head())
    
    # Split data into features and target
    X = data.drop('target', axis=1)
    y = data['target']
    
    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("\nIdentifying categorical columns...")
    cat_columns = get_categorical_columns(X_train)
    print(f"Identified categorical columns: {cat_columns}")
    
    print("\nEncoding categorical features...")
    # Process and encode the training data
    X_train_encoded, encoders = process_encode_data(X_train)
    
    # Save encoders for later use
    os.makedirs('model_artifacts', exist_ok=True)
    with open('model_artifacts/encoders.pkl', 'wb') as f:
        pickle.dump(encoders, f)
    
    print("\nTraining a model with encoded features...")
    # Create and train a model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Select only numeric columns for training
    numeric_columns = X_train_encoded.select_dtypes(include=[np.number]).columns
    model.fit(X_train_encoded[numeric_columns], y_train)
    
    # Save the model
    with open('model_artifacts/rf_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("\nEncoding test data using the same encoders...")
    # Process and encode the test data with the same encoders
    X_test_encoded, _ = process_encode_data(X_test, encoders)
    
    print("\nMaking predictions...")
    # Make predictions
    y_pred = model.predict(X_test_encoded[numeric_columns])
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")
    
    print("\nExample of processing new data for prediction:")
    # Create a small sample of new data
    new_data = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=5),
        'stock_code': ['000001', '000002', '000003', '000004', '000005'],
        'open': np.random.random(5) * 100,
        'high': np.random.random(5) * 100,
        'low': np.random.random(5) * 100,
        'close': np.random.random(5) * 100,
        'volume': np.random.randint(1000, 10000, 5),
        'day_gan': ['甲', '乙', '丙', '丁', '戊'],
        'day_zhi': ['子', '丑', '寅', '卯', '辰'],
        'wuxi': ['金', '木', '水', '火', '土'],
        'sector': ['Technology', 'Finance', 'Healthcare', 'Energy', None]
    })
    new_data['bazi_day'] = new_data['day_gan'] + new_data['day_zhi']
    
    # Process and encode the new data using the same encoders
    new_data_encoded, _ = process_encode_data(new_data, encoders)
    
    # Make predictions on new data
    new_pred = model.predict(new_data_encoded[numeric_columns])
    
    # Add predictions to the original data
    new_data['predicted'] = new_pred
    
    print("New data with predictions:")
    print(new_data[['stock_code', 'day_gan', 'day_zhi', 'wuxi', 'predicted']])
    
    print("\nEncoding utilities demonstration complete.")

if __name__ == "__main__":
    main() 