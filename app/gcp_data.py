from google.cloud import bigquery
import pandas as pd
import logging
from datetime import datetime, timedelta

__name__ = "gcp_data"

# Configure logging settings
logging.basicConfig(level=logging.debug,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)

def get_date_range(start_date, end_date, project_id='stock8word', dataset_name='GG88', table_name='thousand_year_data'):
    """
    Queries a BigQuery table for rows within a specific date range and returns the result as a pandas DataFrame.

    Parameters:
    - start_date (datetime): The start of the date range.
    - end_date (datetime): The end of the date range.
    - project_id (str): The Google Cloud project ID.
    - dataset_name (str): The name of the BigQuery dataset.
    - table_name (str): The name of the BigQuery table.

    Returns:
    - pandas.DataFrame: A DataFrame containing the queried rows.
    """
    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)

    # Convert start_date and end_date to string in format 'YYYY-MM-DD HH:MM:SS'
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

    # SQL query to select rows within the date range
    query = f"""
        SELECT *
        FROM `{project_id}.{dataset_name}.{table_name}`
        WHERE time BETWEEN TIMESTAMP('{start_date_str}') AND TIMESTAMP('{end_date_str}')
    """

    # Execute the query and return results as a DataFrame
    result_df = client.query(query).to_dataframe()

    return result_df


def query_stock_info(symbol, project_id='stock8word', dataset_name='GG88', table_name='stock_info'):
    """
    Queries the stock_info table for a specific stock symbol and returns the result as a pandas DataFrame.
    
    Parameters:
    - symbol: The stock symbol to query.
    - project_id: The Google Cloud project ID.
    - dataset_name: The name of the BigQuery dataset.
    - table_name: The name of the BigQuery table.
    
    Returns:
    - A pandas DataFrame containing the queried row(s).
    """
    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)

    # SQL query to select the row for the given symbol
    query = f"""
        SELECT *
        FROM `{project_id}.{dataset_name}.{table_name}`
        WHERE ticker = '{symbol}'
    """

    # Execute the query
    query_job = client.query(query)

    # Convert the result to a pandas DataFrame
    result_df = query_job.to_dataframe()

    return result_df

# Example usage:
symbol_to_query = '00001'  # Replace with the symbol you want to query
result_df = query_stock_info(symbol=symbol_to_query)
print(result_df)
