#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Model Storage Module

This module handles saving and loading models from Google Drive.
It provides functionality to store trained models and retrieve them later.
"""

import os
import pickle
import logging
from datetime import datetime
import tempfile
import pytz
import joblib
import json
import io

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

# Set up logger
logger = logging.getLogger('GFAnalytics.GoogleDriveStorage')

class GoogleDriveStorage:
    """
    Handles saving and loading models from Google Drive.
    
    This class provides functionality to store trained models in Google Drive
    and retrieve them later for prediction.
    """
    
    def __init__(self, config):
        """
        Initialize the GoogleDriveStorage.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.folder_id = config['gcp']['gdrive']['folder_id']
        self.model_filename = config['gcp']['gdrive']['model_filename']
        self.credentials_path = config['gcp']['credentials_path']
        self.service = None
        
        # Create local backup directory
        self.local_backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
        os.makedirs(self.local_backup_dir, exist_ok=True)
        
        try:
            # Initialize Drive API client
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive storage initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive storage: {str(e)}")
            logger.info("Will use local storage as fallback")
    
    def save_model(self, model):
        """
        Save the model to Google Drive.
        
        Args:
            model: The model to save.
            
        Returns:
            str: The ID of the file in Google Drive, or local path if fallback used.
        """
        try:
            # Generate timestamp for filename
            timestamp = datetime.now(pytz.timezone('Asia/Hong_Kong')).strftime('%Y%m%d_%H%M%S')
            filename = self.model_filename.replace('.pkl', f'_{timestamp}.pkl')
            
            # Save model to a temporary file
            temp_filepath = os.path.join(self.local_backup_dir, filename)
            logger.info(f"Saving model to temporary file: {temp_filepath}")
            
            # Save model with feature names and encoders
            model_data = {
                'model': model.model,
                'feature_names': model.feature_names,
                'label_encoders': model.label_encoders
            }
            joblib.dump(model_data, temp_filepath)
            
            # Save feature importance separately as JSON
            if hasattr(model, 'get_feature_importance'):
                feature_importance = model.get_feature_importance()
                feature_importance_path = temp_filepath.replace('.pkl', '_feature_importance.json')
                feature_importance.to_json(feature_importance_path, orient='records')
            
            # First try to save to Google Drive
            if self.service is not None:
                try:
                    logger.info(f"Saving model to Google Drive as {filename}")
                    file_metadata = {
                        'name': filename,
                        'parents': [self.folder_id]
                    }
                    
                    media = MediaFileUpload(
                        temp_filepath,
                        mimetype='application/octet-stream',
                        resumable=True
                    )
                    
                    file = self.service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    logger.info(f"Model saved to Google Drive with ID: {file.get('id')}")
                    return file.get('id')
                except Exception as e:
                    logger.error(f"Error saving model to Google Drive: {str(e)}")
                    logger.info("Using local storage as fallback")
            
            # If Google Drive failed or is not available, return the local path
            logger.info(f"Model saved successfully to local storage: {temp_filepath}")
            return temp_filepath
            
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise
    
    def load_model(self, file_id=None):
        """
        Load a model from Google Drive or local storage.
        
        Args:
            file_id (str, optional): The ID of the file in Google Drive or local path.
                If None, loads the latest model.
                
        Returns:
            The loaded model.
        """
        try:
            # Check if file_id is a local path
            if file_id and os.path.exists(file_id):
                logger.info(f"Loading model from local storage: {file_id}")
                model_data = joblib.load(file_id)
                return model_data
            
            # If not a local path, try Google Drive
            if self.service is None:
                logger.error("Google Drive service not initialized")
                raise ValueError("Google Drive service not initialized")
            
            if file_id is None:
                # Find the latest model file
                results = self.service.files().list(
                    q=f"'{self.folder_id}' in parents and mimeType='application/octet-stream' and name contains '.pkl'",
                    fields="files(id, name, createdTime)"
                ).execute()
                
                files = results.get('files', [])
                if not files:
                    logger.error("No model files found in Google Drive")
                    raise FileNotFoundError("No model files found in Google Drive")
                
                # Sort by creation time (newest first)
                files.sort(key=lambda x: x['createdTime'], reverse=True)
                file_id = files[0]['id']
                logger.info(f"Loading latest model file: {files[0]['name']}")
            
            # Download the file to a temporary location
            temp_filepath = os.path.join(self.local_backup_dir, f"temp_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")
            request = self.service.files().get_media(fileId=file_id)
            
            with open(temp_filepath, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    logger.info(f"Download {int(status.progress() * 100)}%.")
            
            # Load the model
            model_data = joblib.load(temp_filepath)
            
            # Clean up temporary file
            os.remove(temp_filepath)
            
            logger.info("Model loaded successfully from Google Drive")
            return model_data
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            # Try to load from local backup if available
            local_models = [f for f in os.listdir(self.local_backup_dir) if f.endswith('.pkl')]
            if local_models:
                # Sort by filename (which includes timestamp)
                local_models.sort(reverse=True)
                fallback_path = os.path.join(self.local_backup_dir, local_models[0])
                logger.info(f"Attempting to load from local backup: {fallback_path}")
                try:
                    model_data = joblib.load(fallback_path)
                    return model_data
                except Exception as e2:
                    logger.error(f"Failed to load from local backup: {str(e2)}")
            
            raise 