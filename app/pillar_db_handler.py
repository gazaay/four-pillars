from google.cloud import bigquery
import pandas as pd
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logger = logging.getLogger(__name__)

def get_versioned_pillars(version: str = "v1.0", force_recalculate: bool = False, 
                          days_back: int = 50, days_forward: int = 2, forecast_months: int = 12) -> pd.DataFrame:
    """
    Get the thousand-year current pillars dataset, either from database or by calculating it.
    
    Args:
        version: Version number for the dataset (e.g., "v1.0")
        force_recalculate: If True, recalculate even if data exists in database
        days_back: Number of days to look back from today (default: 50)
        days_forward: Number of days to look forward from today (default: 2)
        forecast_months: Number of months to include in the forecast (default: 12)
        
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
        dataset = calculate_thousand_year_pillars(days_back, days_forward, forecast_months)
        # Rename columns to match database schema
        column_mapping = {
            'time': 'time',
            '流時': 'hour_pillar',
            '流日': 'day_pillar', 
            '-流時': 'hidden_hour_pillar',
            '流月': 'month_pillar',
            '流年': 'year_pillar',
            '-流月': 'hidden_month_pillar',
            '時運': 'hour_yun',
            '日運': 'day_yun',
            '月運': 'month_yun',
            '年運': 'year_yun'
        }
        
        logger.info("Renaming columns to match database schema")
        dataset = dataset.rename(columns=column_mapping)
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

                bigquery.SchemaField("hour_pillar", "STRING"),
                bigquery.SchemaField("day_pillar", "STRING"),
                bigquery.SchemaField("hidden_hour_pillar", "STRING"),
                bigquery.SchemaField("month_pillar", "STRING"),
                bigquery.SchemaField("year_pillar", "STRING"),
                bigquery.SchemaField("hidden_month_pillar", "STRING"),

              
                bigquery.SchemaField("hour_yun", "STRING"),
                bigquery.SchemaField("day_yun", "STRING"),
                bigquery.SchemaField("month_yun", "STRING"),
                bigquery.SchemaField("year_yun", "STRING"),
            ],
            write_disposition="WRITE_APPEND"
        )
        
        # Use the client to upload dataframe to BigQuery
        table_ref = f"{project_id}.{dataset_name}.{table_name}"
        job = client.load_table_from_dataframe(dataset, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete
        
        # Store metadata about the dataset parameters
        metadata_table = f"{project_id}.{dataset_name}.thousand_year_current_pillars_metadata"
        
        try:
            # Create metadata table if it doesn't exist
            try:
                client.get_table(metadata_table)
            except Exception:
                # Table doesn't exist, create it
                schema = [
                    bigquery.SchemaField("version", "STRING"),
                    bigquery.SchemaField("metadata", "STRING"),
                    bigquery.SchemaField("creation_date", "TIMESTAMP")
                ]
                table = bigquery.Table(metadata_table, schema=schema)
                client.create_table(table)
                logger.info(f"Created metadata table: {metadata_table}")
            
            # Delete existing metadata for this version
            metadata_delete_query = f"""
            DELETE FROM `{metadata_table}`
            WHERE version = '{version}'
            """
            client.query(metadata_delete_query)
            
            # Insert metadata with the parameters used - use string for datetime
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            metadata = {
                'days_back': days_back,
                'days_forward': days_forward,
                'forecast_months': forecast_months,
                'creation_date': current_time
            }
            
            metadata_rows = [{
                'version': version,
                'metadata': json.dumps(metadata),
                'creation_date': datetime.now()
            }]
            
            client.insert_rows_json(metadata_table, metadata_rows)
            logger.info(f"Stored dataset parameters in metadata table")
        except Exception as e:
            logger.warning(f"Could not store metadata: {str(e)}")
        
        logger.info(f"Successfully stored {len(dataset)} rows in {table_name} with version {version}")
        
        # Remove version column from returned dataset for consistency
        return dataset.drop(columns=['version'])
        
    except Exception as e:
        logger.error(f"Error in get_versioned_pillars: {str(e)}")
        # Fallback to calculation if database operations fail
        logger.info("Falling back to direct calculation due to error")
        return calculate_thousand_year_pillars(days_back, days_forward, forecast_months)

def calculate_thousand_year_pillars(days_back=50, days_forward=2, forecast_months=12) -> pd.DataFrame:
    """
    Calculate the thousand-year current pillars dataset from scratch.
    
    Args:
        days_back: Number of days to look back from today (default: 50)
        days_forward: Number of days to look forward from today (default: 2)
        forecast_months: Number of months to include in the forecast (default: 12)
    
    Returns:
        DataFrame containing the time and 8-word pillars
    """
    from app import chengseng  # Import here to avoid circular imports
    
    logger.info(f"Calculating pillars with parameters: days_back={days_back}, days_forward={days_forward}, forecast_months={forecast_months}")
    
    # Define time range
    today = datetime.now()
    # Set the time to 9:00 AM to match the original code
    today = today.replace(hour=9, minute=0, second=0, microsecond=0)
    
    start_date = today - timedelta(days=days_back)
    end_date = today + timedelta(days=days_forward)
    
    # Create a blank data frame with time column
    time_range = pd.date_range(start=start_date, end=end_date, freq='1H').union(
        pd.date_range(end_date, end_date + pd.DateOffset(months=forecast_months), freq='D'))
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


                bigquery.SchemaField("hour_pillar", "STRING"),
                bigquery.SchemaField("day_pillar", "STRING"),
                bigquery.SchemaField("hidden_hour_pillar", "STRING"),
                bigquery.SchemaField("month_pillar", "STRING"),
                bigquery.SchemaField("year_pillar", "STRING"),
                bigquery.SchemaField("hidden_month_pillar", "STRING"),

              
                bigquery.SchemaField("hour_yun", "STRING"),
                bigquery.SchemaField("day_yun", "STRING"),
                bigquery.SchemaField("month_yun", "STRING"),
                bigquery.SchemaField("year_yun", "STRING"),
            ]
            
            # Create the table
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            logger.info(f"Table {table_ref} created successfully")
            return True
    except Exception as e:
        logger.error(f"Error checking/creating table: {str(e)}")
        return False 