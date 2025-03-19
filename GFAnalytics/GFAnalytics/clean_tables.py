#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to clean BigQuery tables
"""

import logging
from GFAnalytics.data.data_storage import BigQueryStorage
from GFAnalytics.utils.config_utils import load_config

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Load config
        config = load_config()
        
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