#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV Utilities Module

This module provides utilities for logging DataFrames to CSV files.
"""

import os
import pandas as pd
import datetime
import logging
import yaml
import sys
from pathlib import Path

logger = logging.getLogger('GFAnalytics.CSVUtils')

class DataFrameLogger:
    """
    Class for logging DataFrames to CSV files.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the DataFrameLogger.
        
        Args:
            config_path (str, optional): Path to the configuration file.
                If None, will look for a default configuration.
        """
        self.config = self._load_config(config_path)
        self.output_dir = self._ensure_output_dir()
        logger.info(f"DataFrameLogger initialized. Output directory: {self.output_dir}")
    
    def _load_config(self, config_path):
        """
        Load configuration from a YAML file.
        
        Args:
            config_path (str, optional): Path to the configuration file.
            
        Returns:
            dict: Configuration dictionary.
        """
        # Default configuration
        default_config = {
            'csv_logging': {
                'enabled': True,
                'output_dir': 'csv_logs',
                'include_timestamp': True,
                'timestamp_format': '%Y%m%d_%H%M%S',
                'max_rows': 1000,  # Maximum rows to log, 0 for unlimited
                'index': True,     # Whether to include index in CSV
                'compression': None, # Compression to use (None, 'gzip', 'bz2', 'zip', 'xz')
                'float_format': '%.6g', # Format for floating point numbers
                'encoding': 'utf-8'
            }
        }
        
        # Try to load the config file
        if config_path is not None:
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                
                # Update the default config with user config
                if 'csv_logging' in user_config:
                    default_config['csv_logging'].update(user_config['csv_logging'])
                logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
                logger.info("Using default configuration")
        
        return default_config['csv_logging']
    
    def _ensure_output_dir(self):
        """
        Ensure the output directory exists.
        
        Returns:
            str: Path to the output directory.
        """
        output_dir = self.config['output_dir']
        
        # Check if it's a relative or absolute path
        if not os.path.isabs(output_dir):
            # For relative paths, try to create relative to:
            # 1. Current working directory
            # 2. Project root directory (if we can find it)
            
            # Try to find project root (look for GFAnalytics directory)
            project_root = None
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Navigate up the directory tree looking for the project root
            while current_dir != os.path.dirname(current_dir):  # Stop at the root directory
                if os.path.basename(current_dir) == 'GFAnalytics' or os.path.exists(os.path.join(current_dir, 'GFAnalytics')):
                    project_root = current_dir
                    break
                current_dir = os.path.dirname(current_dir)
            
            if project_root:
                output_dir = os.path.join(project_root, output_dir)
            else:
                # Use current working directory if we can't find the project root
                output_dir = os.path.join(os.getcwd(), output_dir)
        
        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def log_df(self, df, name, **kwargs):
        """
        Log a DataFrame to a CSV file.
        
        Args:
            df (pandas.DataFrame): The DataFrame to log.
            name (str): Name for the CSV file.
            **kwargs: Additional arguments to pass to DataFrame.to_csv()
            
        Returns:
            str: Path to the saved CSV file.
        """
        if not self.config['enabled']:
            logger.info(f"DataFrame logging is disabled. Not logging '{name}'")
            return None
        
        # Apply row limit if configured
        if self.config['max_rows'] > 0 and len(df) > self.config['max_rows']:
            logger.info(f"Limiting '{name}' to {self.config['max_rows']} rows (from {len(df)})")
            df_to_save = df.head(self.config['max_rows'])
        else:
            df_to_save = df
        
        # Create filename
        filename = name
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # Add timestamp if configured
        if self.config['include_timestamp']:
            timestamp = datetime.datetime.now().strftime(self.config['timestamp_format'])
            filename = f"{timestamp}_{filename}"
        
        # Full path
        filepath = os.path.join(self.output_dir, filename)
        
        # Set default CSV options from config
        csv_options = {
            'index': self.config['index'],
            'float_format': self.config['float_format'],
            'encoding': self.config['encoding']
        }
        
        # Add compression if specified
        if self.config['compression']:
            csv_options['compression'] = self.config['compression']
        
        # Override with any user-provided options
        csv_options.update(kwargs)
        
        # Save to CSV
        try:
            df_to_save.to_csv(filepath, **csv_options)
            logger.info(f"DataFrame '{name}' saved to {filepath} ({len(df_to_save)} rows, {len(df_to_save.columns)} columns)")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save DataFrame '{name}' to {filepath}: {str(e)}")
            return None

# Global instance for easy access
_df_logger = None

def get_logger(config_path=None):
    """
    Get or create a global DataFrameLogger instance.
    
    Args:
        config_path (str, optional): Path to configuration file.
        
    Returns:
        DataFrameLogger: DataFrameLogger instance.
    """
    global _df_logger
    if _df_logger is None:
        _df_logger = DataFrameLogger(config_path)
    return _df_logger

def logdf(df, name, config_path=None, **kwargs):
    """
    Log a DataFrame to a CSV file using a global logger instance.
    
    Args:
        df (pandas.DataFrame): The DataFrame to log.
        name (str): Name for the CSV file.
        config_path (str, optional): Path to configuration file.
        **kwargs: Additional arguments to pass to DataFrame.to_csv()
        
    Returns:
        str: Path to the saved CSV file.
    """
    logger_instance = get_logger(config_path)
    return logger_instance.log_df(df, name, **kwargs)

def configure(config_path):
    """
    Configure the global logger instance with a specific configuration.
    
    Args:
        config_path (str): Path to configuration file.
        
    Returns:
        DataFrameLogger: Configured DataFrameLogger instance.
    """
    global _df_logger
    _df_logger = DataFrameLogger(config_path)
    return _df_logger 