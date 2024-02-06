import logging
from app import bazi
import numpy as np
import itertools

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


def base_add_haap_features_to_df(df, columns_to_initialize, columns_to_combine, haap_style="合"):
    happ_df = df.copy()
    
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
               happ_df.at[index, haap_style + '_' + ''.join(results_combined)] = 1 # Set the default value to np.nan
               happ_df.at[index, haap_style + '_' + ''.join(set(''.join(results_combined)))] = 1 # Set the default value to np.nan
            else:
                logger.debug(haap_style + ''.join(results_combined))
                
    return happ_df

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
    haap_style = "相刑"
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
    haap_style = "相衝"
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
    haap_style = "相破"
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
    haap_style = "相害"
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

