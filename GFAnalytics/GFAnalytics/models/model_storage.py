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

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError


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
        self.logger = logging.getLogger('GFAnalytics.GoogleDriveStorage')
        
        # Get Google Drive configuration
        self.folder_id = config['gcp']['gdrive']['folder_id']
        self.model_filename = config['gcp']['gdrive']['model_filename']
        
        # Initialize Google Drive API
        self.drive_service = self._initialize_drive_service()
    
    def _initialize_drive_service(self):
        """
        Initialize Google Drive API service.
        
        Returns:
            googleapiclient.discovery.Resource: Google Drive API service.
        """
        try:
            credentials_path = self.config['gcp']['credentials_path']
            
            # Create credentials from service account file
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Build the Drive API service
            drive_service = build('drive', 'v3', credentials=credentials)
            
            return drive_service
            
        except Exception as e:
            self.logger.error(f"Error initializing Google Drive service: {str(e)}")
            raise
    
    def save_model(self, model, filename=None):
        """
        Save a trained model to Google Drive.
        
        Args:
            model: Trained machine learning model.
            filename (str, optional): Filename to save the model as.
                                     If None, uses the configured filename.
        
        Returns:
            str: ID of the saved file in Google Drive.
        """
        if filename is None:
            filename = self.model_filename
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_with_timestamp = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        
        self.logger.info(f"Saving model to Google Drive as {filename_with_timestamp}")
        
        try:
            # Create a temporary file to store the model
            with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as temp_file:
                temp_filename = temp_file.name
                
                # Serialize the model to the temporary file
                pickle.dump(model, temp_file)
            
            # Upload the file to Google Drive
            file_metadata = {
                'name': filename_with_timestamp,
                'parents': [self.folder_id]
            }
            
            media = MediaFileUpload(temp_filename, mimetype='application/octet-stream')
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            
            self.logger.info(f"Model saved successfully with ID: {file_id}")
            
            # Clean up the temporary file
            os.unlink(temp_filename)
            
            return file_id
            
        except Exception as e:
            self.logger.error(f"Error saving model to Google Drive: {str(e)}")
            raise
    
    def load_model(self, file_id=None):
        """
        Load a trained model from Google Drive.
        
        Args:
            file_id (str, optional): ID of the file to load.
                                    If None, loads the latest model.
        
        Returns:
            object: Loaded machine learning model.
        """
        self.logger.info("Loading model from Google Drive")
        
        try:
            # If file_id is not provided, find the latest model
            if file_id is None:
                file_id = self._find_latest_model()
            
            # Create a temporary file to download the model
            with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Download the file from Google Drive
            request = self.drive_service.files().get_media(fileId=file_id)
            
            with open(temp_filename, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            # Load the model from the temporary file
            with open(temp_filename, 'rb') as f:
                model = pickle.load(f)
            
            self.logger.info(f"Model loaded successfully from ID: {file_id}")
            
            # Clean up the temporary file
            os.unlink(temp_filename)
            
            return model
            
        except Exception as e:
            self.logger.error(f"Error loading model from Google Drive: {str(e)}")
            raise
    
    def _find_latest_model(self):
        """
        Find the latest model in Google Drive.
        
        Returns:
            str: ID of the latest model file.
        """
        try:
            # Search for model files in the folder
            query = f"'{self.folder_id}' in parents and trashed = false and mimeType = 'application/octet-stream'"
            
            response = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, createdTime)',
                orderBy='createdTime desc'
            ).execute()
            
            files = response.get('files', [])
            
            if not files:
                self.logger.error("No model files found in Google Drive")
                raise FileNotFoundError("No model files found in Google Drive")
            
            # Return the ID of the latest file
            latest_file = files[0]
            self.logger.info(f"Found latest model: {latest_file['name']}")
            
            return latest_file['id']
            
        except Exception as e:
            self.logger.error(f"Error finding latest model: {str(e)}")
            raise 