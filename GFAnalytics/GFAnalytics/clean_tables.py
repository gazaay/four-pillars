#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to clean BigQuery tables
"""

import logging
import os
import yaml
from GFAnalytics.data.data_storage import BigQueryStorage

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Load config from default path
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize storage
        storage = BigQueryStorage(config)
        
        # Clean specific table
        # storage.clean_table('bazi_data')
        
        # Or clean all tables
        storage.clean_all_tables()
        
        logger.info("Tables cleaned successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning tables: {str(e)}")
        raise

if __name__ == "__main__":
    main()