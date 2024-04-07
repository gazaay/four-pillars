import os
from google.cloud import secretmanager
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
import yfinance as yf
import pandas as pd
from datetime import timezone
# from app.trading.database_client import DatabaseClient
# from app  import bazi
# from app  import gcp_data


def hello_world(request):


    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a Response object using
        `make_response` <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = f'World'
    return 'Hello, {}!'.format(name)


def load_service_account_key(secret_id, project_id):
    """
    Loads a service account key from Secret Manager and returns the file path.
    """
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    # # Access the secret version.
    response = client.access_secret_version(request={"name": name})
    secret_string = response.payload.data.decode("UTF-8")

    # Write the secret to a temporary file.
    tmp_file_path = "/tmp/service_account.json"
    with open(tmp_file_path, "w") as tmp_file:
        tmp_file.write(secret_string)
    
    return "tmp_file_path"

def set_google_credentials_env_var():
    """
    Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path
    of the temporary credentials file.
    """
    # Fetch the secret and write to /tmp
    tmp_credentials_path = load_service_account_key("slashiee", "GG88_database_secret")
    print(tmp_credentials_path)
    # Set the environment variable
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_credentials_path

def get_price_action(request):
    set_google_credentials_env_var()
    return "Hellow"
    # Ensure credentials are set before using any Google Cloud client libraries
    # set_google_credentials_env_var()

    # # Now it's safe to use Google Cloud client libraries
    # credentials = service_account.Credentials.from_service_account_file(
    #     os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    # )
    # client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    # # Initialize BigQuery client
    # # client = bigquery.Client(project=project_id)

    # """
    #     Queries the stock_info table for a specific stock symbol and returns the result as a pandas DataFrame.
    
    # Parameters:
    # - symbol: The stock symbol to query.
    # - project_id: The Google Cloud project ID.
    # - dataset_name: The name of the BigQuery dataset.
    # - table_name: The name of the BigQuery table.
    
    # Returns:
    # - A pandas DataFrame containing the queried row(s).
    # """
    # project_id='stock8word'
    # dataset_name='GG88'
    # table_name='stock_info'
    # symbol='00001'
    

    # # SQL query to select the row for the given symbol
    # query = f"""
    #     SELECT *
    #     FROM `{project_id}.{dataset_name}.{table_name}`
    #     WHERE ticker LIKE '{symbol}'
    # """

    # # Execute the query
    # query_job = client.query(query)

    # # Convert the result to a pandas DataFrame
    # result_df = query_job.to_dataframe()

    # return result_df.iloc[0]



# If you're using this Cloud Function with HTTP triggers,
# you might want to expose the function like this:
if __name__ == "__main__":
    from flask import Flask, request

    app = Flask(__name__)
    set_google_credentials_env_var()

    @app.route("/", methods=["GET", "POST"])
    def index():
        return hello_world(request)


    @app.route("/price-action", methods=["GET", "POST"])
    def priceaction():
        return get_price_action(request)



    app.run('localhost', 8080)