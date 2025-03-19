#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Cloud Platform Utilities for GFAnalytics

This module provides utility functions for interacting with Google Cloud Platform,
particularly focusing on authentication and credential setup for BigQuery and Google Drive.
"""

import os
import json
import logging
from google.oauth2 import service_account
from google.cloud import bigquery, storage
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# Set up logger
logger = logging.getLogger('GFAnalytics.gcp_utils')


def setup_gcp_credentials(credentials_path):
    """
    Set up Google Cloud Platform credentials.
    
    Args:
        credentials_path (str): Path to the service account credentials JSON file.
        
    Returns:
        bool: True if credentials were set up successfully, False otherwise.
    """
    try:
        # Check if the credentials file exists
        if not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found at {credentials_path}")
            return False
        
        # Set the environment variable for GCP authentication
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        logger.info(f"GCP credentials set up successfully from {credentials_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to set up GCP credentials: {str(e)}")
        return False


def get_bigquery_client(project_id=None):
    """
    Get a BigQuery client.
    
    Args:
        project_id (str, optional): The Google Cloud project ID. If None, uses the default project.
        
    Returns:
        google.cloud.bigquery.Client: A BigQuery client.
    """
    try:
        if project_id:
            client = bigquery.Client(project=project_id)
        else:
            client = bigquery.Client()
        
        logger.info(f"BigQuery client created for project {client.project}")
        return client
    except Exception as e:
        logger.error(f"Failed to create BigQuery client: {str(e)}")
        raise


def get_storage_client(project_id=None):
    """
    Get a Google Cloud Storage client.
    
    Args:
        project_id (str, optional): The Google Cloud project ID. If None, uses the default project.
        
    Returns:
        google.cloud.storage.Client: A Storage client.
    """
    try:
        if project_id:
            client = storage.Client(project=project_id)
        else:
            client = storage.Client()
        
        logger.info(f"Storage client created for project {client.project}")
        return client
    except Exception as e:
        logger.error(f"Failed to create Storage client: {str(e)}")
        raise


def get_drive_service(credentials_path=None):
    """
    Get a Google Drive API service.
    
    Args:
        credentials_path (str, optional): Path to the service account credentials JSON file.
            If None, uses the GOOGLE_APPLICATION_CREDENTIALS environment variable.
            
    Returns:
        googleapiclient.discovery.Resource: A Google Drive API service.
    """
    try:
        # Use the provided credentials path or the environment variable
        if credentials_path is None:
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        # Load credentials from the service account file
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Build the Drive API service
        service = build('drive', 'v3', credentials=credentials)
        
        logger.info("Google Drive API service created successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to create Google Drive API service: {str(e)}")
        raise


def upload_file_to_drive(file_path, folder_id, mime_type=None, service=None):
    """
    Upload a file to Google Drive.
    
    Args:
        file_path (str): Path to the file to upload.
        folder_id (str): ID of the folder to upload the file to.
        mime_type (str, optional): MIME type of the file. If None, it will be guessed.
        service (googleapiclient.discovery.Resource, optional): A Google Drive API service.
            If None, a new service will be created.
            
    Returns:
        str: The ID of the uploaded file.
    """
    try:
        # Create a Drive service if not provided
        if service is None:
            service = get_drive_service()
        
        # Get the file name from the path
        file_name = os.path.basename(file_path)
        
        # Create file metadata
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Create media
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        # Upload the file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        logger.info(f"File {file_name} uploaded to Google Drive with ID {file.get('id')}")
        return file.get('id')
    except Exception as e:
        logger.error(f"Failed to upload file to Google Drive: {str(e)}")
        raise


def download_file_from_drive(file_id, output_path, service=None):
    """
    Download a file from Google Drive.
    
    Args:
        file_id (str): ID of the file to download.
        output_path (str): Path where the file will be saved.
        service (googleapiclient.discovery.Resource, optional): A Google Drive API service.
            If None, a new service will be created.
            
    Returns:
        bool: True if the file was downloaded successfully, False otherwise.
    """
    try:
        # Create a Drive service if not provided
        if service is None:
            service = get_drive_service()
        
        # Get the file
        request = service.files().get_media(fileId=file_id)
        
        # Download the file
        with io.FileIO(output_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Download progress: {int(status.progress() * 100)}%")
        
        logger.info(f"File with ID {file_id} downloaded to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to download file from Google Drive: {str(e)}")
        return False


def create_bigquery_dataset(dataset_id, project_id=None, location='US'):
    """
    Create a BigQuery dataset if it doesn't exist.
    
    Args:
        dataset_id (str): The ID of the dataset to create.
        project_id (str, optional): The Google Cloud project ID. If None, uses the default project.
        location (str, optional): The location of the dataset. Default is 'US'.
        
    Returns:
        google.cloud.bigquery.Dataset: The created or existing dataset.
    """
    try:
        # Get a BigQuery client
        client = get_bigquery_client(project_id)
        
        # Construct the full dataset reference
        dataset_ref = client.dataset(dataset_id)
        
        # Try to get the dataset to check if it exists
        try:
            dataset = client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_id} already exists")
        except Exception:
            # Dataset doesn't exist, create it
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = location
            dataset = client.create_dataset(dataset)
            logger.info(f"Dataset {dataset_id} created in {location}")
        
        return dataset
    except Exception as e:
        logger.error(f"Failed to create BigQuery dataset: {str(e)}")
        raise


def create_bigquery_table(dataset_id, table_id, schema, project_id=None):
    """
    Create a BigQuery table if it doesn't exist.
    
    Args:
        dataset_id (str): The ID of the dataset containing the table.
        table_id (str): The ID of the table to create.
        schema (list): The schema of the table as a list of SchemaField objects.
        project_id (str, optional): The Google Cloud project ID. If None, uses the default project.
        
    Returns:
        google.cloud.bigquery.Table: The created or existing table.
    """
    try:
        # Get a BigQuery client
        client = get_bigquery_client(project_id)
        
        # Construct the full table reference
        table_ref = client.dataset(dataset_id).table(table_id)
        
        # Try to get the table to check if it exists
        try:
            table = client.get_table(table_ref)
            logger.info(f"Table {dataset_id}.{table_id} already exists")
        except Exception:
            # Table doesn't exist, create it
            table = bigquery.Table(table_ref, schema=schema)
            table = client.create_table(table)
            logger.info(f"Table {dataset_id}.{table_id} created")
        
        return table
    except Exception as e:
        logger.error(f"Failed to create BigQuery table: {str(e)}")
        raise 