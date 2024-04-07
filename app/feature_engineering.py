from datetime import datetime
from app import bazi, gcp_data, chengseng
import pandas as pd
# import numpy as np
# import cProfile
# import random, string
# from tqdm import tqdm
# import concurrent.futures
import logging
import uuid
from app.config_loader import global_config



__name__ = "feature_engineering"

# Configure logging settings
logging.basicConfig(level=logging.debug,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)


def feature_engineering(symbol_to_query, ric_to_query, start_date, end_date):
      # sample access custom_encoding_mapping['-本時']

      # Example usage:
      # Replace with the symbol you want to query
      result_df = gcp_data.query_stock_info(symbol=symbol_to_query)
      logger.info(result_df)
      if len(result_df) > 0:
          first_item = result_df["birthday_day_time"].iloc[0]
          symbol_list_date = result_df.iloc[0]
          logger.info(first_item)
      else:
          logger.info("The DataFrame is empty.")
      base_8w = bazi.get_heavenly_branch_ymdh_pillars_base(symbol_list_date.bd_year,
                                                                  symbol_list_date.bd_month,
                                                                  symbol_list_date.bd_day,
                                                                  symbol_list_date.bd_hour)
      logger.info(base_8w)

      return base_feature_engineering(symbol_to_query, ric_to_query, base_8w, start_date, end_date)

def base_feature_engineering(symbol_to_query, ric_to_query, base_8w, start_date, end_date):

      # result_df = gcp_data.get_date_range(start_date, end_date)
      result_df = gcp_data.get_date_range(start_date, end_date)
      logger.info(result_df)

      mapping_local = {
          '時': '本時',
          '日': '本日',
          '月': '本月',
          '年': '本年',
          '-月': '-本月',
          '-時': '-本時',
      }

      # Loop through the dictionary and add each item as a new column to result_df
      for key, value in base_8w.items():
          result_df[mapping_local[key]] = value

      # Inverting the dictionary to be English to Chinese for renaming purposes
      # english_to_chinese_col_mapping = {v: k for k, v in column_name_mapping.items()}

      for chinese_col, english_col in global_config["column_name_mapping"].items():
        # logger.info(chinese_col, english_col)
        if english_col in result_df.columns:
          result_df[chinese_col] = result_df[english_col]
          result_df.drop(columns=[english_col], inplace=True)
      # Print the updated DataFrame
      logger.info(result_df)

      current_base_df = result_df.copy()


      # @title Step 7 (cont.): Get stock chengseng and merge with the dataset

      result_df = chengseng.create_chengseng_for_dataset(current_base_df)

      # Call the function
      # Ensure stock_target_intraday and result_df are defined and loaded appropriately
      merged_and_filtered_df = result_df

      # Display or further process merged_and_filtered_df
      logger.info(merged_and_filtered_df.head())

      merged_and_filtered_df['symbol'] = symbol_to_query
      merged_and_filtered_df['ric_code'] = ric_to_query

      merged_and_filtered_df["UUID"]  = str(uuid.uuid4())
      merged_and_filtered_df["last_modified_date"] = datetime.now()

      return merged_and_filtered_df