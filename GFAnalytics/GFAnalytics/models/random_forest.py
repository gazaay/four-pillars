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
        
        # Prepare the data
        X, y = self._prepare_data(df)
        
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.model_params.get('random_state', 42)
        )
        
        # Create and train the model
        self.model = RandomForestRegressor(
            n_estimators=self.model_params.get('n_estimators', 100),
            max_depth=self.model_params.get('max_depth', None),
            min_samples_split=self.model_params.get('min_samples_split', 2),
            min_samples_leaf=self.model_params.get('min_samples_leaf', 1),
            random_state=self.model_params.get('random_state', 42),
            n_jobs=-1  # Use all available cores
        )
        
        # Train the model
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
        
        # Prepare the data
        X, _ = self._prepare_data(df, is_training=False)
        
        # Make predictions
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
        # Create a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Drop non-feature columns
        columns_to_drop = ['time', 'uuid', 'last_modified_date']
        if is_training:
            columns_to_drop.append('target')
        
        # Drop columns that exist in the DataFrame
        columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        
        # Prepare features (X)
        X = df.drop(columns_to_drop, axis=1, errors='ignore')
        
        # Prepare target (y) if training
        y = df['target'] if is_training and 'target' in df.columns else None
        
        return X, y
    
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
        
        # Prepare the data
        X, y = self._prepare_data(df)
        
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
        
        # Get feature importance
        importance = self.model.feature_importances_
        
        # Create a DataFrame with feature names and importance
        feature_importance = pd.DataFrame({
            'feature': self.model.feature_names_in_,
            'importance': importance
        })
        
        # Sort by importance
        feature_importance = feature_importance.sort_values('importance', ascending=False)
        
        return feature_importance
    
    def save(self, filepath):
        """
        Save the trained model to a file.
        
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
            
            logger.info(f"Model saved successfully to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            return False
    
    def load(self, filepath):
        """
        Load a trained model from a file.
        
        Args:
            filepath (str): The path to load the model from.
            
        Returns:
            RandomForestModel: The loaded model.
        """
        logger.info(f"Loading model from {filepath}")
        
        try:
            # Load the model
            self.model = joblib.load(filepath)
            
            logger.info(f"Model loaded successfully from {filepath}")
            return self
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise 