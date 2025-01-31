from datetime import datetime, timedelta
from fastapi import FastAPI
from app  import bazi
from app import chengseng
import logging

import concurrent.futures
from tqdm import tqdm
import random
import pandas as pd
import pytz
from typing import List


app = FastAPI()
__name__ = "four_pillar"

# Configure logging settings
logging.basicConfig(level=logging.DEBUG,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"message":  bazi.HeavenlyStem.JIA.name + " " + str(bazi.HeavenlyStem.JIA.value) + " " + str(bazi.EarthlyBranchCN[bazi.EarthlyBranch.MAO.name].value)}


@app.get("/year/{year}")
def get_heavenly_branch_y(year: int):
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, 1,1)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem), "Earthly Branch": bazi.resolveEarthlyBranch(earthly_branch)}

@app.get("/year_january_heavenly_stem/{year}")
def get_heavenly_branch(year: int):
    heavenly_stem = bazi.calculate_month_heavenly(year, 0)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem)}


@app.get("/year/{year}/month/{month}")
def get_heavenly_branch_ym(year: int, month: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly(year, month-1)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month-1,1)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem), 
            "Earthly Branch": bazi.resolveEarthlyBranch(earthly_branch), 
            "Heavenly Month Stem": bazi.resolveHeavenlyStem(heavenly_month_stem),
            "Earthly Month Stem": bazi.resolveEarthlyBranch(earthly_month_stem)
            }


@app.get("/year/{year}/month/{month}/day/{day}")
def get_heavenly_branch_ymd(year: int, month: int, day: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly(year, month)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month,1)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly(year, month, day, 9, 15)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem), 
            "Earthly Branch": bazi.resolveEarthlyBranch(earthly_branch), 
            "Heavenly Month Stem": bazi.resolveHeavenlyStem(heavenly_month_stem),
            "Earthly Month Stem": bazi.resolveEarthlyBranch(earthly_month_stem),
            "Heavenly Day Stem": bazi.resolveHeavenlyStem(heavenly_day_stem),
            "Earthly Day Stem": bazi.resolveEarthlyBranch(earthly_day_stem)
            }


@app.get("/year/{year}/month/{month}/day/{day}/hour/{hour}")
def get_heavenly_branch_ymdh(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly(year, month)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month, day)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly(year, month, day, 9, 15)
    heavenly_hour_stem, earthly_hour_stem = bazi.calculate_hour_heavenly(year, month, day, hour)
    return {"Heavenly Stem": bazi.resolveHeavenlyStem(heavenly_stem), 
            "Earthly Branch": bazi.resolveEarthlyBranch(earthly_branch), 
            "Heavenly Month Stem": bazi.resolveHeavenlyStem(heavenly_month_stem),
            "Earthly Month Stem": bazi.resolveEarthlyBranch(earthly_month_stem),
            "Heavenly Day Stem": bazi.resolveHeavenlyStem(heavenly_day_stem),
            "Earthly Day Stem": bazi.resolveEarthlyBranch(earthly_day_stem),
            "Heavenly Hour Stem": bazi.resolveHeavenlyStem(heavenly_hour_stem),
            "Earthly Hour Stem": bazi.resolveEarthlyBranch(earthly_hour_stem)
            }


@app.get("/luna_year/{from_year}/to_year/{to_year}")
def get_heavenly_branch_yy(from_year: int, to_year: int):

    current_date = datetime.date(from_year, 1, 1)
    end_date = datetime.date(to_year, 12, 31)

    while current_date <= end_date:
       # Do something with the current_date
        logger.debug(current_date.strftime("YYYY-MM-DD"))
        # Move to the next day
        current_date += datetime.timedelta(days=1)



# Calculate for normal 8w
def get_heavenly_branch_ymdh_pillars_base(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly_withSeason_for_baselife_time(year, month,day, hour)
    dark_month_stem = bazi.calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month, day)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly_base(year, month, day, hour, 15)
    heavenly_hour_stem, earthly_hour_stem = bazi.calculate_hour_heavenly(year, month, day, hour)
    dark_hour_stem = bazi.calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem )
    
    
    return {
            "時": bazi.resolveHeavenlyStem(heavenly_hour_stem) + bazi.resolveEarthlyBranch(earthly_hour_stem),
            "日": bazi.resolveHeavenlyStem(heavenly_day_stem) + bazi.resolveEarthlyBranch(earthly_day_stem),
            "-時": dark_hour_stem,
            "月": bazi.resolveHeavenlyStem(heavenly_month_stem) + bazi.resolveEarthlyBranch(earthly_month_stem),
            "年": bazi.resolveHeavenlyStem(heavenly_stem) + bazi.resolveEarthlyBranch(earthly_branch), 
            "-月": dark_month_stem,
           }

# Calculate for normal 8w
def get_heavenly_branch_ymdh_pillars_current(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly_withSeason_for_baselife_time(year, month,day, hour)
    dark_month_stem = bazi.calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month, day)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly_base(year, month, day, hour, 13)
    heavenly_hour_stem, earthly_hour_stem = bazi.calculate_hour_heavenly(year, month, day, hour)
    dark_hour_stem = bazi.calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem )
    

    
    return {
            "時": bazi.resolveHeavenlyStem(heavenly_hour_stem) + bazi.resolveEarthlyBranch(earthly_hour_stem),
            "日": bazi.resolveHeavenlyStem(heavenly_day_stem) + bazi.resolveEarthlyBranch(earthly_day_stem),
            "-時": dark_hour_stem,
            "月": bazi.resolveHeavenlyStem(heavenly_month_stem) + bazi.resolveEarthlyBranch(earthly_month_stem),
            "年": bazi.resolveHeavenlyStem(heavenly_stem) + bazi.resolveEarthlyBranch(earthly_branch), 
            "-月": dark_month_stem,
           }



# Calculate for normal 8w
def get_heavenly_branch_ymdh_pillars(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly_withSeason_for_baselife_time(year, month, day, hour)(year, month,day)
    dark_month_stem = bazi.calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month, day)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly_with_half(year, month, day, hour, 15)
    heavenly_hour_stem, earthly_hour_stem = bazi.calculate_hour_heavenly(year, month, day, hour)
    dark_hour_stem = bazi.calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem )
    
    
    return {
            "時": bazi.resolveHeavenlyStem(heavenly_hour_stem) + bazi.resolveEarthlyBranch(earthly_hour_stem),
            "日": bazi.resolveHeavenlyStem(heavenly_day_stem) + bazi.resolveEarthlyBranch(earthly_day_stem),
            "-時": dark_hour_stem,
            "月": bazi.resolveHeavenlyStem(heavenly_month_stem) + bazi.resolveEarthlyBranch(earthly_month_stem),
            "年": bazi.resolveHeavenlyStem(heavenly_stem) + bazi.resolveEarthlyBranch(earthly_branch), 
            "-月": dark_month_stem,
           }





# Calculate with normal 8w and split
def get_heavenly_branch_ymdh_splitpillars(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly_withSeason_for_current_time(year, month)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month,1)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly_with_half(year, month, day, hour, 15)
    heavenly_hour_stem, earthly_hour_stem = bazi.calculate_hour_heavenly(year, month, day, hour)
    return {"年天": bazi.resolveHeavenlyStem(heavenly_stem), 
            "年地": bazi.resolveEarthlyBranch(earthly_branch), 
            "月天": bazi.resolveHeavenlyStem(heavenly_month_stem),
            "月地": bazi.resolveEarthlyBranch(earthly_month_stem),
            "日天": bazi.resolveHeavenlyStem(heavenly_day_stem),
            "日地": bazi.resolveEarthlyBranch(earthly_day_stem),
            "時天": bazi.resolveHeavenlyStem(heavenly_hour_stem),
            "時地": bazi.resolveEarthlyBranch(earthly_hour_stem)
            }



# 戊辰
year=2023
month =8
day = 30
hour =9
minute = 15

# 壬子
# year=1996
# month =1
# day = 16
# hour =13
# minute = 15

#己丑
# year=1997
# month =2
# day = 16
# hour =13
# minute = 15

# 壬戌
# year=1998
# month =3
# day = 16
# hour =13
# minute = 15

# 戊戌
# year=1999
# month =4
# day = 16
# hour =13
# minute = 15



# 1/3/2019 - 丁丑	庚子	壬午	庚辰	戊戌	乙酉

# 癸丑
year=2019
month =1
day = 3
hour =9
minute = 15

# 1/13/2019 - 戊子	乙丑	癸巳	乙丑	戊戌	庚午
year=2019
month =1
day = 13
hour =9
minute = 15

# 7/5/2021 - 壬申	己巳	丁卯	己酉	辛丑	甲辰
year=2019
month =7
day = 5
hour =9
minute = 15

# 6/22/2022 - 己亥	辛酉	甲午	辛酉	壬寅	丙辰
year=2019
month =6
day = 33
hour =9
minute = 15

# 3/4/2023 - 壬辰	辛酉	丁酉	己巳	癸卯	甲戌
year=2023
month =3
day = 4
hour =9
minute = 15

# 8/12/2023 - 辛丑	壬寅	丙午	庚申	癸卯	乙卯
# year=2023
# month =8
# day = 12
# hour =9
# minute = 15

# 4/27/1979- 辛丑	壬寅	丙午	庚申	癸卯	乙卯
# year=1979   
# month =4
# day = 27
# hour =13
# minute = 15

# 8/20/2023- 辛丑	壬寅	丙午	庚申	癸卯	乙卯
year=2023  
month =8
day = 20
hour =9
minute = 15

# 9/9/2023- 辛巳	庚午	丙午	辛酉	癸卯	乙卯
year=2019 
month =4
day = 5
hour =9
minute = 15

# 公元2023年09月23日 農歷08月(大)09日 星期六 天秤座
# 歲次：癸卯年、生肖屬兔、辛酉月、甲申日
year = 2023
month = 9
day = 23
hour = 13

# # My
# # 歲次：
# year = 1979
# month = 4
# day = 27
# hour = 13


# # My
# # 歲次：
# year = 2023
# month = 12
# day =2
# hour = 13


# # result = get_heavenly_branch_ymdh_pillars_base(year, month, day, hour)

# # logger.info (result)

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)

# bazi.get_Luna_Month_With_Season(datetime(2023, 12, 21, 9, 0, 0))
# bazi.get_Luna_Month_With_Season(datetime(2023, 12, 24, 9, 0, 0))
# bazi.get_Luna_Month_With_Season(datetime(2024, 1, 4, 9, 0, 0))
# bazi.get_Luna_Month_With_Season(datetime(2024, 1, 6, 9, 0, 0))
# bazi.get_Luna_Month_With_Season(datetime(2024, 1, 8, 9, 0, 0))
# bazi.get_Luna_Month_With_Season(datetime(2024, 1, 16, 9, 0, 0))
# bazi.get_Luna_Month_With_Season(datetime(2024, 1, 22, 9, 0, 0))
# bazi.get_Luna_Month_With_Season(datetime(2024, 2, 1, 9, 0, 0))

# # My
# # 歲次：
year = 1979
month = 4
day =27
hour = 13

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
# print("##################################/n")
# year = 2023
# month = 12
# day =19
# hour = 11

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")
# year = 2023
# month = 12
# day =22
# hour = 11

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")
# year = 2023
# month = 12
# day =23
# hour = 11

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")
# year = 2024
# month = 1
# day =19
# hour = 11

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")

# year = 2024
# month = 2
# day =3
# hour = 11

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")

# year = 2024
# month = 2
# day =9
# hour = 13

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")
# year = 2024
# month = 2
# day =10
# hour = 9

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")

# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,4,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,5,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,6,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,7,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,8,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,9,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,10,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,11,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,12,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,13,9)}")


# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,1,12,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,1,13,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,1,14,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,1,15,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,1,18,9)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,1,18,11)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,1,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,2,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,3,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,4,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,5,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,6,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,7,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,8,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,9,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,10,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,11,18,12)}")
# print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(2024,12,18,12)}")

# year = 2023
# month = 11
# day = 1

# # Create a date object
# current_date = datetime(year, month, day, 7)

# # Add timedelta of 1 day
# next_day = current_date + timedelta(days=1)

# for i in range(1, 15):
#     # Add timedelta of 1 day
#     next = current_date + timedelta(months=i)
#     print(f"################# {next.year,next.month,next.day,next.hour} #################")
#     print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(next.year,next.month,next.day , next.hour )}")
def format_bazi_output(data_dict):
    # First row: Keys
    keys = list(data_dict.keys())
    print(" ".join(f"{key:^4}" for key in keys))

    # Second and third rows: Split the values (assuming each value is 2 characters)
    values = list(data_dict.values())
    first_chars = [val[0] for val in values]
    second_chars = [val[1] for val in values]

    # Print second row (first characters)
    print(" ".join(f"{char:^4}" for char in first_chars))

    # Print third row (second characters)
    print(" ".join(f"{char:^4}" for char in second_chars))

def format_bazi_output_2(data_dict):
    # First row: Keys
    keys = list(data_dict.keys())
    print(" ".join(f"{key:<5}" for key in keys))

    # Second and third rows: Split the values
    values = list(data_dict.values())
    first_chars = [val[0] for val in values]
    second_chars = [val[1] for val in values]

    # Print second row (first characters)
    print(" ".join(f"{char:<5}" for char in first_chars))

    # Print third row (second characters)
    print(" ".join(f"{char:<5}" for char in second_chars))

def format_bazi_output_3(data_dict):
    # Define the groups - now including negative entries
    basic_keys = ['時', '日',  '-日', '-時','月', '年', '-年','-月']
    he_keys = ['合時', '合日',  '-合日', '-合時','合月', '合年', '-合年','-合月', ]
    hai_keys = ['害時', '害日', '-害日', '-害時',  '害月', '害年', '-害年', '-害月', ]
    po_keys = ['破時', '破日', '-破日','-破時' , '破月', '破年', '-破年', '-破月']

    def format_group(keys, values):
        # First two rows: keys
        first_row = []
        second_row = []
        for key in keys:
            if key in values:  # Only process if key exists in data
                if key.startswith('-'):
                    # For negative entries, show empty space in name rows
                    first_row.append("  ")
                    second_row.append("  ")
                else:
                    if len(key) == 1:
                        first_row.append(key)
                        second_row.append(" ")
                    else:
                        first_row.append(key[0])
                        second_row.append(key[-1])

        # Get values for existing keys
        third_row = []
        fourth_row = []
        for key in keys:
            if key in values:
                value = values[key]
                third_row.append(value[0])
                fourth_row.append(value[1])

        return [
            "".join(f"{char:<1}" for char in first_row),
            "".join(f"{char:<1}" for char in second_row),
            "".join(f"{char:<1}" for char in third_row),
            "".join(f"{char:<1}" for char in fourth_row)
        ]

    # Format and print each group
    groups = [
        (basic_keys, "Basic Pillars"),
        (he_keys, "He (合) Group"),
        (hai_keys, "Hai (害) Group"),
        (po_keys, "Po (破) Group")
    ]

    for keys, group_name in groups:
        rows = format_group(keys, data_dict)
        if any(row.strip() for row in rows):  # Only print if there's data
            for row in rows:
                print(row)
            print()

def get_pillar_from_dict(data_dict, pillar_type):
    """
    Extract year or month pillar from data_dict where values are strings
    pillar_type should be '年' or '月'
    """
    if pillar_type in data_dict:
        pillar = data_dict[pillar_type]
        return pillar  # Already in the format '甲子'
    return None

from datetime import datetime
from dateutil.relativedelta import relativedelta

def format_solar_terms_output(solar_terms_list):
    """
    Format solar terms list into a readable table with Chinese names

    Args:
        solar_terms_list: List of datetime objects from bazi.get_solar_terms()
    """
    # Ordered list of solar terms (節氣) - starting from 小寒
    solar_term_names = [
        "小寒 (Minor Cold)",        # 1月
        "大寒 (Major Cold)",
        "立春 (Start of Spring)",   # 2月
        "雨水 (Rain Water)",
        "驚蟄 (Awakening Insects)", # 3月
        "春分 (Spring Equinox)",
        "清明 (Pure Brightness)",   # 4月
        "穀雨 (Grain Rain)",
        "立夏 (Start of Summer)",   # 5月
        "小滿 (Grain Full)",
        "芒種 (Grain in Ear)",      # 6月
        "夏至 (Summer Solstice)",
        "小暑 (Minor Heat)",        # 7月
        "大暑 (Major Heat)",
        "立秋 (Start of Autumn)",   # 8月
        "處暑 (End of Heat)",
        "白露 (White Dew)",         # 9月
        "秋分 (Autumn Equinox)",
        "寒露 (Cold Dew)",          # 10月
        "霜降 (Frost Descent)",
        "立冬 (Start of Winter)",   # 11月
        "小雪 (Minor Snow)",
        "大雪 (Major Snow)",        # 12月
        "冬至 (Winter Solstice)"
    ]

    print("\n節氣 Solar Terms Calendar")
    print("=" * 75)
    print(f"{'#':<3} {'Date':<12} {'Time':<10} {'Solar Term':<30} {'Timezone':<20}")
    print("-" * 75)

    # Process each solar term
    for idx, dt in enumerate(solar_terms_list):
        # Get the solar term name based on position in the year
        term_idx = idx % 24  # 24 solar terms in total
        term_name = solar_term_names[term_idx]

        # Format the date, time and timezone
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M:%S")
        tz_str = str(dt.tzinfo)

        # Print the formatted line
        print(f"{idx+1:<3} {date_str:<12} {time_str:<10} {term_name:<30} {tz_str:<20}")

def generate_bazi_analysis(input_date: datetime):
    next_date = input_date
    print(f"##### {next_date.year}/{next_date.month}/{next_date.day} {next_date.hour}:00 #####")
    bazi_data = bazi.get_ymdh_current(next_date.year, next_date.month, next_date.day, next_date.hour)
    print(f"{bazi_data}")
    format_bazi_output_3(bazi_data) 
    bazi_data = bazi.get_ymdh_base(next_date.year, next_date.month, next_date.day, next_date.hour)
    print(f"{bazi_data}")
    format_bazi_output_3(bazi_data) 
    year_pillar = get_pillar_from_dict(bazi_data, '年')
    month_pillar = get_pillar_from_dict(bazi_data, '月')
    
    bazi.print_daiYun("male", year_pillar,month_pillar, input_date)

def split_pillar(pillar_str):
    """
    Split a pillar string into heavenly stem and earthly branch
    Example: '甲子' -> ('甲', '子')
    """
    return pillar_str[0], pillar_str[1]

# Assuming current_date is initialized, e.g.,
current_date = datetime(2025, 1, 7, 9)  # Example: January 1st, 2024 at 12:00
current_date = datetime(2025, 1, 7, 9)  # Example: January 1st, 2024 at 12:00
current_date = datetime(1989, 9, 28, 13)  # Example: January 1st, 2024 at 12:00
# current_date = datetime(2024, 10, 2, 9)  # Example: January 1st, 2024 at 12:00
# current_date = datetime(2022, 3, 16, 13)  # Example: January 1st, 2024 at 12:00
current_date = datetime(1979, 4, 27, 13)  # Example: January 1st, 2024 at 12:00
generate_bazi_analysis(current_date)
# current_date = datetime(2025, 1, 17, 9)  # Example: January 1st, 2024 at 12:00
# generate_bazi_analysis(current_date)


next_date = current_date 

for i in range(0, 5):
    # Add i months to current_date
    # # Assuming bazi.get_heavenly_branch_ymdh_pillars_current is a method call that you have defined or imported
    # print(f"{bazi.get_heavenly_branch_ymdh_pillars_current(next_date.year,next_date.month,next_date.day, next_date.hour)}")
    # print(f"{bazi.get_heavenly_branch_ymdh_pillars_current_flip_Option_2(next_date.year,next_date.month,next_date.day, next_date.hour)}")
    # bazi_data = bazi.get_heavenly_branch_ymdh_pillars_current_flip_Option_2(next_date.year, next_date.month, next_date.day, next_date.hour)
    # print(f"##### {next_date.year}/{next_date.month}/{next_date.day} {next_date.hour}:00 #####")
    # format_bazi_output_3(bazi_data) 
    # generate_bazi_analysis(next_date)
    next_date = current_date + relativedelta(days=i)
    # next_date = current_date + relativedelta(hour=i)
    # 

print(f"{format_solar_terms_output(bazi.get_solar_terms(1979))}") 



# Example datetime
current_time = datetime(1979, 4, 27, 13, 30, tzinfo=pytz.timezone('Asia/Shanghai'))
solar_terms = bazi.get_solar_terms(1979)  # Your existing solar terms list

days, next_term, term_name = bazi.find_days_to_next_solar_term(current_time, solar_terms)

print(f"\nCurrent time: {current_time}")
print(f"Next solar term: {next_term} - {term_name}")
print(f"Days until next solar term: {days:.2f} days")

# year = 2023
# month = 11
# day =7
# hour = 0

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")

# year = 2023
# month = 11
# day =8
# hour = 23

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")

# year = 2023
# month = 11
# day =9
# hour = 0

# result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
# logger.info (result)
# print("##################################/n")

# year = 1979
# month = 4
# day =27
# hour = 13

# result = get_heavenly_branch_ymdh_pillars_base(year, month, day, hour)
# logger.info (result)
# print("################ {'時': '辛未', '日': '甲子', '-時': '丙寅', '月': '戊辰', '年': '己未', '-月': '癸酉'} /n")

# year = 2024
# month = 1
# day =24
# hour = 0

# result = get_heavenly_branch_ymdh_pillars_base(year, month, day, hour)
# logger.info (result)
# print("################ {'時': '庚子', '日': '丁亥', '-時': '乙巳', '月': '乙丑', '年': '癸卯', '-月': '庚午'} /n")


# year = 2023
# month = 12
# day =24
# hour = 0

# result = get_heavenly_branch_ymdh_pillars_base(year, month, day, hour)
# logger.info (result)
# print("################ {'時': '戊子', '日': '丙辰', '-時': '癸巳', '月': '甲子', '年': '癸卯', '-月': '己巳'} /n")



# year = 2023
# month = 11
# day =8
# hour = 0

# result = get_heavenly_branch_ymdh_pillars_base(year, month, day, hour)
# logger.info (result)
# print("################ {'時': '丙子', '日': '庚午', '-時': '辛巳', '月': '壬戌', '年': '癸卯', '-月': '丁巳'} /n")


# year = 2023
# month = 11
# day =2
# hour = 0

# result = get_heavenly_branch_ymdh_pillars_base(year, month, day, hour)
# logger.info (result)
# print("################ {'時': '丙子', '日': '庚午', '-時': '辛巳', '月': '壬戌', '年': '癸卯', '-月': '丁巳'} /n")


# heavenly_month_stem, earthly_month_stem  = bazi.calculate_month_heavenly(year,month,day)

# logger.info(bazi.resolveHeavenlyStem(heavenly_month_stem) + bazi.resolveEarthlyBranch(earthly_month_stem))

# logger.debug(f"Year Stem is {get_heavenly_branch_y(2018)}")

# logger.debug(f"{bazi.SixtyStem(121)}")
# logger.debug(f"{bazi.getSixtyStemIndex('甲子')}")
# logger.info(f"{bazi.calculate_day_heavenly(year, month, day)}")
# logger.info(f"{bazi.calculate_day_heavenly(year, month, day)}")
# logger.info(f"{get_heavenly_branch_ymd(year, month, day)}")
# Creating a datetime object for a specific date and time
# specific_datetime = datetime(year, month,day,hour, 30, 0)  # Year, Month, Day, Hour, Minute, Second
# logger.info(f"{bazi.get_Luna_Month_With_Season(specific_datetime)}")


# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(0)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(1)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(2)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(3)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(4)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(5)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(6)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(7)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(8)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(9)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(10)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(11)))
# logger.info(bazi.resolveHeavenlyStem(bazi.get_next_half_heavenly(12)))


# Process one row of 8w

# specific_datetime = datetime(2019,4,4,9, 30, 0)  # Year, Month, Day, Hour, Minute, Second
# print(f"{bazi.get_Luna_Month_With_Season(specific_datetime)}")

# def process_8w_row(row):
#     # counting()


# try:
    
#     year = 2023
#     month = 8
#     day = 23
#     hour = 9
    
#     result_current = get_heavenly_branch_ymdh_pillars(year,month,day,hour)
# except Exception as e:
#     print("Error: {0}".format(e))
            






# # Set the maximum number of threads you want to use
# max_threads = 20 # Change this as needed

# #loop 1000 times and create an array that can iterrows later. 
# rows = []
# rows = [rows.append(1) for i in range(100000)]

# total_rows = len(rows)

#  # Create a ThreadPoolExecutor with the desired number of threads
# with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
#     # Wrap the executor with tqdm for progress tracking
#     with tqdm(total=total_rows, desc="Processing", unit="row", dynamic_ncols=True) as pbar:
#         # Submit each row for processing in parallel
#         futures = [executor.submit(process_8w_row, row) for row in range(100000)]

#         # Process completed tasks
#         for future in concurrent.futures.as_completed(futures):
#             # Update the progress bar for each completed task
#             pbar.update()

#         # Wait for all tasks to complete
#         # concurrent.futures.wait(futures)




# # Define the range of years for random dates
# start_year = 1900
# end_year = 2100

# # Generate 10000 random dates
# random_dates = [datetime(random.randint(start_year, end_year), random.randint(1, 12), random.randint(1, 28)) for _ in range(10000)]

# for target_date in random_dates:
#     solar_old , result_old = bazi.get_Luna_Month_With_Season_zz(target_date)
#     solar_new, result_new = bazi.get_Luna_Month_With_Season(target_date)

#     if result_old != result_new:
#         print(f"Mismatch for date {target_date}: Old method = {result_old}, New method = {result_new}")
        
#     if solar_old != solar_new:
#         print(f"Mismatch for date {target_date} - {result_new}: Old method = {solar_old}, New method = {solar_new}")   



# @title Step 3: Define time range
# today = datetime.now()
# # Set the time to 9:30 AM
# today = today.replace(hour=9, minute=00, second=0, microsecond=0)

# start_date = today - timedelta(days=30)
# end_date = today + timedelta(days=10)

# # @title Step 4: Create a blank data frame with time column
# time_range = pd.date_range(start=start_date, end=end_date, freq='1H').union(pd.date_range(end_date, end_date + pd.DateOffset(months=12), freq='D'))
# dataset = pd.DataFrame({'time': time_range})

# # @title Step 5: Adding 8w pillars to the dataset
# dataset = chengseng.adding_8w_pillars(dataset)

# print(dataset)