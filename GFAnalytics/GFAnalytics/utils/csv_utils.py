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
import glob

from GFAnalytics.utils.global_run_id import get_run_id

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
        self.run_id = get_run_id()
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
                'max_rows': 200000,  # Maximum rows to log, 0 for unlimited
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
        Ensure the output directory exists, organized by run_id.
        
        Returns:
            str: Path to the output directory.
        """
        base_output_dir = self.config['output_dir']
        
        # Check if it's a relative or absolute path
        if not os.path.isabs(base_output_dir):
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
                base_output_dir = os.path.join(project_root, base_output_dir)
            else:
                # Use current working directory if we can't find the project root
                base_output_dir = os.path.join(os.getcwd(), base_output_dir)
        
        # Create the run-specific directory using the run_id
        run_output_dir = os.path.join(base_output_dir, self.run_id)
        
        # Create the directory if it doesn't exist
        os.makedirs(run_output_dir, exist_ok=True)
        return run_output_dir
    
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

def get_base_output_dir(config_path=None):
    """
    Get the base output directory for CSV logs.
    
    Args:
        config_path (str, optional): Path to configuration file.
        
    Returns:
        str: Path to the base output directory.
    """
    # Use the same logic as in DataFrameLogger._load_config and _ensure_output_dir
    # but without creating a new instance
    
    # Default configuration
    default_config = {
        'csv_logging': {
            'output_dir': 'csv_logs',
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
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
    
    base_output_dir = default_config['csv_logging']['output_dir']
    
    # Check if it's a relative or absolute path
    if not os.path.isabs(base_output_dir):
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
            base_output_dir = os.path.join(project_root, base_output_dir)
        else:
            # Use current working directory if we can't find the project root
            base_output_dir = os.path.join(os.getcwd(), base_output_dir)
    
    return base_output_dir

def list_runs(config_path=None):
    """
    List all available run directories.
    
    Args:
        config_path (str, optional): Path to configuration file.
        
    Returns:
        pandas.DataFrame: DataFrame with run_id, timestamp, and logs_count information.
    """
    base_dir = get_base_output_dir(config_path)
    
    # Check if the directory exists
    if not os.path.exists(base_dir):
        logger.warning(f"Base output directory {base_dir} does not exist.")
        return pd.DataFrame(columns=['run_id', 'timestamp', 'logs_count'])
    
    # Get all subdirectories
    run_dirs = sorted([d for d in os.listdir(base_dir) 
                      if os.path.isdir(os.path.join(base_dir, d))], 
                      reverse=True)  # Sort newest first
    
    runs_data = []
    for run_id in run_dirs:
        try:
            # Extract timestamp from run_id (assuming format: YYYYMMDD_HHMMSS_uuid)
            timestamp_str = run_id.split('_')[0] + '_' + run_id.split('_')[1]
            timestamp = datetime.datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            
            # Count CSV files in the run directory
            run_path = os.path.join(base_dir, run_id)
            csv_files = glob.glob(os.path.join(run_path, '*.csv'))
            logs_count = len(csv_files)
            
            runs_data.append({
                'run_id': run_id,
                'timestamp': timestamp,
                'logs_count': logs_count
            })
        except Exception as e:
            logger.warning(f"Error processing run directory {run_id}: {str(e)}")
    
    return pd.DataFrame(runs_data)

def get_run_logs(run_id, config_path=None):
    """
    Get a list of all log files for a specific run.
    
    Args:
        run_id (str): The run ID to get logs for.
        config_path (str, optional): Path to configuration file.
        
    Returns:
        pandas.DataFrame: DataFrame with log file information.
    """
    base_dir = get_base_output_dir(config_path)
    run_dir = os.path.join(base_dir, run_id)
    
    # Check if the directory exists
    if not os.path.exists(run_dir):
        logger.warning(f"Run directory {run_dir} does not exist.")
        return pd.DataFrame(columns=['filename', 'size', 'modified_time'])
    
    # Get all CSV files
    csv_files = glob.glob(os.path.join(run_dir, '*.csv'))
    
    log_data = []
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        
        log_data.append({
            'filename': filename,
            'size': size,
            'modified_time': modified_time
        })
    
    # Sort by modified time (newest first)
    return pd.DataFrame(log_data).sort_values('modified_time', ascending=False) 