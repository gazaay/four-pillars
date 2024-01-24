from datetime import datetime, timedelta
from fastapi import FastAPI
from app  import bazi
import logging

import concurrent.futures
from tqdm import tqdm
import random



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
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly_withSeason_for_baselife_time(year, month,day)
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
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly_withSeason_for_current_time(year, month,day, hour)
    dark_month_stem = bazi.calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month, day)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly_current(year, month, day, hour, 15)
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
    heavenly_month_stem, earthly_month_stem = bazi.calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)(year, month,day)
    dark_month_stem = bazi.calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = bazi.calculate_year_heavenly(year, month, day)
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly_current(year, month, day, hour, 15)
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
    heavenly_day_stem, earthly_day_stem = bazi.calculate_day_heavenly_current(year, month, day, hour, 15)
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

bazi.get_Luna_Month_With_Season(datetime(2023, 12, 21, 9, 0, 0))
bazi.get_Luna_Month_With_Season(datetime(2023, 12, 24, 9, 0, 0))
bazi.get_Luna_Month_With_Season(datetime(2024, 1, 4, 9, 0, 0))
bazi.get_Luna_Month_With_Season(datetime(2024, 1, 6, 9, 0, 0))
bazi.get_Luna_Month_With_Season(datetime(2024, 1, 8, 9, 0, 0))
bazi.get_Luna_Month_With_Season(datetime(2024, 1, 16, 9, 0, 0))
bazi.get_Luna_Month_With_Season(datetime(2024, 1, 22, 9, 0, 0))
bazi.get_Luna_Month_With_Season(datetime(2024, 2, 1, 9, 0, 0))

# My
# 歲次：
year = 1979
month = 4
day =27
hour = 11

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
print("##################################/n")
year = 2023
month = 12
day =19
hour = 11

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
print("##################################/n")
year = 2023
month = 12
day =22
hour = 11

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
print("##################################/n")
year = 2023
month = 12
day =23
hour = 11

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
print("##################################/n")
year = 2023
month = 12
day =31
hour = 11

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
print("##################################/n")

year = 2024
month = 2
day =3
hour = 11

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
print("##################################/n")

year = 2024
month = 2
day =4
hour = 17

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
print("##################################/n")
year = 2024
month = 2
day =5
hour = 11

result = get_heavenly_branch_ymdh_pillars_current(year, month, day, hour)
logger.info (result)
print("##################################/n")

# heavenly_month_stem, earthly_month_stem  = bazi.calculate_month_heavenly(year,month,day)

# logger.info(bazi.resolveHeavenlyStem(heavenly_month_stem) + bazi.resolveEarthlyBranch(earthly_month_stem))

# logger.debug(f"Year Stem is {get_heavenly_branch_y(2018)}")

# logger.debug(f"{bazi.SixtyStem(121)}")
# logger.debug(f"{bazi.getSixtyStemIndex('甲子')}")
# logger.info(f"{bazi.calculate_day_heavenly(year, month, day)}")
# logger.info(f"{bazi.calculate_day_heavenly(year, month, day)}")
# logger.info(f"{get_heavenly_branch_ymd(year, month, day)}")
# Creating a datetime object for a specific date and time
specific_datetime = datetime(year, month,day,hour, 30, 0)  # Year, Month, Day, Hour, Minute, Second
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


#     try:
        
#         year = 2023
#         month = 8
#         day = 23
#         hour = 9
        
#         result_current = get_heavenly_branch_ymdh_pillars(year,month,day,hour)
#     except Exception as e:
#         print("Error: {0}".format(e))
             






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
