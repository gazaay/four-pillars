from datetime import datetime, timedelta
from app  import bazi
import json
import pandas as pd
import pytz
import numpy as np
from google.oauth2 import service_account
from google.cloud import secretmanager
from google.cloud import bigquery
from app.config_loader import global_config, get_config, update_config_content, update_config_field
from app.feature_engineering import feature_engineering

# Load the configuration at application start
print (global_config["column_name_mapping"].items())



# Assuming load_service_account_key is called and sets the environment variable correctly
# service_account_path = load_service_account_key("slashiee", "GG88_database_secret")
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
# print(f"here is the path {service_account_path}")

# Testing if feature engineering works on local
symbol_to_query ="00001"
ric_to_query="0001.hk"
today = datetime.now()
master_start_date = today - timedelta(days=1)
master_end_date = today + timedelta(days=20)
merged_and_filtered_df = feature_engineering(symbol_to_query, ric_to_query, master_start_date, master_end_date)
print(merged_and_filtered_df)




##########################################
# BELOW ARE SCRIPTS TO UPDATE CONFIG TABLE
##########################################
# # Create a dictionary to map Chinese column names to English column names
# column_name_mapping = {
#     '本時': 'base_time',
#     '本日': 'base_day',
#     '-本時': 'base_minus_time',
#     '本月': 'base_month',
#     '本年': 'base_year',
#     '-本月': 'base_minus_month',
#     '流時': 'current_time',
#     '流日': 'current_day',
#     '-流時': 'current_minus_time',
#     '流月': 'current_month',
#     '流年': 'current_year',
#     '-流月': 'current_minus_month',
#     '長_本時_流時': 'diff_base_time_current_time',
#     '長_本時_流日': 'diff_base_time_current_day',
#     '長_本時_-流時': 'diff_base_time_current_minus_time',
#     '長_本時_流月': 'diff_base_time_current_month',
#     '長_本時_流年': 'diff_base_time_current_year',
#     '長_本時_-流月': 'diff_base_time_current_minus_month',
#     '長_本日_流時': 'diff_base_day_current_time',
#     '長_本日_流日': 'diff_base_day_current_day',
#     '長_本日_-流時': 'diff_base_day_current_minus_time',
#     '長_本日_流月': 'diff_base_day_current_month',
#     '長_本日_流年': 'diff_base_day_current_year',
#     '長_本日_-流月': 'diff_base_day_current_minus_month',
#     '長_-本時_流時': 'diff_base_minus_time_current_time',
#     '長_-本時_流日': 'diff_base_minus_time_current_day',
#     '長_-本時_-流時': 'diff_base_minus_time_current_minus_time',
#     '長_-本時_流月': 'diff_base_minus_time_current_month',
#     '長_-本時_流年': 'diff_base_minus_time_current_year',
#     '長_-本時_-流月': 'diff_base_minus_time_current_minus_month',
#     '長_本月_流時': 'diff_base_month_current_time',
#     '長_本月_流日': 'diff_base_month_current_day',
#     '長_本月_-流時': 'diff_base_month_current_minus_time',
#     '長_本月_流月': 'diff_base_month_current_month',
#     '長_本月_流年': 'diff_base_month_current_year',
#     '長_本月_-流月': 'diff_base_month_current_minus_month',
#     '長_本年_流時': 'diff_base_year_current_time',
#     '長_本年_流日': 'diff_base_year_current_day',
#     '長_本年_-流時': 'diff_base_year_current_minus_time',
#     '長_本年_流月': 'diff_base_year_current_month',
#     '長_本年_流年': 'diff_base_year_current_year',
#     '長_本年_-流月': 'diff_base_year_current_minus_month',
#     '長_-本月_流時': 'diff_base_minus_month_current_time',
#     '長_-本月_流日': 'diff_base_minus_month_current_day',
#     '長_-本月_-流時': 'diff_base_minus_month_current_minus_time',
#     '長_-本月_流月': 'diff_base_minus_month_current_month',
#     '長_-本月_流年': 'diff_base_minus_month_current_year',
#     '長_-本月_-流月': 'diff_base_minus_month_current_minus_month',
# }

# update_config_field("column_name_mapping", json.dumps(column_name_mapping))

# # Below are the scripts to update the config table on one of the fields in one config only. 
# # update_config_content("column_name_mapping", "GARY_本時", "base_time")

# config_df = get_config()
# global_config["column_name_mapping"] = config_df[config_df['item'] == 'column_name_mapping']['content'].iloc[0]

# print (global_config["column_name_mapping"].items())
