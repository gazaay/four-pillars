#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Storage Module for GFAnalytics

This module provides functionality to store data in BigQuery,
with functions to create tables and store different types of data.
"""

import logging
import pandas as pd
from google.cloud import bigquery
import uuid
from datetime import datetime
import pytz

# Import utilities
from GFAnalytics.utils.gcp_utils import (
    get_bigquery_client,
    create_bigquery_dataset,
    create_bigquery_table
)

# Set up logger
logger = logging.getLogger('GFAnalytics.data_storage')


class BigQueryStorage:
    """
    Class for storing data in BigQuery.
    """
    
    def __init__(self, config):
        """
        Initialize the BigQueryStorage.
        
        Args:
            config (dict): Configuration dictionary.
        """
        self.config = config
        self.project_id = config['gcp']['project_id']
        self.dataset_id = config['gcp']['bigquery']['dataset']
        self.tables = config['gcp']['bigquery']['tables']
        self.current_batch_id = None
        
        # Initialize BigQuery client
        self.client = get_bigquery_client(self.project_id)
        
        # Create dataset if it doesn't exist
        self._create_dataset()
        
        # Create tables if they don't exist
        self._create_tables()
        
        logger.info(f"BigQueryStorage initialized for project {self.project_id}, dataset {self.dataset_id}")
    
    def _create_dataset(self):
        """Create the dataset if it doesn't exist."""
        try:
            create_bigquery_dataset(self.dataset_id, self.project_id)
            logger.info(f"Dataset {self.dataset_id} created or already exists")
        except Exception as e:
            logger.error(f"Failed to create dataset {self.dataset_id}: {str(e)}")
            raise
    
    def _create_tables(self):
        """Create tables if they don't exist."""
        try:
            # Create stock data table
            stock_data_schema = [
                bigquery.SchemaField("time", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("Open", "FLOAT64"),
                bigquery.SchemaField("High", "FLOAT64"),
                bigquery.SchemaField("Low", "FLOAT64"),
                bigquery.SchemaField("Close", "FLOAT64"),
                bigquery.SchemaField("Volume", "INTEGER"),
                bigquery.SchemaField("stock_code", "STRING"),
                bigquery.SchemaField("ric_code", "STRING"),
                bigquery.SchemaField("uuid", "STRING"),
                bigquery.SchemaField("batch_id", "STRING"),
                bigquery.SchemaField("last_modified_date", "TIMESTAMP")
            ]
            create_bigquery_table(self.dataset_id, self.tables['stock_data'], stock_data_schema, self.project_id)
            
            # Create Bazi data table
            bazi_data_schema = [
                bigquery.SchemaField("time", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("stock_code", "STRING"),
                # Base pillars
                bigquery.SchemaField("base_year_pillar", "STRING"),
                bigquery.SchemaField("base_month_pillar", "STRING"),
                bigquery.SchemaField("base_day_pillar", "STRING"),
                bigquery.SchemaField("base_hour_pillar", "STRING"),
                bigquery.SchemaField("base_month_pillar_minus", "STRING"),
                bigquery.SchemaField("base_hour_pillar_minus", "STRING"),
                bigquery.SchemaField("base_year_pillar_minus", "STRING"),
                bigquery.SchemaField("base_day_pillar_minus", "STRING"),
                bigquery.SchemaField("base_current_daiyun", "STRING"),
                bigquery.SchemaField("base_current_siyun", "STRING"),
                # Current pillars
                bigquery.SchemaField("current_year_pillar", "STRING"),
                bigquery.SchemaField("current_month_pillar", "STRING"),
                bigquery.SchemaField("current_day_pillar", "STRING"),
                bigquery.SchemaField("current_hour_pillar", "STRING"),
                bigquery.SchemaField("current_year_pillar_minus", "STRING"),
                bigquery.SchemaField("current_month_pillar_minus", "STRING"),
                bigquery.SchemaField("current_day_pillar_minus", "STRING"),
                bigquery.SchemaField("current_hour_pillar_minus", "STRING"),
                bigquery.SchemaField("current_daiyun", "STRING"),
                bigquery.SchemaField("current_siyun", "STRING"),
                # Wuxi fields
                bigquery.SchemaField("current_wuxi_hour", "STRING"),
                bigquery.SchemaField("current_wuxi_day", "STRING"),
                bigquery.SchemaField("current_wuxi_month", "STRING"),
                bigquery.SchemaField("current_wuxi_year", "STRING"),
                # Metadata fields
                bigquery.SchemaField("uuid", "STRING"),
                bigquery.SchemaField("batch_id", "STRING"),
                bigquery.SchemaField("last_modified_date", "TIMESTAMP")
            ]
            create_bigquery_table(self.dataset_id, self.tables['bazi_data'], bazi_data_schema, self.project_id)
            
            # Create training data table
            training_data_schema = [
                bigquery.SchemaField("time", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("stock_code", "STRING"),
                bigquery.SchemaField("Open", "FLOAT64"),
                bigquery.SchemaField("High", "FLOAT64"),
                bigquery.SchemaField("Low", "FLOAT64"),
                bigquery.SchemaField("Close", "FLOAT64"),
                bigquery.SchemaField("Volume", "INTEGER"),
                # Add ChengShen features
                bigquery.SchemaField("cs_base_hour_current_hour", "STRING"),
                bigquery.SchemaField("cs_base_hour_current_day", "STRING"),
                bigquery.SchemaField("cs_base_hour_current_month", "STRING"),
                bigquery.SchemaField("cs_base_hour_current_year", "STRING"),
                bigquery.SchemaField("cs_base_day_current_hour", "STRING"),
                bigquery.SchemaField("cs_base_day_current_day", "STRING"),
                bigquery.SchemaField("cs_base_day_current_month", "STRING"),
                bigquery.SchemaField("cs_base_day_current_year", "STRING"),
                bigquery.SchemaField("cs_base_month_current_hour", "STRING"),
                bigquery.SchemaField("cs_base_month_current_day", "STRING"),
                bigquery.SchemaField("cs_base_month_current_month", "STRING"),
                bigquery.SchemaField("cs_base_month_current_year", "STRING"),
                bigquery.SchemaField("cs_base_year_current_hour", "STRING"),
                bigquery.SchemaField("cs_base_year_current_day", "STRING"),
                bigquery.SchemaField("cs_base_year_current_month", "STRING"),
                bigquery.SchemaField("cs_base_year_current_year", "STRING"),
                # Add encoded features
                bigquery.SchemaField("encoded_cs_base_hour_current_hour", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_hour_current_day", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_hour_current_month", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_hour_current_year", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_day_current_hour", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_day_current_day", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_day_current_month", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_day_current_year", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_month_current_hour", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_month_current_day", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_month_current_month", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_month_current_year", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_year_current_hour", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_year_current_day", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_year_current_month", "INTEGER"),
                bigquery.SchemaField("encoded_cs_base_year_current_year", "INTEGER"),
                # Add target variable
                bigquery.SchemaField("target", "FLOAT64"),
                bigquery.SchemaField("uuid", "STRING"),
                bigquery.SchemaField("batch_id", "STRING"),
                bigquery.SchemaField("last_modified_date", "TIMESTAMP")
            ]
            create_bigquery_table(self.dataset_id, self.tables['training_data'], training_data_schema, self.project_id)
            
            # Create prediction data table
            prediction_data_schema = [
                bigquery.SchemaField("time", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("stock_code", "STRING"),
                bigquery.SchemaField("predicted_value", "FLOAT64"),
                bigquery.SchemaField("confidence", "FLOAT64"),
                bigquery.SchemaField("uuid", "STRING"),
                bigquery.SchemaField("batch_id", "STRING"),
                bigquery.SchemaField("last_modified_date", "TIMESTAMP")
            ]
            create_bigquery_table(self.dataset_id, self.tables['prediction_data'], prediction_data_schema, self.project_id)
            
            # Create model metrics table
            model_metrics_schema = [
                bigquery.SchemaField("model_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("stock_code", "STRING"),
                bigquery.SchemaField("training_start_date", "TIMESTAMP"),
                bigquery.SchemaField("training_end_date", "TIMESTAMP"),
                bigquery.SchemaField("mse", "FLOAT64"),
                bigquery.SchemaField("rmse", "FLOAT64"),
                bigquery.SchemaField("r2", "FLOAT64"),
                bigquery.SchemaField("medae", "FLOAT64"),
                bigquery.SchemaField("feature_importance", "STRING"),  # JSON string
                bigquery.SchemaField("uuid", "STRING"),
                bigquery.SchemaField("batch_id", "STRING"),
                bigquery.SchemaField("last_modified_date", "TIMESTAMP")
            ]
            create_bigquery_table(self.dataset_id, self.tables['model_metrics'], model_metrics_schema, self.project_id)
            
            # Create batch table
            batch_schema = [
                bigquery.SchemaField("batch_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("description", "STRING"),
                bigquery.SchemaField("stock_code", "STRING"),
                bigquery.SchemaField("start_date", "TIMESTAMP"),
                bigquery.SchemaField("end_date", "TIMESTAMP"),
                bigquery.SchemaField("status", "STRING"),  # e.g., 'in_progress', 'completed', 'failed'
                bigquery.SchemaField("created_at", "TIMESTAMP"),
                bigquery.SchemaField("completed_at", "TIMESTAMP"),
                # Batch process metadata
                bigquery.SchemaField("process_type", "STRING"),  # e.g., 'training', 'prediction', 'backtesting'
                bigquery.SchemaField("data_count", "INTEGER"),   # Number of records processed
                bigquery.SchemaField("error_count", "INTEGER"),  # Number of errors encountered
                # Batch parameters
                bigquery.SchemaField("parameters", "STRING"),    # JSON string of parameters used for this batch
                bigquery.SchemaField("bazi_features_used", "STRING"),  # Comma separated list of Bazi features used
                bigquery.SchemaField("model_parameters", "STRING"),    # JSON string of model parameters
                bigquery.SchemaField("technical_indicators_used", "STRING"),  # Indicators used for this batch
                # Identifiers
                bigquery.SchemaField("created_by", "STRING"),    # User or process that created the batch
                bigquery.SchemaField("uuid", "STRING")
            ]
            create_bigquery_table(self.dataset_id, self.tables['batch'], batch_schema, self.project_id)
            
            logger.info("All tables created or already exist")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
    
    def create_batch(self, description=None, parameters=None, process_type='default', created_by=None):
        """
        Create a new batch and return the batch_id.
        
        Args:
            description (str, optional): Description of the batch.
            parameters (dict, optional): Parameters used for this batch.
            process_type (str, optional): Type of process (e.g., 'training', 'prediction', 'backtesting').
            created_by (str, optional): User or process that created the batch.
            
        Returns:
            str: The batch ID.
        """
        try:
            # Generate a new UUID for the batch
            batch_id = str(uuid.uuid4())
            self.current_batch_id = batch_id
            
            # Extract specific parameters for structured storage
            bazi_features_used = ""
            technical_indicators_used = ""
            model_parameters = ""
            
            if parameters:
                # Extract Bazi features if available
                if 'features' in parameters and 'use_bazi' in parameters['features']:
                    bazi_features_used = "base_pillars,current_pillars"
                    if 'use_chengshen' in parameters['features'] and parameters['features']['use_chengshen']:
                        bazi_features_used += ",chengshen"
                    if 'use_wuxi' in parameters['features'] and parameters['features']['use_wuxi']:
                        bazi_features_used += ",wuxi"
                
                # Extract technical indicators if available
                if 'features' in parameters and 'technical_indicators' in parameters['features']:
                    if isinstance(parameters['features']['technical_indicators'], list):
                        technical_indicators_used = ",".join(parameters['features']['technical_indicators'])
                    else:
                        technical_indicators_used = str(parameters['features']['technical_indicators'])
                
                # Extract model parameters if available
                if 'model' in parameters and 'params' in parameters['model']:
                    model_parameters = str(parameters['model']['params'])
            
            # Create a record for the batch table
            batch_record = {
                'batch_id': batch_id,
                'description': description,
                'stock_code': self.config['stock']['code'],
                'start_date': datetime.now(pytz.timezone('Asia/Hong_Kong')),
                'end_date': None,
                'status': 'in_progress',
                'created_at': datetime.now(pytz.timezone('Asia/Hong_Kong')),
                'completed_at': None,
                # Batch process metadata
                'process_type': process_type,
                'data_count': 0,  # Will be updated when batch is completed
                'error_count': 0, # Will be updated when batch is completed
                # Batch parameters
                'parameters': str(parameters) if parameters else None,
                'bazi_features_used': bazi_features_used,
                'model_parameters': model_parameters,
                'technical_indicators_used': technical_indicators_used,
                # Identifiers
                'created_by': created_by or 'system',
                'uuid': str(uuid.uuid4())
            }
            
            # Get the table reference
            table_ref = self.client.dataset(self.dataset_id).table(self.tables['batch'])
            
            # Insert the batch record
            errors = self.client.insert_rows_json(table_ref, [batch_record])
            
            if errors:
                logger.error(f"Errors occurred while creating batch record: {errors}")
                return None
            
            logger.info(f"Created new batch with ID: {batch_id}")
            return batch_id
        except Exception as e:
            logger.error(f"Failed to create batch: {str(e)}")
            return None
    
    def complete_batch(self, batch_id=None, status='completed', data_count=None, error_count=0):
        """
        Mark a batch as completed.
        
        Args:
            batch_id (str, optional): The batch ID to complete. If None, uses the current batch ID.
            status (str, optional): The status to set. Default is 'completed'.
            data_count (int, optional): The number of records processed. If None, will be calculated.
            error_count (int, optional): The number of errors encountered.
            
        Returns:
            bool: True if the batch was completed successfully, False otherwise.
        """
        try:
            # Use the provided batch_id or the current one
            batch_id = batch_id or self.current_batch_id
            
            if not batch_id:
                logger.error("No batch ID provided or set")
                return False
            
            # If data_count is not provided, try to calculate it
            if data_count is None:
                try:
                    # Count records in tables with this batch_id
                    data_count = 0
                    for table_name in ['stock_data', 'bazi_data', 'training_data', 'prediction_data']:
                        table_id = f"{self.project_id}.{self.dataset_id}.{self.tables[table_name]}"
                        query = f"""
                        SELECT COUNT(*) as count
                        FROM `{table_id}`
                        WHERE batch_id = '{batch_id}'
                        """
                        query_job = self.client.query(query)
                        results = list(query_job.result())
                        if results:
                            data_count += results[0]['count']
                except Exception as e:
                    logger.warning(f"Failed to calculate data count for batch {batch_id}: {str(e)}")
                    data_count = 0
            
            # Construct the update query
            query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.{self.tables['batch']}`
            SET end_date = CURRENT_TIMESTAMP(),
                completed_at = CURRENT_TIMESTAMP(),
                status = '{status}',
                data_count = {data_count},
                error_count = {error_count}
            WHERE batch_id = '{batch_id}'
            """
            
            # Execute the query
            query_job = self.client.query(query)
            query_job.result()  # Wait for the query to complete
            
            logger.info(f"Batch {batch_id} marked as {status} with {data_count} records and {error_count} errors")
            
            # Reset current_batch_id if it was the one completed
            if batch_id == self.current_batch_id:
                self.current_batch_id = None
                
            return True
        except Exception as e:
            logger.error(f"Failed to complete batch {batch_id}: {str(e)}")
            return False
    
    def store_stock_data(self, data):
        """
        Store stock data in BigQuery.
        
        Args:
            data (pandas.DataFrame): The stock data to store.
            
        Returns:
            bool: True if the data was stored successfully, False otherwise.
        """
        try:
            # Make a copy of the data to avoid modifying the original
            df = data.copy()
            
            # Ensure the data has the required columns
            required_columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'stock_code', 'ric_code']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'stock_code':
                        df[col] = self.config['stock']['code']
                    elif col == 'ric_code':
                        df[col] = self.config['stock']['ric_code']
                    else:
                        df[col] = None
            
            # Add UUID and last_modified_date if they don't exist
            if 'uuid' not in df.columns:
                df['uuid'] = [str(uuid.uuid4()) for _ in range(len(df))]
            
            if 'last_modified_date' not in df.columns:
                df['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
            
            # Add batch_id if it doesn't exist
            if 'batch_id' not in df.columns:
                df['batch_id'] = self.current_batch_id
            
            # Convert the DataFrame to a list of dictionaries
            rows_to_insert = df.to_dict('records')
            
            # Get the table reference
            table_ref = self.client.dataset(self.dataset_id).table(self.tables['stock_data'])
            
            # Insert the rows
            errors = self.client.insert_rows_json(table_ref, rows_to_insert)
            
            if errors:
                logger.error(f"Errors occurred while inserting stock data: {errors}")
                return False
            
            logger.debug(f"Successfully stored {len(df)} stock data records")
            return True
        except Exception as e:
            logger.error(f"Failed to store stock data: {str(e)}")
            return False
    
    def store_bazi_data(self, data):
        """
        Store Bazi data in BigQuery.
        
        Args:
            data (pandas.DataFrame): The Bazi data to store.
            
        Returns:
            bool: True if the data was stored successfully, False otherwise.
        """
        try:
            # Make a copy of the data to avoid modifying the original
            df = data.copy()
            
            # Define all expected columns
            columns = [
                'time', 'stock_code',
                # Base pillars
                'base_year_pillar', 'base_month_pillar', 'base_day_pillar', 'base_hour_pillar',
                'base_month_pillar_minus', 'base_hour_pillar_minus', 'base_year_pillar_minus', 'base_day_pillar_minus',
                'base_current_daiyun', 'base_current_siyun',
                # Current pillars
                'current_year_pillar', 'current_month_pillar', 'current_day_pillar', 'current_hour_pillar',
                'current_year_pillar_minus', 'current_month_pillar_minus', 'current_day_pillar_minus', 'current_hour_pillar_minus',
                'current_daiyun', 'current_siyun',
                # Wuxi fields
                'current_wuxi_hour', 'current_wuxi_day', 'current_wuxi_month', 'current_wuxi_year',
                # Metadata
                'uuid', 'last_modified_date'
            ]
            
            # Ensure the data has the required columns
            for col in columns:
                if col not in df.columns:
                    if col == 'stock_code':
                        df[col] = self.config['stock']['code']
                    elif col == 'uuid':
                        df[col] = [str(uuid.uuid4()) for _ in range(len(df))]
                    elif col == 'last_modified_date':
                        df[col] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
                    else:
                        df[col] = None
            
            # Add batch_id if it doesn't exist
            if 'batch_id' not in df.columns:
                df['batch_id'] = self.current_batch_id
                columns.append('batch_id')
            
            # Select only the columns we need
            df = df[columns]
            
            # Convert timestamp columns to string format if they are datetime objects
            if isinstance(df['time'].iloc[0], datetime):
                df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            if isinstance(df['last_modified_date'].iloc[0], datetime):
                df['last_modified_date'] = df['last_modified_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert the DataFrame to a list of dictionaries
            rows_to_insert = df.to_dict('records')
            
            # Get the table reference
            table_ref = self.client.dataset(self.dataset_id).table(self.tables['bazi_data'])
            
            # Insert the rows
            errors = self.client.insert_rows_json(table_ref, rows_to_insert)
            
            if errors:
                logger.error(f"Errors occurred while inserting Bazi data: {errors}")
                return False
            
            logger.info(f"Successfully stored {len(df)} Bazi data records")
            return True
        except Exception as e:
            logger.error(f"Failed to store Bazi data: {str(e)}")
            return False
    
    def store_training_data(self, data):
        """
        Store training data in BigQuery.
        
        Args:
            data (pandas.DataFrame): The training data to store.
            
        Returns:
            bool: True if the data was stored successfully, False otherwise.
        """
        try:
            # Make a copy of the data to avoid modifying the original
            df = data.copy()
            
            # Add UUID and last_modified_date if they don't exist
            if 'uuid' not in df.columns:
                df['uuid'] = [str(uuid.uuid4()) for _ in range(len(df))]
            
            if 'last_modified_date' not in df.columns:
                df['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
            
            # Add batch_id if it doesn't exist
            if 'batch_id' not in df.columns:
                df['batch_id'] = self.current_batch_id
            
            # Convert the DataFrame to a list of dictionaries
            rows_to_insert = df.to_dict('records')
            
            # Get the table reference
            table_ref = self.client.dataset(self.dataset_id).table(self.tables['training_data'])
            
            # Insert the rows
            errors = self.client.insert_rows_json(table_ref, rows_to_insert)
            
            if errors:
                logger.error(f"Errors occurred while inserting training data: {errors}")
                return False
            
            logger.info(f"Successfully stored {len(df)} training data records")
            return True
        except Exception as e:
            logger.error(f"Failed to store training data: {str(e)}")
            return False
    
    def store_prediction_data(self, data):
        """
        Store prediction data in BigQuery.
        
        Args:
            data (pandas.DataFrame): The prediction data to store.
            
        Returns:
            bool: True if the data was stored successfully, False otherwise.
        """
        try:
            # Make a copy of the data to avoid modifying the original
            df = data.copy()
            
            # Ensure the data has the required columns
            required_columns = ['time', 'stock_code', 'predicted_value', 'confidence']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'stock_code':
                        df[col] = self.config['stock']['code']
                    else:
                        df[col] = None
            
            # Add UUID and last_modified_date if they don't exist
            if 'uuid' not in df.columns:
                df['uuid'] = [str(uuid.uuid4()) for _ in range(len(df))]
            
            if 'last_modified_date' not in df.columns:
                df['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
            
            # Add batch_id if it doesn't exist
            if 'batch_id' not in df.columns:
                df['batch_id'] = self.current_batch_id
            
            # Convert the DataFrame to a list of dictionaries
            rows_to_insert = df.to_dict('records')
            
            # Get the table reference
            table_ref = self.client.dataset(self.dataset_id).table(self.tables['prediction_data'])
            
            # Insert the rows
            errors = self.client.insert_rows_json(table_ref, rows_to_insert)
            
            if errors:
                logger.error(f"Errors occurred while inserting prediction data: {errors}")
                return False
            
            logger.info(f"Successfully stored {len(df)} prediction data records")
            return True
        except Exception as e:
            logger.error(f"Failed to store prediction data: {str(e)}")
            return False
    
    def store_model_metrics(self, metrics):
        """
        Store model metrics in BigQuery.
        
        Args:
            metrics (dict): The model metrics to store.
            
        Returns:
            bool: True if the metrics were stored successfully, False otherwise.
        """
        try:
            # Create a DataFrame with the metrics
            df = pd.DataFrame([metrics])
            
            # Ensure the data has the required columns
            required_columns = [
                'model_id', 'stock_code', 'training_start_date', 'training_end_date',
                'mse', 'rmse', 'r2', 'medae', 'feature_importance'
            ]
            for col in required_columns:
                if col not in df.columns:
                    if col == 'stock_code':
                        df[col] = self.config['stock']['code']
                    elif col == 'model_id':
                        df[col] = str(uuid.uuid4())
                    else:
                        df[col] = None
            
            # Add UUID and last_modified_date if they don't exist
            if 'uuid' not in df.columns:
                df['uuid'] = [str(uuid.uuid4()) for _ in range(len(df))]
            
            if 'last_modified_date' not in df.columns:
                df['last_modified_date'] = datetime.now(pytz.timezone('Asia/Hong_Kong'))
            
            # Add batch_id if it doesn't exist
            if 'batch_id' not in df.columns:
                df['batch_id'] = self.current_batch_id
            
            # Convert the DataFrame to a list of dictionaries
            rows_to_insert = df.to_dict('records')
            
            # Get the table reference
            table_ref = self.client.dataset(self.dataset_id).table(self.tables['model_metrics'])
            
            # Insert the rows
            errors = self.client.insert_rows_json(table_ref, rows_to_insert)
            
            if errors:
                logger.error(f"Errors occurred while inserting model metrics: {errors}")
                return False
            
            logger.info("Successfully stored model metrics")
            return True
        except Exception as e:
            logger.error(f"Failed to store model metrics: {str(e)}")
            return False
    
    def store_stock_metadata(self):
        """Store stock metadata including listing date."""
        schema = [
            bigquery.SchemaField("stock_code", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("ric_code", "STRING"),
            bigquery.SchemaField("listing_date", "DATE"),
            bigquery.SchemaField("last_modified_date", "TIMESTAMP")
        ]
        
        data = {
            'stock_code': self.config['stock']['code'],
            'ric_code': self.config['stock']['ric_code'],
            'listing_date': self.stock_loader.get_listing_date(),
            'last_modified_date': datetime.now(pytz.timezone('Asia/Hong_Kong'))
        }
        
        table_id = f"{self.project_id}.{self.dataset_id}.stock_metadata"
        
        # Create or update table
        self._create_table_if_not_exists(table_id, schema)
        self._store_data(table_id, [data])

    def clean_table(self, table_name):
        """
        Clean (delete all data) from a specific table.
        
        Args:
            table_name (str): Name of the table to clean
        """
        try:
            # Instead of DELETE, we'll recreate the table
            table_id = f"{self.project_id}.{self.dataset_id}.{self.tables[table_name]}"
            table = self.client.get_table(table_id)
            
            # Store the schema
            schema = table.schema
            
            # Delete the table
            self.client.delete_table(table_id)
            logger.info(f"Deleted table: {table_name}")
            
            # Recreate the table with same schema
            table = bigquery.Table(table_id, schema=schema)
            self.client.create_table(table)
            logger.info(f"Recreated table: {table_name}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to clean table {table_name}: {str(e)}")
            return False

    def clean_all_tables(self):
        """Clean all tables in the dataset."""
        try:
            for table_name in self.tables.keys():
                self.clean_table(table_name)
            logger.info("Successfully cleaned all tables")
            return True
        except Exception as e:
            logger.error(f"Failed to clean all tables: {str(e)}")
            return False
    
    def get_batch_info(self, batch_id=None):
        """
        Get information about a specific batch.
        
        Args:
            batch_id (str, optional): The batch ID to get information about. If None, uses the current batch ID.
            
        Returns:
            dict: The batch information.
        """
        try:
            # Use the provided batch_id or the current one
            batch_id = batch_id or self.current_batch_id
            
            if not batch_id:
                logger.error("No batch ID provided or set")
                return None
            
            # Construct the query
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.{self.tables['batch']}`
            WHERE batch_id = '{batch_id}'
            """
            
            # Execute the query
            query_job = self.client.query(query)
            results = list(query_job.result())
            
            if not results:
                logger.error(f"Batch {batch_id} not found")
                return None
            
            # Convert to dictionary
            batch_info = dict(results[0].items())
            logger.info(f"Retrieved information for batch {batch_id}")
            
            return batch_info
        except Exception as e:
            logger.error(f"Failed to get batch info for {batch_id}: {str(e)}")
            return None

    def update_batch_info(self, batch_id=None, **kwargs):
        """
        Update information for a specific batch.
        
        Args:
            batch_id (str, optional): The batch ID to update. If None, uses the current batch ID.
            **kwargs: Key-value pairs to update in the batch record.
            
        Returns:
            bool: True if the batch was updated successfully, False otherwise.
        """
        try:
            # Use the provided batch_id or the current one
            batch_id = batch_id or self.current_batch_id
            
            if not batch_id:
                logger.error("No batch ID provided or set")
                return False
            
            # Validate that the batch exists
            batch_info = self.get_batch_info(batch_id)
            if not batch_info:
                logger.error(f"Batch {batch_id} not found")
                return False
            
            # Construct the SET clause of the update query
            set_clauses = []
            for key, value in kwargs.items():
                # Skip invalid columns or batch_id which shouldn't be updated
                if key == 'batch_id' or key not in batch_info.keys():
                    continue
                
                # Format the value based on its type
                if value is None:
                    set_clauses.append(f"{key} = NULL")
                elif isinstance(value, (int, float)):
                    set_clauses.append(f"{key} = {value}")
                elif isinstance(value, bool):
                    set_clauses.append(f"{key} = {str(value).lower()}")
                else:
                    # Escape single quotes in string values
                    value_str = str(value).replace("'", "''")
                    set_clauses.append(f"{key} = '{value_str}'")
            
            # If no valid updates, return early
            if not set_clauses:
                logger.warning(f"No valid updates for batch {batch_id}")
                return True
            
            # Construct the update query
            query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.{self.tables['batch']}`
            SET {', '.join(set_clauses)}
            WHERE batch_id = '{batch_id}'
            """
            
            # Execute the query
            query_job = self.client.query(query)
            query_job.result()  # Wait for the query to complete
            
            logger.info(f"Batch {batch_id} updated with {len(set_clauses)} field(s)")
            return True
        except Exception as e:
            logger.error(f"Failed to update batch {batch_id}: {str(e)}")
            return False
            
    def get_batches_by_status(self, status):
        """
        Get a list of batches with a specific status.
        
        Args:
            status (str): The status to filter by (e.g., 'in_progress', 'completed', 'failed').
            
        Returns:
            list: A list of batch information dictionaries.
        """
        try:
            # Construct the query
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.{self.tables['batch']}`
            WHERE status = '{status}'
            ORDER BY created_at DESC
            """
            
            # Execute the query
            query_job = self.client.query(query)
            results = list(query_job.result())
            
            # Convert to list of dictionaries
            batches = [dict(row.items()) for row in results]
            logger.info(f"Retrieved {len(batches)} batches with status '{status}'")
            
            return batches
        except Exception as e:
            logger.error(f"Failed to get batches with status {status}: {str(e)}")
            return [] 