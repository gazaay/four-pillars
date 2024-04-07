from google.cloud import bigquery
import pandas as pd
import logging
from datetime import datetime, timedelta
import json

__name__ = "config_loader"

# Configure logging settings
logging.basicConfig(level=logging.DEBUG,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)

global_config = {}

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

# Call this function at the start of your application
config_df = get_config()
global_config["column_name_mapping"] = config_df[config_df['item'] == 'column_name_mapping']['content'].iloc[0]

logger.info(global_config)



def update_config_content( item, key, new_value, project_id='stock8word', dataset_name='GG88', table_name='config'):
    """
    Updates a key within the JSON content of a specified item in a BigQuery table.

    Parameters:
    - project_id (str): Google Cloud project ID.
    - dataset_name (str): BigQuery dataset name.
    - table_name (str): BigQuery table name.
    - item (str): The item identifier to update.
    - key (str): The key within the JSON content to update.
    - new_value (str or int): The new value to set for the key.

    Returns:
    - None
    """
    client = bigquery.Client(project=project_id)

    # Fetch the current content of the row to be updated
    query = f"""
    SELECT content
    FROM `{project_id}.{dataset_name}.{table_name}`
    WHERE item = @item
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("item", "STRING", item)
        ]
    )
    current_content_result = client.query(query, job_config=job_config).to_dataframe()
    if current_content_result.empty:
        logger.info("Item not found.")
        return

    # Parse the current content
    current_content = json.loads(current_content_result.iloc[0]['content'])

    # Update the key with the new value
    current_content[key] = new_value

    # Convert the updated content back to a JSON string
    updated_content_json = json.dumps(current_content, ensure_ascii=False)

    # Construct the SQL query to update the content field in the specified row
    update_query = f"""
    UPDATE `{project_id}.{dataset_name}.{table_name}`
    SET content = @updated_content
    WHERE item = @item
    """
    update_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("updated_content", "STRING", updated_content_json),
            bigquery.ScalarQueryParameter("item", "STRING", item)
        ]
    )

    # Execute the update query
    client.query(update_query, job_config=update_job_config)
    logger.info(f"Content for item '{item}' updated successfully.")




def update_config_field( item, new_value, project_id='stock8word', dataset_name='GG88', table_name='config', field_name='content'):
    """
    Updates a specified field in a row identified by row_id in a BigQuery table.

    Parameters:
    - project_id (str): Google Cloud project ID.
    - dataset_name (str): BigQuery dataset name.
    - table_name (str): BigQuery table name.
    - row_id (int or str): The ID of the row to update.
    - field_name (str): The name of the field to update.
    - new_value (str): The new value to set for the field.

    Returns:
    - None
    """
    client = bigquery.Client(project=project_id)
    table_full_path = f"`{project_id}.{dataset_name}.{table_name}`"

    # Construct the SQL query to update the specified field in the row with the given ID
    query = f"""
    UPDATE {table_full_path}
    SET {field_name} = @new_value
    WHERE item = @item
    """

    # Set up the query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("new_value", "STRING", new_value),
            bigquery.ScalarQueryParameter("item", "STRING", item),  # Adjust the type if your ID is not a string
        ]
    )

    # Execute the query
    client.query(query, job_config=job_config)

    logger.info(f"Field '{field_name}' for item '{item}' updated successfully.")
