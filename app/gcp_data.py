from google.cloud import bigquery
import pandas as pd
import logging

__name__ = "gcp_data"

# Configure logging settings
logging.basicConfig(level=logging.debug,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)



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
