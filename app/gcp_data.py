from google.cloud import bigquery
import pandas as pd
import logging
from datetime import datetime, timedelta
import json

__name__ = "gcp_data"

# Configure logging settings
logging.basicConfig(level=logging.debug,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)

def get_config(project_id='stock8word', dataset_name='GG88', table_name='config'):
    """
    Fetches configuration data from the specified BigQuery table and returns it as a pandas DataFrame.

    Parameters:
    - project_id (str): The Google Cloud project ID.
    - dataset_name (str): The name of the BigQuery dataset.
    - table_name (str): The name of the BigQuery table (default 'config').

    Returns:
    - pandas.DataFrame: A DataFrame containing the configuration data.
    """
    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)

    # Construct the SQL query to select all rows from the config table
    query = f"SELECT * FROM `{project_id}.{dataset_name}.{table_name}`"

    # Execute the query and return results as a DataFrame
    result_df = client.query(query).to_dataframe()
    # Assuming all columns may contain JSON strings, try parsing each value
    for column in result_df.columns:
        try:
            # Attempt to parse the JSON string into a Python dictionary
            result_df[column] = result_df[column].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        except json.JSONDecodeError:
            # If JSON parsing fails, leave the column as is
            pass
            
    return result_df

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
        WHERE ticker LIKE '{symbol}'
    """

    # Execute the query
    query_job = client.query(query)

    # Convert the result to a pandas DataFrame
    result_df = query_job.to_dataframe()

    return result_df

from google.cloud import bigquery

def update_stock_info_field(ticker, field_name, new_value, 
                            project_id='stock8word', dataset_name='GG88', table_name='stock_info'):
    """
    Updates a specified field for a stock in the stock_info table.

    Parameters:
    - project_id (str): Google Cloud project ID.
    - dataset_name (str): BigQuery dataset name.
    - table_name (str): BigQuery table name.
    - ticker (str): The ticker symbol of the stock to update.
    - field_name (str): The name of the field to update.
    - new_value (str or int): The new value to set for the field.

    Returns:
    - None
    """
    client = bigquery.Client(project=project_id)

    # Construct the SQL query to update the specified field for the given ticker
    query = f"""
    UPDATE `{project_id}.{dataset_name}.{table_name}`
    SET {field_name} = @new_value
    WHERE ticker = @ticker
    """

    # Set up the query parameters to prevent SQL injection
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("new_value", "STRING", new_value),
            bigquery.ScalarQueryParameter("ticker", "STRING", ticker)
        ]
    )

    # Execute the update query
    client.query(query, job_config=job_config)

    print(f"Stock info for ticker '{ticker}' updated successfully.")

from google.cloud import bigquery

def add_new_stock_info(project_id, dataset_name, table_name, new_row_data):
    """
    Adds a new row to the stock_info table.

    Parameters:
    - project_id (str): Google Cloud project ID.
    - dataset_name (str): BigQuery dataset name.
    - table_name (str): BigQuery table name.
    - new_row_data (dict): A dictionary representing the new row to add. Keys should match the column names.

    Returns:
    - None
    """
    client = bigquery.Client(project=project_id)
    table_id = f"{project_id}.{dataset_name}.{table_name}"

    # Insert the new row
    errors = client.insert_rows_json(table_id, [new_row_data])  
    
    # Make sure new_row_data is a list of dictionaries

    if errors == []:
        print("New row has been added.")
    else:
        print("Errors occurred while inserting the row:", errors)

# new_row_data = {
#     "birthday_day_time": "2024-04-01 09:30:00.000000 UTC",
#     "bd_year": "2024",
#     "bd_month": "4",
#     "bd_day": "1",
#     "ticker": "01234",
#     "ric_code": "01234.hk",
#     "bd_minutes": "30",
#     "bd_hour": "9",
#     "UUID": "unique-uuid-1234-5678",
#     "last_modified_date": "2024-04-07 10:00:00.000000 UTC"
# }

# # Call the function
# add_new_stock_info('stock8word', 'GG88', 'stock_info', new_row_data)



# # Example usage:
# config_df = get_config()
# print(config_df)

# print( config_df[config_df['item'] == 'column_name_mapping']['content'].iloc[0])


# # Example usage:
# symbol_to_query = '00001'  # Replace with the symbol you want to query
# result_df = query_stock_info(symbol=symbol_to_query)
# print(result_df)

# # Example usage:
# stock_list = query_stock_info(symbol='%')

# stock_list['ric_code'] = stock_list['ric_code'].str[1:]
# print(stock_list)
