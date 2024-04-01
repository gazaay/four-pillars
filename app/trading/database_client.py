from google.cloud import bigquery
import json
import pandas as pd

class DatabaseClient:
    def __init__(self, project_id='stock8word', dataset_name='GG88'):
        """
        Initializes the DatabaseClient with a specific Google Cloud project and dataset.

        Parameters:
        - project_id (str): The Google Cloud project ID.
        - dataset_name (str): The name of the BigQuery dataset.
        """
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.client = bigquery.Client(project=self.project_id)

    def get_config(self, table_name='config'):
        """
        Fetches configuration data from the specified BigQuery table and returns it as a pandas DataFrame.

        Parameters:
        - table_name (str): The name of the BigQuery table (default 'config').

        Returns:
        - pandas.DataFrame: A DataFrame containing the configuration data.
        """
        query = f"SELECT * FROM `{self.project_id}.{self.dataset_name}.{table_name}`"
        result_df = self.client.query(query).to_dataframe()
        # Parse JSON strings in columns, if applicable
        result_df = self._parse_json_columns(result_df)
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
    def get_trade_strategy(self, ticker, strategy_name):
        """
        Fetches a specific trade strategy for a given ticker symbol from the `trade_strategies` table.

        Parameters:
        - ticker (str): The ticker symbol.
        - strategy_name (str): The name of the trade strategy.

        Returns:
        - dict: A dictionary containing the trade strategy details.
        """
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_name}.trade_strategies`
        WHERE ticker = '{ticker}'
        AND strategy_name = '{strategy_name}'
        """
        result_df = self.client.query(query).to_dataframe()
        # Parse JSON strings in columns, if applicable
        result_df = self._parse_json_columns(result_df)
        return result_df.to_dict(orient='records')[0] if not result_df.empty else None
    
    
    def get_price_action(self, ticker, start_date, end_date):
        """
        Fetches price action data for a specific ticker symbol within a date range.

        Parameters:
        - ticker (str): The ticker symbol.
        - start_date (str): The start date in 'YYYY-MM-DD' format.
        - end_date (str): The end date in 'YYYY-MM-DD' format.

        Returns:
        - pandas.DataFrame: A DataFrame containing the price action data.
        """
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_name}.price_action`
        WHERE symbol = '{ticker}'
        AND DATE(date) BETWEEN DATE('{start_date}') AND DATE('{end_date}')
        """
        result_df = self.client.query(query).to_dataframe()
        return result_df

    def save_ticker_price(self, ticker, price):
        """
        Saves the ticker price to the `ticker_price` table in BigQuery.

        Parameters:
        - ticker (str): The ticker symbol.
        - price (float): The price of the ticker.
        """
        # Construct the query to insert the ticker price into the database
        query = f"""
        INSERT INTO `{self.project_id}.{self.dataset_name}.ticker_price` (timestamp, UUID, ticker_code, price)
        VALUES (CURRENT_TIMESTAMP(), GENERATE_UUID(), '{ticker}', {price})
        """
        self.client.query(query)

    def _parse_json_columns(self, df):
        """
        Attempts to parse JSON strings in DataFrame columns into Python dictionaries.

        Parameters:
        - df (pandas.DataFrame): The DataFrame to process.

        Returns:
        - pandas.DataFrame: The DataFrame with parsed JSON columns where applicable.
        """
        for column in df.columns:
            try:
                df[column] = df[column].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
            except json.JSONDecodeError:
                pass
        return df

# Example usage
if __name__ == "__main__":
    db_client = DatabaseClient()
    config_df = db_client.get_config()
    print(config_df)
