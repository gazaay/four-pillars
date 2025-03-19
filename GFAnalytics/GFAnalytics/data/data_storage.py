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
                bigquery.SchemaField("last_modified_date", "TIMESTAMP")
            ]
            create_bigquery_table(self.dataset_id, self.tables['stock_data'], stock_data_schema, self.project_id)
            
            # Create Bazi data table
            bazi_data_schema = [
                bigquery.SchemaField("time", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("stock_code", "STRING"),
                bigquery.SchemaField("base_year_pillar", "STRING"),
                bigquery.SchemaField("base_month_pillar", "STRING"),
                bigquery.SchemaField("base_day_pillar", "STRING"),
                bigquery.SchemaField("base_hour_pillar", "STRING"),
                bigquery.SchemaField("base_month_pillar_minus", "STRING"),
                bigquery.SchemaField("base_hour_pillar_minus", "STRING"),
                bigquery.SchemaField("current_year_pillar", "STRING"),
                bigquery.SchemaField("current_month_pillar", "STRING"),
                bigquery.SchemaField("current_day_pillar", "STRING"),
                bigquery.SchemaField("current_hour_pillar", "STRING"),
                bigquery.SchemaField("current_month_pillar_minus", "STRING"),
                bigquery.SchemaField("current_hour_pillar_minus", "STRING"),
                bigquery.SchemaField("uuid", "STRING"),
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
                bigquery.SchemaField("last_modified_date", "TIMESTAMP")
            ]
            create_bigquery_table(self.dataset_id, self.tables['model_metrics'], model_metrics_schema, self.project_id)
            
            logger.info("All tables created or already exist")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
    
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
            
            # Convert the DataFrame to a list of dictionaries
            rows_to_insert = df.to_dict('records')
            
            # Get the table reference
            table_ref = self.client.dataset(self.dataset_id).table(self.tables['stock_data'])
            
            # Insert the rows
            errors = self.client.insert_rows_json(table_ref, rows_to_insert)
            
            if errors:
                logger.error(f"Errors occurred while inserting stock data: {errors}")
                return False
            
            logger.info(f"Successfully stored {len(df)} stock data records")
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
            
            # Select only the columns we need
            columns = [
                'time', 'stock_code',
                'base_year_pillar', 'base_month_pillar', 'base_day_pillar', 'base_hour_pillar',
                'base_month_pillar_minus', 'base_hour_pillar_minus',
                'current_year_pillar', 'current_month_pillar', 'current_day_pillar', 'current_hour_pillar',
                'current_month_pillar_minus', 'current_hour_pillar_minus',
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
            
            # Select only the columns we need
            df = df[columns]
            
            # Convert timestamp columns to string format
            df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
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