import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pillar_helper')

def get_pillars_dataset(version="v1.0", force_recalculate=False):
    """
    Get a dataset with 8-word pillars, either from database or by calculating it.
    This is a wrapper function that can be used in notebooks for convenience.
    
    Args:
        version (str): Version number for the dataset
        force_recalculate (bool): If True, recalculate even if data exists in database
        
    Returns:
        DataFrame containing the time and 8-word pillars
    """
    # Setup paths to find our modules
    setup_import_paths()
    
    try:
        # Try different import paths to find pillar_db_handler
        try:
            # Try direct import first (if in same directory)
            from pillar_db_handler import get_versioned_pillars, check_table_exists
        except ImportError:
            try:
                # Try from app directory
                from app.pillar_db_handler import get_versioned_pillars, check_table_exists
            except ImportError:
                # Try from parent directory
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from pillar_db_handler import get_versioned_pillars, check_table_exists
        
        # First check if the table exists and create it if needed
        check_table_exists()
        
        # Get the dataset from the database or calculate it if needed
        logger.info(f"Getting pillars dataset version {version}, force_recalculate={force_recalculate}")
        dataset = get_versioned_pillars(version=version, force_recalculate=force_recalculate)
        
        logger.info(f"Retrieved dataset with {len(dataset)} rows")
        return dataset
        
    except ImportError as e:
        logger.warning(f"Could not import pillar_db_handler: {e}")
        logger.info("Falling back to direct calculation")
        return calculate_pillars_directly()
    except Exception as e:
        logger.error(f"Error getting versioned pillars: {e}")
        logger.info("Falling back to direct calculation")
        return calculate_pillars_directly()

def calculate_pillars_directly():
    """
    Calculate the pillars dataset directly without database caching.
    Used as a fallback if the database handler isn't available.
    
    Returns:
        DataFrame with pillars
    """
    # Setup paths to find our modules
    setup_import_paths()
    
    try:
        # Try different import paths to find chengseng
        try:
            # Try direct import first
            import chengseng
        except ImportError:
            try:
                # Try from app directory
                from app import chengseng
            except ImportError:
                # Try with parent directory in path
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from app import chengseng
        
        logger.info("Calculating pillars directly (no database caching)")
        
        # Define time range
        today = datetime.now()
        today = today.replace(hour=9, minute=0, second=0, microsecond=0)
        
        start_date = today - timedelta(days=1525)
        end_date = today + timedelta(days=220)
        
        # Create a blank data frame with time column
        time_range = pd.date_range(start=start_date, end=end_date, freq='1H').union(
            pd.date_range(end_date, end_date + pd.DateOffset(months=12), freq='D'))
        dataset = pd.DataFrame({'time': time_range})
        
        # Adding 8w pillars to the dataset
        dataset = chengseng.adding_8w_pillars(dataset)
        
        logger.info(f"Finished direct calculation, dataset has {len(dataset)} rows")
        return dataset
    except Exception as e:
        logger.error(f"Error in direct calculation: {e}")
        raise

def setup_import_paths():
    """Set up Python import paths to find our modules"""
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Add parent directory to path
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    
    # Add app directory to path
    app_dir = os.path.join(parent_dir, 'app')
    if os.path.exists(app_dir) and app_dir not in sys.path:
        sys.path.append(app_dir) 