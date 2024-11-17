import logging
from app import bazi
import numpy as np
import itertools
import pandas as pd
from tqdm import tqdm


__name__ = "haap"

# Configure logging settings
logging.basicConfig(level=logging.debug,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)


# 地支相刑						
# 寅刑巳，巳刑申，申刑寅，為無恩之刑。						
# 未刑丑，丑刑戌，戌刑未，為持勢之刑。						
# 子刑卯，卯刑子，為無禮之刑。						
# 辰刑辰，午刑午，酉刑酉，亥刑亥，為自刑之刑。						
						
# 地支相衝						
# 子午相衝，丑未相衝，寅申相衝，卯酉相衝，辰戌相衝，巳亥相衝。						
						
# 地支相破						
# 子酉相破，午卯相破，巳申相破，寅亥相破，辰丑相破，戌未相破。						
# 地支相害						
# 子未相害，丑午相害，寅巳相害，卯辰相害，申亥相害，酉戌相害。						
						
# 地支六合						
# 子丑合化土	寅亥合化木	卯戌合化火	辰酉合化金	巳申合化水	午未為陰陽中正合化土。	
						
						
# 地支三合						
# 申子辰合成水局	巳酉丑合成金局	寅午戌合成火局	亥卯未合成木局。	
# 

def base_add_haap_features_to_df(df, columns_to_initialize, columns_to_combine, haap_style="合"):
  # Create a copy of the dataframe
  happ_df = df.copy()
  
  # Pre-calculate all 地支 columns at once using vectorized operations
  for col in columns_to_initialize:
      if col in df.columns:
          happ_df[col + '_地支'] = df[col].astype(str).str[-1]
  
  # Initialize dictionary for combination columns
  combination_columns = {}
  
  with tqdm(total=len(df), desc=f"Processing rows - {haap_style}") as pbar:
      for chunk_start in range(0, len(df), chunk_size):
          chunk_end = min(chunk_start + chunk_size, len(df))
          chunk_indices = df.index[chunk_start:chunk_end]
          
          # Process each combination pattern
          for combine_col in columns_to_combine:
              # Count required occurrences for each 地支 in combine_col
              required_counts = {}
              for char in combine_col:
                  required_counts[char] = required_counts.get(char, 0) + 1
              
              for idx in chunk_indices:
                  found_counts = {}
                  results_combined = []
                  
                  for col in columns_to_initialize:
                      if col in happ_df.columns:
                          # Convert to string and get the value explicitly
                          last_char = str(happ_df.at[idx, col + '_地支'])
                          
                          # Check if it's a valid string before comparing
                          if isinstance(last_char, str) and last_char in combine_col:
                              current_count = found_counts.get(last_char, 0)
                              required_count = required_counts.get(last_char, 0)
                              
                              if current_count < required_count:
                                  results_combined.append(last_char)
                                  found_counts[last_char] = current_count + 1
                  
                  if len(results_combined) > 1:
                      valid_combination = True
                      for char, required_count in required_counts.items():
                          if found_counts.get(char, 0) != required_count:
                              valid_combination = False
                              break
                      
                      if valid_combination:
                          col_name = f"{haap_style}_{''.join(combine_col)}"
                          if col_name not in combination_columns:
                              combination_columns[col_name] = np.zeros(len(df), dtype=int)
                          combination_columns[col_name][happ_df.index.get_loc(idx)] = 1
          
          pbar.update(chunk_end - chunk_start)
  
  # Add all combination columns at once
  for col_name, values in combination_columns.items():
      happ_df[col_name] = values
  
  return happ_df

def zzzzzzbase_add_haap_features_to_df(df, columns_to_initialize, columns_to_combine, haap_style="合"):
    # Create a copy of the dataframe
    happ_df = df.copy()
    
    # Pre-calculate all 地支 columns at once using vectorized operations
    for col in columns_to_initialize:
        if col in df.columns:
            happ_df[col + '_地支'] = df[col].astype(str).str[-1]
    
    # Initialize dictionary for combination columns
    combination_columns = {}
    
    # Process rows in chunks for better performance
    chunk_size = 1000
    
    with tqdm(total=len(df), desc=f"Processing rows - {haap_style}") as pbar:
        for chunk_start in range(0, len(df), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(df))
            chunk_indices = df.index[chunk_start:chunk_end]
            
            # Process each combination pattern
            for combine_col in columns_to_combine:
                # Count required occurrences for each 地支 in combine_col
                required_counts = {}
                for char in combine_col:
                    required_counts[char] = required_counts.get(char, 0) + 1
                
                # Create mask for matching characters
                for idx in chunk_indices:
                    # Dictionary to keep track of found occurrences
                    found_counts = {}
                    results_combined = []
                    
                    # Check each column for matches
                    for col in columns_to_initialize:
                        if col in happ_df.columns:
                            last_char = happ_df.at[idx, col + '_地支']
                            if last_char in combine_col:
                                # Only add if we haven't reached the required count
                                current_count = found_counts.get(last_char, 0)
                                required_count = required_counts.get(last_char, 0)
                                
                                if current_count < required_count:
                                    results_combined.append(last_char)
                                    found_counts[last_char] = current_count + 1
                    
                    # If we found multiple matches according to the required pattern
                    if len(results_combined) > 1:
                        # Verify that we have the correct counts for each character
                        valid_combination = True
                        for char, required_count in required_counts.items():
                            if found_counts.get(char, 0) != required_count:
                                valid_combination = False
                                break
                        
                        if valid_combination:
                            col_name = f"{haap_style}_{''.join(combine_col)}"
                            if col_name not in combination_columns:
                                combination_columns[col_name] = np.zeros(len(df), dtype=int)
                            combination_columns[col_name][happ_df.index.get_loc(idx)] = 1
                            
                            logger.debug(f"Found valid combination at index {idx}: {results_combined}")
                            logger.debug(f"Required counts: {required_counts}")
                            logger.debug(f"Found counts: {found_counts}")
            
            pbar.update(chunk_end - chunk_start)
    
    # Add all combination columns at once
    for col_name, values in combination_columns.items():
        happ_df[col_name] = values
    
    return happ_df


def zzzzzbase_add_haap_features_to_df(df, columns_to_initialize, columns_to_combine, haap_style="合"):
  # Create a copy of the dataframe
  happ_df = df.copy()
  
  # Pre-calculate all 地支 columns at once using vectorized operations
  for col in columns_to_initialize:
      if col in df.columns:
          happ_df[col + '_地支'] = df[col].astype(str).str[-1]
  
  # Initialize dictionary for combination columns
  combination_columns = {}
  
  # Process rows in chunks for better performance
  chunk_size = 1000
  total_chunks = (len(df) + chunk_size - 1) // chunk_size
  
  with tqdm(total=len(df), desc=f"Processing rows - {haap_style}") as pbar:
      for chunk_start in range(0, len(df), chunk_size):
          chunk_end = min(chunk_start + chunk_size, len(df))
          chunk_indices = df.index[chunk_start:chunk_end]
          
          # Process each combination pattern
          for combine_col in columns_to_combine:
              # Create mask for matching characters
              for idx in chunk_indices:
                  results_combined = []
                  
                  # Check each column for matches
                  for col in columns_to_initialize:
                      if col in happ_df.columns:
                          last_char = happ_df.at[idx, col + '_地支']
                          if last_char in combine_col:
                              results_combined.append(last_char)
                  
                  # If we found multiple matches, record the combination
                  if len(results_combined) > 1:
                      col_name = f"{haap_style}_{''.join(sorted(set(results_combined)))}"
                      if col_name not in combination_columns:
                          # Initialize with zeros for all rows
                          combination_columns[col_name] = np.zeros(len(df), dtype=int)
                      # Set 1 only for this specific index
                      combination_columns[col_name][happ_df.index.get_loc(idx)] = 1
          
          pbar.update(chunk_end - chunk_start)
  
  # Add all combination columns at once
  for col_name, values in combination_columns.items():
      happ_df[col_name] = values
      
  # Verify the distribution of values
  for col in happ_df.columns:
      if col.startswith(haap_style):
          logger.debug(f"\nColumn {col} value counts:\n{happ_df[col].value_counts()}")
  
  return happ_df
		

def zzzz_base_add_haap_features_to_df(df, columns_to_initialize, columns_to_combine, haap_style="合"):
  # Create a copy of the dataframe
  happ_df = df.copy()
  
  # Pre-calculate all 地支 columns at once using vectorized operations
  for col in columns_to_initialize:
      if col in df.columns:
          happ_df[col + '_地支'] = df[col].astype(str).str[-1]
  
  # Initialize dictionary for combination columns
  combination_columns = {}
  
  # Process rows in chunks for better performance
  chunk_size = 1000
  total_chunks = (len(df) + chunk_size - 1) // chunk_size
  
  with tqdm(total=len(df), desc=f"Processing rows - {haap_style}") as pbar:
      for chunk_start in range(0, len(df), chunk_size):
          chunk_end = min(chunk_start + chunk_size, len(df))
          chunk_indices = df.index[chunk_start:chunk_end]
          
          # Process each combination pattern
          for combine_col in columns_to_combine:
              # Create mask for matching characters
              for idx in chunk_indices:
                  results_combined = []
                  
                  # Check each column for matches
                  for col in columns_to_initialize:
                      if col in happ_df.columns:
                          last_char = happ_df.at[idx, col + '_地支']
                          if last_char in combine_col:
                              results_combined.append(last_char)
                  
                  # If we found multiple matches, record the combination
                  if len(results_combined) > 1:
                      col_name = f"{haap_style}_{''.join(sorted(set(results_combined)))}"
                      if col_name not in combination_columns:
                          combination_columns[col_name] = np.zeros(len(df), dtype=int)
                      combination_columns[col_name][chunk_start:chunk_end] = 1
          
          pbar.update(chunk_end - chunk_start)
  
  # Add all combination columns at once
  for col_name, values in combination_columns.items():
      happ_df[col_name] = values
  
  return happ_df

def zzz_base_add_haap_features_to_df(df, columns_to_initialize, columns_to_combine, haap_style="合"):
    happ_df = df.copy()

    # Create a dictionary to store all new columns and their values
    new_columns = {}
    # Create progress bar for the outer loop
    total_rows = len(happ_df)
    with tqdm(total=total_rows, desc="Processing rows - " + haap_style) as pbar:
        # Iterate through each row
        for index, row in happ_df.iterrows():
            for combine_col in columns_to_combine: 
                results_combined = []
                is_haap = False
                for col in columns_to_initialize:
                    # Check if the column exists in the DataFrame
                    if col in row.index:
                        # Split the first and last characters
                        first_char = str(row[col])[0]
                        last_char = str(row[col])[-1]
                        # Store new column values in dictionary instead of direct assignment
                        col_name = col + '_地支'

                        if col_name not in new_columns:
                            new_columns[col_name] = {}
                        new_columns[col_name][index] = last_char

                        if last_char in combine_col:
                            results_combined.append(last_char)
                            is_haap = True
                            logger.debug(f'{last_char} is in {combine_col} and added to results_combined')
                        else:
                            logger.debug(f'{last_char} is not in {combine_col} and added to results_combined and is_haap is {is_haap}')       
                        # Create new columns with the separated characters
                        # happ_df.at[index, col + '_地支'] = last_char
                logger.debug(f'results_combined: {results_combined}')
                    
                if len(results_combined) > 1:
                    # Store combined results in dictionary
                    # col_name1 = haap_style + '_' + ''.join(results_combined)
                    col_name2 = haap_style + '_' + ''.join(set(''.join(results_combined)))
                    
                    # if col_name1 not in new_columns:
                    #     new_columns[col_name1] = {}
                    if col_name2 not in new_columns:
                        new_columns[col_name2] = {idx: 0 for idx in happ_df.index}  # Initialize with 0s
                        
                    # new_columns[col_name1][index] = 1
                    new_columns[col_name2][index] = 1
                    logger.debug( col_name2 )
                else:
                    logger.debug(haap_style + ''.join(results_combined))

                # After the loop, create new columns all at once
                for col_name, values in new_columns.items():
                    happ_df[col_name] = pd.Series(values)  

                #     if last_char in combine_col:
                #         results_combined.append(last_char)
                #         is_haap = True
                #         logger.debug(f'{last_char} is in {combine_col} and added to results_combined')
                #     else:
                #         logger.debug(f'{last_char} is not in {combine_col} and added to results_combined and is_haap is {is_haap}')
                # logger.debug(f'results_combined: {results_combined}')
                # if len(results_combined) > 1:
                #    happ_df[index, haap_style + '_' + ''.join(results_combined)] = 1 # Set the default value to np.nan
                #    happ_df[index, haap_style + '_' + ''.join(set(''.join(results_combined)))] = 1 # Set the default value to np.nan
                # else:
                #     logger.debug(haap_style + ''.join(results_combined))
            # Update progress bar
            pbar.update(1)               
    return happ_df



def zz_base_add_haap_features_to_df(df, columns_to_initialize, columns_to_combine, haap_style="合"):
    happ_df = df.copy()
    new_columns = []
    
    # Iterate through each row
    for index, row in happ_df.iterrows():
        for combine_col in columns_to_combine: 
            results_combined = []
            is_haap = False
            for col in columns_to_initialize:
                # Check if the column exists in the DataFrame
                if col in row.index:
                    # Split the first and last characters
                    first_char = str(row[col])[0]
                    last_char = str(row[col])[-1]
                    
                    # Create new columns with the separated characters
                    happ_df.at[index, col + '_地支'] = last_char
                if last_char in combine_col:
                    results_combined.append(last_char)
                    is_haap = True
                    logger.debug(f'{last_char} is in {combine_col} and added to results_combined')
                else:
                    logger.debug(f'{last_char} is not in {combine_col} and added to results_combined and is_haap is {is_haap}')
            logger.debug(f'results_combined: {results_combined}')
            if len(results_combined) > 1:
                new_column_name = haap_style + '_' + ''.join(results_combined)
                happ_df[new_column_name] = 1
                new_columns.append(new_column_name)
                new_column_name_unique = haap_style + '_' + ''.join(set(''.join(results_combined)))
                happ_df[new_column_name_unique] = 1
                new_columns.append(new_column_name_unique)
            else:
                logger.debug(haap_style + '_' + ''.join(results_combined) + ' is {happ_df["合_" + ''.join(results_combined)]}')
                
    return pd.concat([happ_df, pd.DataFrame(columns=new_columns)], axis=1)


def add_haap_features_to_df(df):

    # 地支三合						
    # 申子辰合成水局	巳酉丑合成金局	寅午戌合成火局	亥卯未合成木局。	
    # columns_to_initialize = ['本時', '本日', '-本時', '本月', '本年', '-本月', '流時', '流日', '-流時', '流月', '流年', '-流月']
    # # happ_df = df.copy()
    # columns_巳酉丑_to_combine = ['巳', '酉', '丑']
    # columns_申子辰_to_combine = ['申', '子', '辰']
    # columns_寅午戌_to_combine = ['寅', '午', '戌']
    # columns_亥卯未_to_combine = ['亥', '卯', '未']
    # combine_columns = [columns_巳酉丑_to_combine, columns_申子辰_to_combine, columns_寅午戌_to_combine, columns_亥卯未_to_combine]
    # haap_style = "三合"
    # # Iterate through each row
    # for index, row in happ_df.iterrows():
    #     for combine_col in combine_columns: 
    #         results_combined = []
    #         is_haap = False
    #         for col in columns_to_initialize:
    #             # Check if the column exists in the DataFrame
    #             if col in row.index:
    #                 # Split the first and last characters
    #                 first_char = str(row[col])[0]
    #                 last_char = str(row[col])[-1]
                    
    #                 # Create new columns with the separated characters
    #                 # happ_df.at[index, col + '_first'] = first_char
    #                 happ_df.at[index, col + '_地支'] = last_char
    #             if last_char in combine_col:
    #                 results_combined.append(last_char)
    #                 is_haap = True
    #                 logger.debug(f'{last_char} is in {combine_col} and added to results_combined')
    #             else:
    #                 # results_combined.append('')
    #                 logger.debug(f'{last_char} is not in {combine_col} and added to results_combined and is_haap is {is_haap}')
    #         logger.debug(f'results_combined: {results_combined}')
    #         if len(results_combined) > 1:
    #            happ_df.at[index, '合_' + ''.join(results_combined)] = 1 # Set the default value to np.nan
    #            happ_df.at[index, '合_' + ''.join(set(''.join(results_combined)))] = 1 # Set the default value to np.nan
    #         else:
    #             logger.debug(f'合_' + ''.join(results_combined) + ' is {happ_df["合_" + ''.join(results_combined)]}')
                
    # happ_df = base_add_haap_features_to_df(df, columns_to_initialize, combine_columns, haap_style)
    # List of columns for 合 testing
    

    # # Function to calculate 合 and return the result
    # def calculate_he(column_values):
    #     return ''.join(column_values)

    # # Generate all possible combinations of columns_to_combine
    # combinations = list(itertools.product(*[happ_df[col] for col in columns_to_combine]))

    # # Create a new column with the 合 result for each combination
    # for i, combination in enumerate(combinations):
    #     combination_name = '_'.join(['合'] + list(combination) + [str(i + 1)])
    #     happ_df[combination_name] = happ_df.apply(lambda row: calculate_he([row[col] for col in combination]), axis=1)

    # Display the modified DataFrame


    # 地支相刑						
    # 寅刑巳，巳刑申，申刑寅，為無恩之刑。						
    # 未刑丑，丑刑戌，戌刑未，為持勢之刑。						
    # 子刑卯，卯刑子，為無禮之刑。						
    # 辰刑辰，午刑午，酉刑酉，亥刑亥，為自刑之刑。						
    columns_to_initialize = ['本時', '本日', '-本時', '本月', '本年', '-本月', '流時', '流日', '-流時', '流月', '流年', '-流月']
    columns_1_to_combine = ['寅', '巳']
    columns_2_to_combine = ['巳', '申']
    columns_3_to_combine = ['申', '寅']
    columns_4_to_combine = ['未', '丑']
    columns_5_to_combine = ['丑', '戌']
    columns_6_to_combine = ['戌', '未']
    columns_4_to_combine = ['子', '卯']
    columns_5_to_combine = ['卯', '子']
    columns_6_to_combine = ['辰', '辰']
    columns_7_to_combine = ['午', '午']
    columns_8_to_combine = ['酉', '酉']
    columns_9_to_combine = ['亥', '亥']
    combine_columns = [columns_1_to_combine, columns_2_to_combine, columns_3_to_combine, columns_4_to_combine,columns_5_to_combine, columns_6_to_combine, columns_7_to_combine, columns_8_to_combine, columns_9_to_combine]
    haap_style = "刑"
    happ_df = base_add_haap_features_to_df(df, columns_to_initialize, combine_columns, haap_style)


    # 地支相衝						
    # 子午相衝，丑未相衝，寅申相衝，卯酉相衝，辰戌相衝，巳亥相衝。						
    columns_to_initialize = ['本時', '本日', '-本時', '本月', '本年', '-本月', '流時', '流日', '-流時', '流月', '流年', '-流月']
    columns_1_to_combine = ['子', '午']
    columns_2_to_combine = ['丑', '未']
    columns_3_to_combine = ['寅', '申']
    columns_4_to_combine = ['卯', '酉']
    columns_5_to_combine = ['辰', '戌']
    columns_6_to_combine = ['巳', '亥']
    combine_columns = [columns_1_to_combine, columns_2_to_combine, columns_3_to_combine, columns_4_to_combine,columns_5_to_combine, columns_6_to_combine]
    haap_style = "衝"
    happ_df = base_add_haap_features_to_df(happ_df, columns_to_initialize, combine_columns, haap_style)

                    
    # 地支相破						
    # 子酉相破，午卯相破，巳申相破，寅亥相破，辰丑相破，戌未相破。			
    columns_to_initialize = ['本時', '本日', '-本時', '本月', '本年', '-本月', '流時', '流日', '-流時', '流月', '流年', '-流月']
    columns_1_to_combine = ['子', '酉']
    columns_2_to_combine = ['午', '卯']
    columns_3_to_combine = ['巳', '申']
    columns_4_to_combine = ['寅', '亥']
    columns_5_to_combine = ['辰', '丑']
    columns_6_to_combine = ['戌', '未']
    combine_columns = [columns_1_to_combine, columns_2_to_combine, columns_3_to_combine, columns_4_to_combine,columns_5_to_combine, columns_6_to_combine]
    haap_style = "破"
    happ_df = base_add_haap_features_to_df(happ_df, columns_to_initialize, combine_columns, haap_style)


    # 地支相害						
    # 子未相害，丑午相害，寅巳相害，卯辰相害，申亥相害，酉戌相害。						
    columns_to_initialize = ['本時', '本日', '-本時', '本月', '本年', '-本月', '流時', '流日', '-流時', '流月', '流年', '-流月']
    columns_1_to_combine = ['子', '未']
    columns_2_to_combine = ['丑', '午']
    columns_3_to_combine = ['寅', '巳']
    columns_4_to_combine = ['卯', '辰']
    columns_5_to_combine = ['申', '亥']
    columns_6_to_combine = ['酉', '戌']
    combine_columns = [columns_1_to_combine, columns_2_to_combine, columns_3_to_combine, columns_4_to_combine,columns_5_to_combine, columns_6_to_combine]
    haap_style = "害"
    happ_df = base_add_haap_features_to_df(happ_df, columns_to_initialize, combine_columns, haap_style)
                      
    # 地支六合						
    # 子丑合化土	寅亥合化木	卯戌合化火	辰酉合化金	巳申合化水	午未為陰陽中正合化土。	
    columns_to_initialize = ['本時', '本日', '-本時', '本月', '本年', '-本月', '流時', '流日', '-流時', '流月', '流年', '-流月']
    columns_1_to_combine = ['子', '丑']
    columns_2_to_combine = ['寅', '亥']
    columns_3_to_combine = ['卯', '戌']
    columns_4_to_combine = ['辰', '酉']
    columns_5_to_combine = ['巳', '申']
    columns_6_to_combine = ['午', '未']
    combine_columns = [columns_1_to_combine, columns_2_to_combine, columns_3_to_combine, columns_4_to_combine,columns_5_to_combine, columns_6_to_combine]
    haap_style = "六合"
    happ_df = base_add_haap_features_to_df(happ_df, columns_to_initialize, combine_columns, haap_style)


    # 地支三合						
    # 申子辰合成水局	巳酉丑合成金局	寅午戌合成火局	亥卯未合成木局。	
    columns_to_initialize = ['本時', '本日', '-本時', '本月', '本年', '-本月', '流時', '流日', '-流時', '流月', '流年', '-流月']
    # happ_df = df.copy()
    columns_巳酉丑_to_combine = ['巳', '酉', '丑']
    columns_申子辰_to_combine = ['申', '子', '辰']
    columns_寅午戌_to_combine = ['寅', '午', '戌']
    columns_亥卯未_to_combine = ['亥', '卯', '未']
    combine_columns = [columns_巳酉丑_to_combine, columns_申子辰_to_combine, columns_寅午戌_to_combine, columns_亥卯未_to_combine]
    haap_style = "三合"
    happ_df = base_add_haap_features_to_df(happ_df, columns_to_initialize, combine_columns, haap_style)


    return happ_df

