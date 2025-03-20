from google.cloud import bigquery
import pandas as pd
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logger = logging.getLogger(__name__)

def get_versioned_pillars(version: str = "v1.0", force_recalculate: bool = False) -> pd.DataFrame:
    """
    Get the thousand-year current pillars dataset, either from database or by calculating it.
    
    Args:
        version: Version number for the dataset (e.g., "v1.0")
        force_recalculate: If True, recalculate even if data exists in database
        
    Returns:
        DataFrame containing the time and 8-word pillars
    """
    try:
        # Initialize BigQuery client
        project_id = 'stock8word'
        dataset_name = 'GG88'
        table_name = 'thousand_year_current_pillars'
        
        client = bigquery.Client(project=project_id)
        
        # Check if the version already exists in the database
        if not force_recalculate:
            logger.info(f"Checking if dataset version {version} exists in the database")
            
            # Query to check if the version exists
            version_check_query = f"""
            SELECT COUNT(*) as count
            FROM `{project_id}.{dataset_name}.{table_name}`
            WHERE version = '{version}'
            LIMIT 1
            """
            
            version_check_result = client.query(version_check_query).to_dataframe()
            
            if version_check_result['count'].iloc[0] > 0:
                logger.info(f"Dataset version {version} found in database. Retrieving data.")
                
                # Retrieve data from database
                query = f"""
                SELECT * EXCEPT(version)
                FROM `{project_id}.{dataset_name}.{table_name}`
                WHERE version = '{version}'
                """
                
                dataset = client.query(query).to_dataframe()
                
                # Convert time column to datetime if it's not already
                if 'time' in dataset.columns and not pd.api.types.is_datetime64_any_dtype(dataset['time']):
                    dataset['time'] = pd.to_datetime(dataset['time'])
                
                logger.info(f"Successfully retrieved {len(dataset)} rows for version {version}")
                return dataset
            else:
                logger.info(f"Dataset version {version} not found in database. Will calculate.")
        
        # If we reach here, we need to calculate the dataset
        logger.info(f"Calculating new dataset version {version}")
        dataset = calculate_thousand_year_pillars()
        
        # Add version column
        dataset['version'] = version
        
        # Store in database - first delete any existing rows with this version
        delete_query = f"""
        DELETE FROM `{project_id}.{dataset_name}.{table_name}`
        WHERE version = '{version}'
        """
        client.query(delete_query)
        
        # Upload the data to BigQuery
        logger.info(f"Storing dataset in BigQuery table: {table_name}")
        
        # Define the table schema if needed - this ensures proper data types
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("time", "TIMESTAMP"),
                bigquery.SchemaField("version", "STRING"),
                # Add other columns as needed based on your dataset structure
                bigquery.SchemaField("year_pillar", "STRING"),
                bigquery.SchemaField("month_pillar", "STRING"),
                bigquery.SchemaField("day_pillar", "STRING"),
                bigquery.SchemaField("hour_pillar", "STRING"),
                bigquery.SchemaField("year_stem", "STRING"),
                bigquery.SchemaField("year_branch", "STRING"),
                bigquery.SchemaField("month_stem", "STRING"),
                bigquery.SchemaField("month_branch", "STRING"),
                bigquery.SchemaField("day_stem", "STRING"),
                bigquery.SchemaField("day_branch", "STRING"),
                bigquery.SchemaField("hour_stem", "STRING"),
                bigquery.SchemaField("hour_branch", "STRING")
            ],
            write_disposition="WRITE_APPEND"
        )
        
        # Use the client to upload dataframe to BigQuery
        table_ref = f"{project_id}.{dataset_name}.{table_name}"
        job = client.load_table_from_dataframe(dataset, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete
        
        logger.info(f"Successfully stored {len(dataset)} rows in {table_name} with version {version}")
        
        # Remove version column from returned dataset for consistency
        return dataset.drop(columns=['version'])
        
    except Exception as e:
        logger.error(f"Error in get_versioned_pillars: {str(e)}")
        # Fallback to calculation if database operations fail
        logger.info("Falling back to direct calculation due to error")
        return calculate_thousand_year_pillars()

def calculate_thousand_year_pillars() -> pd.DataFrame:
    """
    Calculate the thousand-year current pillars dataset from scratch.
    
    Returns:
        DataFrame containing the time and 8-word pillars
    """
    from app import chengseng  # Import here to avoid circular imports
    
    logger.info("Calculating thousand-year pillars from scratch")
    
    # Define time range
    today = datetime.now()
    # Set the time to 9:00 AM to match the original code
    today = today.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # start_date = today - timedelta(days=1525)
    start_date = today - timedelta(days=50)
    end_date = today + timedelta(days=2)
    
    # Create a blank data frame with time column
    time_range = pd.date_range(start=start_date, end=end_date, freq='1H').union(
        pd.date_range(end_date, end_date + pd.DateOffset(months=12), freq='D'))
    dataset = pd.DataFrame({'time': time_range})
    
    # Adding 8w pillars to the dataset
    dataset = chengseng.adding_8w_pillars(dataset)
    
    logger.info(f"Finished calculating dataset with {len(dataset)} rows")
    return dataset

def check_table_exists(project_id='stock8word', dataset_name='GG88', table_name='thousand_year_current_pillars'):
    """
    Check if the table exists in BigQuery and create it if it doesn't.
    
    Returns:
        bool: True if table exists or was created successfully, False otherwise
    """
    try:
        client = bigquery.Client(project=project_id)
        
        # Try to get the table
        table_ref = f"{project_id}.{dataset_name}.{table_name}"
        try:
            client.get_table(table_ref)
            logger.info(f"Table {table_ref} already exists")
            return True
        except Exception:
            logger.info(f"Table {table_ref} does not exist. Creating it...")
            
            # Define schema for the table
            schema = [
                bigquery.SchemaField("time", "TIMESTAMP"),
                bigquery.SchemaField("version", "STRING"),
                bigquery.SchemaField("year_pillar", "STRING"),
                bigquery.SchemaField("month_pillar", "STRING"),
                bigquery.SchemaField("day_pillar", "STRING"),
                bigquery.SchemaField("hour_pillar", "STRING"),
                bigquery.SchemaField("year_stem", "STRING"),
                bigquery.SchemaField("year_branch", "STRING"),
                bigquery.SchemaField("month_stem", "STRING"),
                bigquery.SchemaField("month_branch", "STRING"),
                bigquery.SchemaField("day_stem", "STRING"),
                bigquery.SchemaField("day_branch", "STRING"),
                bigquery.SchemaField("hour_stem", "STRING"),
                bigquery.SchemaField("hour_branch", "STRING")
            ]
            
            # Create the table
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            logger.info(f"Table {table_ref} created successfully")
            return True
    except Exception as e:
        logger.error(f"Error checking/creating table: {str(e)}")
        return False 