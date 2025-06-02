#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Random Forest Model Module for GFAnalytics

This module provides functionality to implement a Random Forest model for stock price prediction.
"""

import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
import joblib
import os
import json
# Import logging utilities
from GFAnalytics.utils.csv_utils import logdf


# Import encoding utilities
from GFAnalytics.utils.encoding_utils import process_encode_data, decode_prediction_data
# Import data utilities
from GFAnalytics.utils.data_utils import prepare_feature_data, get_feature_importance as get_feature_importance_util

# Set up logger
logger = logging.getLogger('GFAnalytics.random_forest')


class RandomForestModel:
    """
    Class for implementing a Random Forest model for stock price prediction.
    """
    
    def __init__(self, config):
        """
        Initialize the RandomForestModel.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.model_params = config['model']['params']
        self.model = None
        self.label_encoders = {}
        self.feature_names = None
        logger.info("RandomForestModel initialized")
    
    def train(self, data):
        """
        Train the Random Forest model.
        
        Args:
            data (pandas.DataFrame): The training data.
            
        Returns:
            RandomForestModel: The trained model.
        """
        logger.info("Training Random Forest model")
        
        # Create a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Encode categorical features
        logger.info("Encoding categorical features")
        encoded_df, self.label_encoders = process_encode_data(df)
        
        # Prepare the data
        X, y = self._prepare_data(encoded_df)
        
        # Store feature names for later use
        self.feature_names = X.columns.tolist()
        
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.model_params.get('random_state', 42)
        )
        
        # Log training data
        logdf(pd.DataFrame(X_train, columns=X.columns), 'random_forest_X_train')
        logdf(pd.DataFrame(y_train, columns=['target']), 'random_forest_y_train')

        # Create and train the model
        self.model = RandomForestRegressor(
            n_estimators=self.model_params.get('n_estimators', 100),
            max_depth=self.model_params.get('max_depth', None),
            min_samples_split=self.model_params.get('min_samples_split', 2),
            min_samples_leaf=self.model_params.get('min_samples_leaf', 1),
            random_state=self.model_params.get('random_state', 42),
            n_jobs=-1,  # Use all available cores
            verbose=1
        )
        
        # Train the model
        logger.info(f"Training with {X_train.shape[0]} samples, {X_train.shape[1]} features")
        self.model.fit(X_train, y_train)
        
        # Log training results
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        logger.info(f"Model trained successfully. Train R² score: {train_score:.4f}, Test R² score: {test_score:.4f}")
        
        return self
    
    def predict(self, data):
        """
        Make predictions using the trained model.
        
        Args:
            data (pandas.DataFrame): The data to make predictions on.
            
        Returns:
            numpy.ndarray: The predictions.
        """
        logger.info("Making predictions with Random Forest model")
        
        # Check if the model has been trained
        if self.model is None:
            logger.error("Model has not been trained yet")
            raise ValueError("Model has not been trained yet")
        
        # Create a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Encode categorical features using the same encoders from training
        logger.info("Encoding categorical features for prediction")
        encoded_df, _ = process_encode_data(df)
        
        # Prepare the data
        X, _ = self._prepare_data(encoded_df, is_training=False)
        
        # Ensure all required features are present
        if self.feature_names is not None:
            missing_features = set(self.feature_names) - set(X.columns)
            extra_features = set(X.columns) - set(self.feature_names)
            
            if missing_features:
                logger.warning(f"Missing features in prediction data: {missing_features}")
                # Add missing features with zeros
                for feature in missing_features:
                    X[feature] = 0
            
            if extra_features:
                logger.warning(f"Extra features in prediction data: {extra_features}")
                # Keep only the features used in training
                X = X[self.feature_names]
        
        # Make predictions
        logger.info(f"Making predictions on {len(X)} samples")
        predictions = self.model.predict(X)
        
        logger.info(f"Made {len(predictions)} predictions")
        return predictions
    
    def _prepare_data(self, data, is_training=True):
        """
        Prepare the data for training or prediction.
        
        Args:
            data (pandas.DataFrame): The data to prepare.
            is_training (bool): Whether the data is for training.
            
        Returns:
            tuple: A tuple containing (X, y) if is_training is True, otherwise (X, None).
        """
        # Use the shared data preparation utility
        return prepare_feature_data(data, is_training)
    
    def tune_hyperparameters(self, data):
        """
        Tune the hyperparameters of the Random Forest model using GridSearchCV.
        
        Args:
            data (pandas.DataFrame): The training data.
            
        Returns:
            dict: The best hyperparameters.
        """
        logger.info("Tuning hyperparameters for Random Forest model")
        
        # Create a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Encode categorical features
        encoded_df, self.label_encoders = process_encode_data(df)
        
        # Prepare the data
        X, y = self._prepare_data(encoded_df)
        
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.model_params.get('random_state', 42)
        )
        
        # Define the hyperparameter grid
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        # Create the model
        rf = RandomForestRegressor(random_state=self.model_params.get('random_state', 42))
        
        # Create the grid search
        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            cv=5,
            n_jobs=-1,
            verbose=1
        )
        
        # Fit the grid search
        grid_search.fit(X_train, y_train)
        
        # Get the best parameters
        best_params = grid_search.best_params_
        
        # Update the model parameters
        self.model_params.update(best_params)
        
        # Create and train the model with the best parameters
        self.model = RandomForestRegressor(**self.model_params, n_jobs=-1)
        self.model.fit(X_train, y_train)
        
        # Log results
        logger.info(f"Best hyperparameters: {best_params}")
        logger.info(f"Best score: {grid_search.best_score_:.4f}")
        
        return best_params
    
    def get_feature_importance(self):
        """
        Get the feature importance of the trained model.
        
        Returns:
            pandas.DataFrame: The feature importance.
        """
        logger.info("Getting feature importance")
        
        # Check if the model has been trained
        if self.model is None:
            logger.error("Model has not been trained yet")
            raise ValueError("Model has not been trained yet")
        
        # Use the shared feature importance utility
        feature_importance = get_feature_importance_util(self)
        
        # Log top features
        top_features = feature_importance.head(20)
        logger.info(f"Top 20 most important features:\n{top_features}")
        
        return feature_importance
    
    def save(self, filepath):
        """
        Save the trained model and encoders to files.
        
        Args:
            filepath (str): The path to save the model to.
            
        Returns:
            bool: True if the model was saved successfully, False otherwise.
        """
        logger.info(f"Saving model to {filepath}")
        
        # Check if the model has been trained
        if self.model is None:
            logger.error("Model has not been trained yet")
            raise ValueError("Model has not been trained yet")
        
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save the model
            joblib.dump(self.model, filepath)
            
            # Save the feature names
            feature_names_path = filepath.replace('.pkl', '_features.json')
            with open(feature_names_path, 'w') as f:
                json.dump(self.feature_names, f)
            
            # Save the encoders
            encoders_path = filepath.replace('.pkl', '_encoders.pkl')
            joblib.dump(self.label_encoders, encoders_path)
            
            logger.info(f"Model saved successfully to {filepath}")
            logger.info(f"Feature names saved to {feature_names_path}")
            logger.info(f"Encoders saved to {encoders_path}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            return False
    
    def load(self, filepath):
        """
        Load a trained model and encoders from files.
        
        Args:
            filepath (str): The path to load the model from.
            
        Returns:
            RandomForestModel: The loaded model.
        """
        logger.info(f"Loading model from {filepath}")
        
        try:
            # Load the model
            self.model = joblib.load(filepath)
            
            # Load the feature names
            feature_names_path = filepath.replace('.pkl', '_features.json')
            if os.path.exists(feature_names_path):
                with open(feature_names_path, 'r') as f:
                    self.feature_names = json.load(f)
            
            # Load the encoders
            encoders_path = filepath.replace('.pkl', '_encoders.pkl')
            if os.path.exists(encoders_path):
                self.label_encoders = joblib.load(encoders_path)
            
            logger.info(f"Model loaded successfully from {filepath}")
            
            if self.feature_names:
                logger.info(f"Loaded {len(self.feature_names)} feature names")
            
            if self.label_encoders:
                logger.info(f"Loaded {len(self.label_encoders)} label encoders")
            
            return self
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise 