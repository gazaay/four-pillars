from datetime import datetime
from app import bazi
import pandas as pd
import numpy as np
import concurrent.futures
import threading
import cProfile
import random, string
from tqdm import tqdm
import concurrent.futures
import logging

__name__ = "chengseng"

# Configure logging settings
logging.basicConfig(level=logging.debug,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)


# Create a lock object
lock = threading.Lock()

# Create a DataFrame
# sorted_df_with_new_features = pd.DataFrame()
result_base = {}

def process_8w_row(index, row):
        # print(row)
        # counting()
        max_attempts = 5
        current_attempt = 0
        required_columns = [
            #   '本時', '本日', '-本時', '本月', '本年', '-本月', 
                            '流時', '流日', '-流時', '流月', '流年', '-流月', '時運', '日運', '-日運', '-時運', '月運', '年運', '-年運', '-月運', ]
        # sorted_df_with_new_features = pd.DataFrame()
        while current_attempt < max_attempts:
                # with lock:
                    try:
                        
                        time_string = row["time"]
                        time_format = "%Y-%m-%dT%H:%M:%S%z"
                        parsed_time = time_string
                        # datetime.strptime(time_string, time_format)
                        # datetime.strptime(time_string, time_format)
                        
                        # Extract the components
                        year = parsed_time.year
                        month = parsed_time.month
                        day = parsed_time.day
                        hour = parsed_time.hour

                        # logger.info(f"{index} - {year} - {month} - {day} - {hour}Started processing")
                        result_current = bazi.get_heavenly_branch_ymdh_pillars_current_flip_Option_2(year,month,day,hour)
                        result_wuxi = bazi.get_wuxi_current(year,month,day,hour)

                        with lock:
                            enhanced_row = row.copy()

                            enhanced_row["流時"] = str(result_current["時"])
                            enhanced_row["流日"] = result_current["日"] 
                            enhanced_row["-流時"] = result_current["-時"]
                            enhanced_row["流月"] = result_current["月"]
                            enhanced_row["流年"] = result_current["年"]
                            enhanced_row["-流月"] = result_current["-月"]

                            enhanced_row["時運"] = result_wuxi["時運"]
                            enhanced_row["日運"] = result_wuxi["日運"]
                            enhanced_row["-日運"] = result_wuxi["-日運"]
                            enhanced_row["-時運"] = result_wuxi["-時運"]
                            enhanced_row["月運"] = result_wuxi["月運"]
                            enhanced_row["年運"] = result_wuxi["年運"]
                            enhanced_row["-年運"] = result_wuxi["-年運"]
                            enhanced_row["-月運"] = result_wuxi["-月運"]

                            return enhanced_row

                        
                    except Exception as e:
                            logger.info(f"{index} -  An error occurred: {e}")
                            current_attempt += 1



def adding_8w_pillars( sorted_df):

    logger.info(f"Adding 8W pillars to the DataFrame")
    _local_df = sorted_df.copy()
    columns_to_initialize = [
        #    '本時', '本日', '-本時', '本月', '本年', '-本月', 
                             '流時', '流日', '-流時', '流月', '流年', '-流月',
                             '時運', '日運', '-日運', '-時運', '月運', '年運', '-年運', '-月運', ]

    for column in columns_to_initialize:
        _local_df[column] = "_"

    # If you only want to see the column names
    print("\nColumn names:")
    print(_local_df.columns.tolist())
    # Set the maximum number of threads you want to use
    max_threads = 5000  # Change this as needed

    rows = _local_df
    total_rows = len(rows)
    # Create a ThreadPoolExecutor with the desired number of threads
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
            # Wrap the executor with tqdm for progress tracking
            with tqdm(total=total_rows, desc="Processing", unit="row", dynamic_ncols=True) as pbar:
                    # Submit each row for processing in parallel
                    rows["流時"] = pd.Series(dtype='object')
                    futures = [executor.submit(process_8w_row, index, row) for index, row in rows.iterrows()]
                    
                    # Process completed tasks
                    for future in concurrent.futures.as_completed(futures):
                            # Update the progress bar for each completed task
                            future_row = future.result()
                            # print(future_row)
                            # future_row['本時'] = result_base["時"]
                            # future_row['本日'] = result_base["日"]
                            # future_row['-本時'] = result_base["-時"]
                            # future_row['本月'] = result_base["月"]
                            # future_row['本年'] = result_base["年"]
                            # future_row['-本月'] = result_base["-月"]
                            
                            try:
                                if isinstance(future_row, dict):
                                    future_row = pd.Series(future_row)
                                    
                                # _local_df[_local_df['time'] == future_row['time']] = future_row
                                # Ensuring future_row is a Series if it's not already, for compatibility with .loc[row_indexer, col_indexer] = value
                                
                                # Finding the index(es) where 'time' matches future_row['time'] and updating those rows
                                matching_indexes = _local_df[_local_df['time'] == future_row['time']].index
                                if not matching_indexes.empty:
                                    for column in _local_df.columns:
                                        # Update each column that exists in future_row for the matching indexes
                                        if column in future_row:
                                            _local_df.loc[matching_indexes, column] = future_row[column]
                                else:
                                    print("No matching 'time' found to update.")
                                    
                            except Exception as e:
                                print(f"An error occurred: {e}")

                            pbar.update()

                    # Wait for all tasks to complete
                    # concurrent.futures.wait(futures)

    return _local_df

def get_cheung_sheng(stem_branch):
    cheung_sheng_dict = {
        "甲亥": "長生", "甲子": "沐浴", "甲丑": "冠帶", "甲寅": "臨官", "甲卯": "帝旺",
        "甲辰": "衰", "甲巳": "病", "甲午": "死", "甲未": "墓庫", "甲申": "絕",
        "甲酉": "胎", "甲戌": "養", "丙寅": "長生", "丙卯": "沐浴", "丙辰": "冠帶",
        "丙巳": "臨官", "丙午": "帝旺", "丙未": "衰", "丙申": "病", "丙酉": "死",
        "丙戌": "墓庫", "丙亥": "絕", "丙子": "胎", "丙丑": "養", "戊寅": "長生",
        "戊卯": "沐浴", "戊辰": "冠帶", "戊巳": "臨官", "戊午": "帝旺", "戊未": "衰",
        "戊申": "病", "戊酉": "死", "戊戌": "墓庫", "戊亥": "絕", "戊子": "胎",
        "戊丑": "養", "庚巳": "長生", "庚午": "沐浴", "庚未": "冠帶", "庚申": "臨官",
        "庚酉": "帝旺", "庚戌": "衰", "庚亥": "病", "庚子": "死", "庚丑": "墓庫",
        "庚寅": "絕", "庚卯": "胎", "庚辰": "養", "壬申": "長生", "壬酉": "沐浴",
        "壬戌": "冠帶", "壬亥": "臨官", "壬子": "帝旺", "壬丑": "衰", "壬寅": "病",
        "壬卯": "死", "壬辰": "墓庫", "壬巳": "絕", "壬午": "胎", "壬未": "養",
        "乙午": "長生", "乙巳": "沐浴", "乙辰": "冠帶", "乙卯": "臨官", "乙寅": "帝旺",
        "乙丑": "衰", "乙子": "病", "乙亥": "死", "乙戌": "墓庫", "乙酉": "絕",
        "乙申": "胎", "乙未": "養", "丁酉": "長生", "丁申": "沐浴", "丁未": "冠帶",
        "丁午": "臨官", "丁巳": "帝旺", "丁辰": "衰", "丁卯": "病", "丁寅": "死",
        "丁丑": "墓庫", "丁子": "絕", "丁亥": "胎", "丁戌": "養", "己酉": "長生",
        "己申": "沐浴", "己未": "冠帶", "己午": "臨官", "己巳": "帝旺", "己辰": "衰",
        "己卯": "病", "己寅": "死", "己丑": "墓庫", "己子": "絕", "己亥": "胎",
        "己戌": "養", "辛子": "長生", "辛亥": "沐浴", "辛戌": "冠帶", "辛酉": "臨官",
        "辛申": "帝旺", "辛未": "衰", "辛午": "病", "辛巳": "死", "辛辰": "墓庫",
        "辛卯": "絕", "辛寅": "胎", "辛丑": "養", "癸卯": "長生", "癸寅": "沐浴",
        "癸丑": "冠帶", "癸子": "臨官", "癸亥": "帝旺", "癸戌": "衰", "癸酉": "病",
        "癸申": "死", "癸未": "墓庫", "癸午": "絕", "癸巳": "胎", "癸辰": "養",
    }
    # print(f"{stem_branch}")
    return cheung_sheng_dict.get(stem_branch, "")

# # Example usage
# stem_branch = "甲亥"
# cheung_sheng = get_cheung_sheng(stem_branch)
# print(f"The Cheung Sheng for {stem_branch} is {cheung_sheng}")

def get_earthly(input_string):
    if pd.isna(input_string):
        return input_string  # Return NaN if the input is NaN
    elif len(input_string) >= 2:
        return input_string[1]
    else:
        return None  # Return None if the input string is too short

# # Example usage
# input_string = "癸丑"
# second_char = get_earthly(input_string)
# if second_char is not None:
#     print(f"The second character of '{input_string}' is '{second_char}'")
# else:
#     print("The input string is too short.")

def get_heavenly(input_string):

    if pd.isna(input_string):
        return input_string  # Return NaN if the input is NaN
    elif len(input_string) >= 2:
        return input_string[0]
    else:
        return None  # Return None if the input string is too short
# # Example usage
# input_string = "癸丑"
# second_char = get_heavenly(input_string)
# if second_char is not None:
#     print(f"The second character of '{input_string}' is '{second_char}'")
# else:
#     print("The input string is too short.")



def apply_logic(base_stem, current_stem):
    # calculate cheung sheng on two stem combine
    # print(f"Converting {base_stem} and {current_stem}")
    current_cheung_sheng = get_cheung_sheng(get_heavenly(base_stem) + get_earthly(current_stem))
    # print(f"dresult 長 {current_cheung_sheng}")
    return current_cheung_sheng



def create_chengseng_for_dataset(data_for_analytics_):
    print("Creating 長生")

    column_index = {
        'base_sets': ["本時", "本日", "-本時", "本月", "本年", "-本月"],
        'current_sets': ["流時", "流日", "-流時", "流月", "流年", "-流月", '時運', '日運', '-日運', '-時運', '月運', '年運', '-年運', '-月運', ]
    }
    data_for_analytics = data_for_analytics_.copy()

    # for index, row in data_for_analytics.iterrows():
    for base_stem_name in column_index['base_sets']:
        for current_stem_name in column_index['current_sets']:
            col_name ="長_" + base_stem_name + "_" + current_stem_name
            heaven = data_for_analytics[base_stem_name].apply(get_heavenly)
            earth = data_for_analytics[current_stem_name].apply(get_earthly)
            data_for_analytics[col_name] = heaven + earth
            data_for_analytics[col_name] = data_for_analytics[col_name].apply(get_cheung_sheng)
            print(f"Creating {col_name}")
    return data_for_analytics