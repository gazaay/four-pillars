from enum import Enum
from lunarcalendar import Converter, Solar, Lunar, DateNotExist, zh_festivals, zh_solarterms
from . import solarterm
from threading import Lock
import logging
import bisect
import pandas as pd
from pytz import timezone
from datetime import datetime, timedelta

__name__ = "bazi"

# Configure logging settings
logging.basicConfig(level=logging.INFO,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)
# Test log messages
logger.debug("This is a debug message")

# Define the Heavenly Stems as an enumeration
class HeavenlyStem(Enum):
    JIA = 1  # 甲
    YI = 2   # 乙
    BING = 3 # 丙
    DING = 4 # 丁
    WU = 5   # 戊
    JI = 6   # 己
    GENG = 7 # 庚
    XIN = 8  # 辛
    REN = 9  # 壬
    GUI = 0 # 癸

# Define the Earthly Branches as an enumeration
class EarthlyBranch(Enum):
    ZI = 1  # 子
    CHOU = 2  # 丑
    YIN = 3  # 寅
    MAO = 4  # 卯
    CHEN = 5  # 辰
    SI = 6  # 巳
    WU = 7  # 午
    WEI = 8  # 未
    SHEN = 9  # 申
    YOU = 10 # 酉
    XU = 11 # 戌
    HAI = 0 # 亥

# # Coefficients for the earthly branches
earthly_branch_enum = {
    "丑": 2,
    "寅": 3,
    "卯": 4,
    "辰": 5,
    "巳": 6,
    "午": 7,
    "未": 8,
    "申": 9,
    "酉": 10,
    "戌": 11,
    "亥": 0,
    "子": 1
}
class HeavenlyStemCN(Enum):
    JIA = '甲'
    YI = '乙'
    BING = '丙'
    DING = '丁'
    WU = '戊'
    JI = '己'
    GENG = '庚'
    XIN = '辛'
    REN = '壬'
    GUI = '癸'





class EarthlyBranchCN(Enum):
    ZI = '子'
    CHOU = '丑'
    YIN = '寅'
    MAO = '卯'
    CHEN = '辰'
    SI = '巳'
    WU = '午'
    WEI = '未'
    SHEN = '申'
    YOU = '酉'
    XU = '戌'
    HAI = '亥'

# Define the Five Elements as an enumeration
class FiveElement(Enum):
    WOOD = 1   # 木
    FIRE = 2   # 火
    EARTH = 3  # 土
    METAL = 4  # 金
    WATER = 5  # 水

# Define Yin and Yang as an enumeration
class YinYang(Enum):
    YIN = 1
    YANG = 2

# Define the Ten Gods as an enumeration
class TenGod(Enum):
    FRIEND = 1   # 正印
    RESOURCE = 2  # 偏印
    OUTPUT = 3  # 正官
    WEALTH = 4  # 偏官
    POWER = 5   # 正财
    STATUS = 6   # 偏财
    COMPANION = 7   # 伤官
    INFLUENCE = 8   # 食神
    SEAL = 9   # 正官
    CLASH = 10  # 比肩

solarterms = {
        "LiChun":1, "YuShui":2, "JingZhe":3, "ChunFen":4, "QingMing":5, "GuYu":6,
        "LiXia":7, "XiaoMan":8, "MangZhong":9, "XiaZhi":10, "XiaoShu":11, "DaShu":12,
        "LiQiu":13, "ChuShu":14, "BaiLu":15, "QiuFen":16, "HanLu":17, "ShuangJiang":18,
        "LiDong":19, "XiaoXue":20, "DaXue":21, "DongZhi":22, "XiaoHan":23, "DaHan":24
    }

heavenly_earthly_dict = {
    "甲子": 1,
    "乙丑": 2,
    "丙寅": 3,
    "丁卯": 4,
    "戊辰": 5,
    "己巳": 6,
    "庚午": 7,
    "辛未": 8,
    "壬申": 9,
    "癸酉": 10,
    "甲戌": 11,
    "乙亥": 12,
    "丙子": 13,
    "丁丑": 14,
    "戊寅": 15,
    "己卯": 16,
    "庚辰": 17,
    "辛巳": 18,
    "壬午": 19,
    "癸未": 20,
    "甲申": 21,
    "乙酉": 22,
    "丙戌": 23,
    "丁亥": 24,
    "戊子": 25,
    "己丑": 26,
    "庚寅": 27,
    "辛卯": 28,
    "壬辰": 29,
    "癸巳": 30,
    "甲午": 31,
    "乙未": 32,
    "丙申": 33,
    "丁酉": 34,
    "戊戌": 35,
    "己亥": 36,
    "庚子": 37,
    "辛丑": 38,
    "壬寅": 39,
    "癸卯": 40,
    "甲辰": 41,
    "乙巳": 42,
    "丙午": 43,
    "丁未": 44,
    "戊申": 45,
    "己酉": 46,
    "庚戌": 47,
    "辛亥": 48,
    "壬子": 49,
    "癸丑": 50,
    "甲寅": 51,
    "乙卯": 52,
    "丙辰": 53,
    "丁巳": 54,
    "戊午": 55,
    "己未": 56,
    "庚申": 57,
    "辛酉": 58,
    "壬戌": 59,
    "癸亥": 60
}

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

    return cheung_sheng_dict.get(stem_branch, "Unknown")

def SixtyStem(index: int) :

    index = index %60

    if index is 0:
        index = 60

    # Reverse the dictionary
    index_to_combination = {value: key for key, value in heavenly_earthly_dict.items()}

    # Now you can use an index to retrieve the corresponding combination
    combination = index_to_combination.get(index)

    if combination is not None:
        logger.debug("Combination:", combination)
    else:
        logger.debug("Index not found.")
    
    return combination

def getSixtyStemIndex(stem):
    return heavenly_earthly_dict[stem]

def calculate_year_heavenly(year, month: int, day):
    if month == 0:
        offset = 1
    else: 
        offset = 0

    solar_term, solar_month_index = get_Luna_Month_With_Season(datetime(year, month, day, 9, 15)) 
    solar_month_index = solarterms[solar_term]
     #Chinese calendar is solar calendar
    # logger.debug(f"Year Pillar: Year: {year} month: {month} Offset is {offset}")
    year, month, day = convert_Solar_to_Luna(year, month, day)
    heavenly_stem_index = (year - 3 - offset) % 10
    earthly_branch_index = (year - 3) % 12
    heavenly_stem = HeavenlyStem(heavenly_stem_index)
    logger.debug(f"Year Earthly Index {earthly_branch_index}")
    earthly_branch = EarthlyBranch(earthly_branch_index )
    logger.debug(f"Year Earthly Branch {earthly_branch.value}")
    
    return heavenly_stem.value, earthly_branch.value

def calculate_year_heavenly_for_current_time(year, month: int, day):
    if month == 0:
        offset = 1
    else: 
        offset = 0

    solar_term, solar_month_index = get_Luna_Month_With_Season(datetime(year, month, day, 9, 15)) 
    solar_month_index = solarterms[solar_term]
     #Chinese calendar is solar calendar
    # logger.debug(f"Year Pillar: Year: {year} month: {month} Offset is {offset}")
    year, month, day = convert_Solar_to_Luna(year, month, day)

    if solar_month_index > 20:
        year = year + 1
    heavenly_stem_index = (year - 3 - offset) % 10
    earthly_branch_index = (year - 3) % 12
    heavenly_stem = HeavenlyStem(heavenly_stem_index)
    logger.debug(f"Year Earthly Index {earthly_branch_index}")
    earthly_branch = EarthlyBranch(earthly_branch_index )
    logger.debug(f"Year Earthly Branch {earthly_branch.value}")
    
    # solar_month_index > 12
    if solar_month_index > 8 and solar_month_index < 20:
        return HeavenlyStem(get_next_half_heavenly(heavenly_stem_index)), EarthlyBranch(get_next_half_earthly(earthly_branch_index))
    else:   
        return heavenly_stem.value, earthly_branch.value

def calculate_year_heavenly_for_current_time_Option_2(year, month: int, day):
    if month == 0:
        offset = 1
    else: 
        offset = 0

    solar_term, solar_month_index = get_Luna_Month_With_Season(datetime(year, month, day, 9, 15)) 
    solar_month_index = solarterms[solar_term]
     #Chinese calendar is solar calendar
    # logger.debug(f"Year Pillar: Year: {year} month: {month} Offset is {offset}")
    year, month, day = convert_Solar_to_Luna(year, month, day)

    if solar_month_index > 20:
        year = year + 1
    heavenly_stem_index = (year - 3 - offset) % 10
    earthly_branch_index = (year - 3) % 12
    heavenly_stem = HeavenlyStem(heavenly_stem_index)
    logger.debug(f"Year Earthly Index {earthly_branch_index}")
    earthly_branch = EarthlyBranch(earthly_branch_index )
    logger.debug(f"Year Earthly Branch {earthly_branch.value}")
    
    # solar_month_index > 12
    if solar_month_index > 12 and solar_month_index < 20:
        return HeavenlyStem(get_next_half_heavenly(heavenly_stem_index)), EarthlyBranch(get_next_half_earthly(earthly_branch_index))
    else:   
        return heavenly_stem.value, earthly_branch.value



# Define a lock for synchronizing access to the shared variable 'i'
i_lock = Lock()

#流時use to calculate the time of day 8w. The month will change based on Season.
def calculate_month_heavenly_withSeason_for_current_time(year, month: int, day, hour):
    
    # if month == 0:
    #     offset = 1
    # else: 
    #     offset = 0
    # logger.debug(f"Month is {month} Offset is {offset}")
    solar_term, solar_month_index = get_Luna_Month_With_Season(datetime(year, month, day, hour, 15)) 
    solar_month_index = solarterms[solar_term]
    # #Chinese calendar is solar calendar
    # use the year only
    if solar_term == "LiChun":
        year = solarterm.LiChun(year).year
    else:
        year, xx_month, zz_day = convert_Solar_to_Luna(year, month, day)
    # if solar_month_index == 1 :
    #     solar_month_index = 25
    
    solar_month_index = solar_month_index + 1

    quotient_solar = solar_month_index // 2
    reminder = solar_month_index % 2

    # if quotient_solar == 0:
    #         quotient_solar = 12
    logger.debug(f"current_month The solar term is {solar_term} The date {year, month, day, hour} month {solar_month_index} day {day} with Solar_Month_index {solar_month_index} Season is {quotient_solar} with {solar_term} and reminder is {reminder}")
    month = quotient_solar

    heavenly_stem_index = (year - 3) % 10
    logger.debug(f"Heavenly Index is {heavenly_stem_index} and team is { HeavenlyStem(heavenly_stem_index)}")
    year_heavenly_stem = HeavenlyStem(heavenly_stem_index)
    logger.debug(f"Heavenly Stem {year_heavenly_stem.name}")
    month_heavenly_stem = ((year % 10 + 2 )  * 2 + month) %10

    # month_heavenly_stem = (year_heavenly_stem.value + year_heavenly_stem.value + 1) % 10
    # month_heavenly_stem = (month_heavenly_stem + month - 1 ) % 10
    logger.debug(f"Month Heavenly Stem {month_heavenly_stem} ")
    earthly_branch_stem = EarthlyBranch((month + 2) %12).value 
    logger.debug(f"Month Earthly Branch Stem {earthly_branch_stem}")

    if reminder > 0:
        logger.debug(f"Next Half Month - month {month}")
        return HeavenlyStem(get_next_half_heavenly(month_heavenly_stem)), EarthlyBranch(get_next_half_earthly(earthly_branch_stem))
    else:
        return HeavenlyStem(month_heavenly_stem), EarthlyBranch(earthly_branch_stem)

# 本時 use for calculate birthday. 
def calculate_month_heavenly_withSeason_for_baselife_time(year, _month: int, day, hour):
    month = _month
    
    # #Chinese calendar is solar calendar
    # year, month, day = convert_Solar_to_Luna(year, month, day)
    # if month == 0:
    #     offset = 1
    # else: 
    #     offset = 0
    # logger.debug(f"Month is {month} Offset is {offset}")
    solar_term, solar_month_index = get_Luna_Month_With_Season(datetime(year, month, day, hour, 15)) 

    solar_month_index = solarterms[solar_term]
    # #Chinese calendar is solar calendar
    # use the year only

    if solar_term == "LiChun":
        year = solarterm.LiChun(year).year
    else:
        year, xx_month, zz_day = convert_Solar_to_Luna(year, month, day)
    # if solar_month_index == 1 :
    #     solar_month_index = 25
    
    
    solar_month_index = solar_month_index + 1

    quotient_solar = solar_month_index // 2
    reminder = solar_month_index % 2

    # if quotient_solar == 0:
    #         quotient_solar = 12
    month = quotient_solar
    logger.debug(f"The solar term is {solar_term} The date {year, month, day, hour} month {solar_month_index} day {day} with Solar_Month_index {solar_month_index} Season is {quotient_solar} with {solar_term} and reminder is {reminder}")

    heavenly_stem_index = (year - 3) % 10
    logger.debug(f"Year Heavenly Index is {heavenly_stem_index} and team is { HeavenlyStem(heavenly_stem_index)}")
    year_heavenly_stem = HeavenlyStem(heavenly_stem_index)
    logger.debug(f"Heavenly Stem {year_heavenly_stem.name}")
    month_heavenly_stem = ((year % 10 + 2 )  * 2 + month) %10

    logger.debug(f"Month Heavenly Stem {month_heavenly_stem} ")
    earthly_branch_stem = EarthlyBranch((month + 2) %12).value 
    logger.debug(f"Month Earthly Branch Stem {earthly_branch_stem}")

    return HeavenlyStem(month_heavenly_stem), EarthlyBranch(earthly_branch_stem)

def calculate_day_heavenly_current(year, month, day, hour, mins):

    #Chinese calendar is solar calendar
    # year, month, day = convert_Solar_to_Luna(year, month, day)
    if hour == 23: 
        day = day + 1
        hour = 0

    if year >= 2000:
    # Calculate the intermediate value
        intermediate_value = (year % 100 + 100) * 5 + (year % 100 + 100) // 4 + 9 + day
    else:
        intermediate_value = (year % 100) * 5 + (year % 100 ) // 4 + 9 + day

    # logger.debug(f"Intermediate value {intermediate_value %60}")
    # if (month == 1) or (month == 4) or (month == 5):
    #     intermediate_value += 1
    # elif (month == 2) or (month == 6) or (month == 7):
    #     intermediate_value += 2

    # Determine if the month is single (29 days) or double (30 days)
    if month % 2 == 0:  # If month is even, it's a double month
        intermediate_value += 30
    else:  # If month is odd, it's a single month
        intermediate_value += 0

    # Determine the adjustment factor for each month
    adjustment_factors = [0, 1, 2, 0, 1, 1, 2, 2, 3, 4, 4, 5, 5]
    adjustment_factor = adjustment_factors[month]

    # Adjust for leap year
    if (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0)):
        if (month == 1) or (month == 2):
            logger.debug("It is Leap Year!")
            adjustment_factor -= 1

    # Apply the adjustment factor
    intermediate_value += adjustment_factor

    # logger.debug(f"Intermediate value after Leap year Adjusted. {intermediate_value %60} with {SixtyStem(intermediate_value %60)}")
    # # Calculate Heavenly Stems and Earthly Branches
    heavenly_stem_index = (intermediate_value % 60) % 10
    earthly_branch_index = (intermediate_value % 60) % 12

    # Define Heavenly Stems and Earthly Branches
    # heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    # earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # heavenly_stem = heavenly_stems[heavenly_stem_index]
    # earthly_branch = earthly_branches[earthly_branch_index]

    if hour >= 11:
        logger.debug(f"Next Half Day - hour {hour}")
        return HeavenlyStem(get_next_half_heavenly(heavenly_stem_index)) , EarthlyBranch(get_next_half_earthly(earthly_branch_index))    
    else:
        return HeavenlyStem(heavenly_stem_index) , EarthlyBranch(earthly_branch_index)

def calculate_day_heavenly_base(year, month, day, hour, mins):

    if hour == 23: 
        day = day + 1
        hour = 0
    #Chinese calendar is solar calendar
    # year, month, day = convert_Solar_to_Luna(year, month, day)


    if year >= 2000:
    # Calculate the intermediate value
        intermediate_value = (year % 100 + 100) * 5 + (year % 100 + 100) // 4 + 9 + day
    else:
        intermediate_value = (year % 100) * 5 + (year % 100 ) // 4 + 9 + day

    # logger.debug(f"Intermediate value {intermediate_value %60}")
    # if (month == 1) or (month == 4) or (month == 5):
    #     intermediate_value += 1
    # elif (month == 2) or (month == 6) or (month == 7):
    #     intermediate_value += 2

    # Determine if the month is single (29 days) or double (30 days)
    if month % 2 == 0:  # If month is even, it's a double month
        intermediate_value += 30
    else:  # If month is odd, it's a single month
        intermediate_value += 0

    # Determine the adjustment factor for each month
    adjustment_factors = [0, 1, 2, 0, 1, 1, 2, 2, 3, 4, 4, 5, 5]
    adjustment_factor = adjustment_factors[month]

    # Adjust for leap year
    if (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0)):
        if (month == 1) or (month == 2):
            logger.debug("It is Leap Year!")
            adjustment_factor -= 1

    # Apply the adjustment factor
    intermediate_value += adjustment_factor

    # logger.debug(f"Intermediate value after Leap year Adjusted. {intermediate_value %60} with {SixtyStem(intermediate_value %60)}")
    # # Calculate Heavenly Stems and Earthly Branches
    heavenly_stem_index = (intermediate_value % 60) % 10
    earthly_branch_index = (intermediate_value % 60) % 12

    # Define Heavenly Stems and Earthly Branches
    # heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    # earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # heavenly_stem = heavenly_stems[heavenly_stem_index]
    # earthly_branch = earthly_branches[earthly_branch_index]

    return HeavenlyStem(heavenly_stem_index) , EarthlyBranch(earthly_branch_index)


def calculate_dark_stem(heavenly_index, earthly_index):
    stem = resolveHeavenlyStem(heavenly_index) + resolveEarthlyBranch(earthly_index)
    # logger.debug(f"Input stem {stem} with {heavenly_index}")
    if earthly_index.value > 7:
        offset = -5
    else:
        offset = 5
    stemIndex = getSixtyStemIndex(stem)
    # logger.debug(f"output stem {SixtyStem(stemIndex + offset)}")
    return SixtyStem(stemIndex + offset)

def zz_calculate_day_heavenly(year, month, day):

    #Chinese calendar is solar calendar
    year, month, day = convert_Solar_to_Luna(year, month, day)

    if month < 3:
        year -= 1
        month += 12
    
    C = year // 100
    y = year % 100
    M = month
    d = day

    if M % 2 == 1:
        i = 0
        j = 0
    else:
        i = 6
        j = 0

    g = 4*C + (C // 4) + 5*y + (y // 4) + (3*(M + 1) // 5) + d -3 + j
    z = 8*C + (C // 4) + 5*y + (y // 4) + (3*(M + 1) // 5) + d +7 + i + j 
    
    heavenly_stem = g % 10
    earthly_branch = z % 12
    
    return HeavenlyStem(heavenly_stem), EarthlyBranch(earthly_branch)

def calculate_hour_heavenly(year, month, day, hour):
    heavenly_stem, earthly_branch = calculate_day_heavenly_base(year, month, day, hour, 15)
    heavenly_stem_index = ((((heavenly_stem.value*2 + (hour+1) // 2) -2) % 10) + 1)%10
    earthly_branch_index = (((((hour + 1) // 2) ) % 12) + 1)%12
    logger.debug("Earthly Branch Index is ", earthly_branch_index)
    return HeavenlyStem(heavenly_stem_index), EarthlyBranch(earthly_branch_index)

def convert_Solar_to_Luna(year, month, day):
    solar = Solar(year, month, day)
    # logger.debug(f":Luna_to_Solar: This is Solar year - {solar}")
    lunar = Converter.Solar2Lunar(solar)
    # logger.debug(f":Luna_to_Solar: This is Lunar year - {lunar.year}")
    logger.debug(f"Solar Date {year}-{month}-{day} converted to {lunar.year} and month {lunar.month} and day {lunar.day}")
    return lunar.year, lunar.month, lunar.day

def resolveHeavenlyStem(number):
    return str(HeavenlyStemCN[HeavenlyStem(number).name].value)

def resolveEarthlyBranch(number ):
    return str(EarthlyBranchCN[EarthlyBranch(number).name].value)

def get_Luna_Month_With_Season_zz(current_datetime):

    year, month, day = convert_Solar_to_Luna (current_datetime.year, current_datetime.month,
                                            current_datetime.day)

    
    # specific_datetime = datetime(year, month, day, current_datetime.hour,current_datetime.minute, current_datetime.second)                                        
    solarterms_list = [
        "LiChun", "YuShui", "JingZhe", "ChunFen", "QingMing", "GuYu",
        "LiXia", "XiaoMan", "MangZhong", "XiaZhi", "XiaoShu", "DaShu",
        "LiQiu", "ChuShu", "BaiLu", "QiuFen", "HanLu", "ShuangJiang",
        "LiDong", "XiaoXue", "DaXue", "DongZhi", "XiaoHan", "DaHan"
    ]  

    i=1
    luna_month = 0

    luna_solar_term = ""
    
    
    for solar_term in solarterms_list:
        with i_lock:
            method = getattr(solarterm, solar_term)  # Assuming the methods are defined in the same module
            current_solarterm_datetime = method(year)
        luna_solar_term = solar_term
        
        # date_string = current_solarterm_datetime
        # format_string = "%Y-%m-%d %H:%M:%S.%f%z"

        # datetime_object = datetime.strptime(date_string, format_string)
        current_datetime = current_datetime.replace(tzinfo=current_solarterm_datetime.tzinfo)

        
        if (current_datetime > current_solarterm_datetime):
            i = i+1
        else: 
            luna_month = i
            break
            
    # logger.debug(f" The Solar term is {luna_solar_term} and {luna_month}")
    return luna_solar_term, luna_month

# Initialize a dictionary to cache solar terms for each year
solar_term_cache = {}

def get_solar_terms(year):
    if year in solar_term_cache:
        return solar_term_cache[year]

    solar_terms = [solarterm.DongZhi(year - 1), solarterm.XiaoHan(year), solarterm.DaHan(year),
        solarterm.LiChun(year), solarterm.YuShui(year), solarterm.JingZhe(year), solarterm.ChunFen(year),
        solarterm.QingMing(year), solarterm.GuYu(year), solarterm.LiXia(year), solarterm.XiaoMan(year),
        solarterm.MangZhong(year), solarterm.XiaZhi(year), solarterm.XiaoShu(year), solarterm.DaShu(year),
        solarterm.LiQiu(year), solarterm.ChuShu(year), solarterm.BaiLu(year), solarterm.QiuFen(year),
        solarterm.HanLu(year), solarterm.ShuangJiang(year), solarterm.LiDong(year), solarterm.XiaoXue(year),
        solarterm.DaXue(year), solarterm.DongZhi(year), solarterm.XiaoHan(year + 1), solarterm.DaHan(year + 1), 
        solarterm.LiChun(year + 2)
    ]

    utc_timezone = timezone('UTC')
    # Set the timezone for the solar terms
    # solar_terms = [ utc_timezone.localize(dt) for dt in solar_terms]

    # Cache the solar terms for the year
    solar_term_cache[year] = solar_terms

    return solar_terms



def find_solar_term_and_index(df, query_date):

   # Set the timezone for query_date to UTC using pytz
    utc_timezone = timezone('Asia/Hong_Kong')
    query_date_utc_aware = utc_timezone.localize(query_date)
    logger.debug(query_date_utc_aware)

    # if query_date_utc_aware <= df.iloc[21]["end_date"] :
    #     # If the date is before January 5th, add one year
    #     query_date_utc_aware += timedelta(days=365)

    # Find the row where the query_date falls within the start_date and end_date range
    row = df[(df['start_date'] <= query_date_utc_aware) & (query_date_utc_aware < df['end_date'])]
    # logger.debug(df)
    if not row.empty:
        # Extract the solar term and index
        solar_term = row['solarterms'].values[0]
        index = df.loc[df['solarterms'] == solar_term].index[0] + 1
        logger.debug(index)
        return solar_term, index
    else:
        logger.debug(df)
        i_num = 21
        s_date = df.iloc[i_num]["start_date"]
        e_date = df.iloc[i_num]["end_date"] 
        logger.debug (f"{query_date_utc_aware} and {s_date}and {e_date}")
        logger.debug (df.iloc[i_num]["start_date"] <= query_date_utc_aware )
        logger.debug ( e_date > query_date_utc_aware)
        return None, None

    
def get_Luna_Month_With_Season(target_date):
    # year, month, day = convert_Solar_to_Luna(target_date.year, target_date.month, target_date.day)

    date_list = get_solar_terms(target_date.year)

    # Original lists
    solarterms = [ "DongZhi", "XiaoHan", "DaHan",
        "LiChun", "YuShui", "JingZhe", "ChunFen", "QingMing", "GuYu",
        "LiXia", "XiaoMan", "MangZhong", "XiaZhi", "XiaoShu", "DaShu",
        "LiQiu", "ChuShu", "BaiLu", "QiuFen", "HanLu", "ShuangJiang",
        "LiDong", "XiaoXue", "DaXue", "DongZhi", "XiaoHan", "DaHan","LiChun",
    ]
    # date_list = date_list[:-1]
    # Merge the three lists into a DataFrame
    df = pd.DataFrame(list(zip(solarterms, date_list, date_list[1:] + [date_list[0]])), columns=['solarterms', 'start_date', 'end_date'])
    
    df = df.iloc[:-1]
    # Update the end_date value for the row with index 21
    # df.loc[21, "end_date"] = solarterm.XiaoHan(target_date.year+1)

    logger.debug (df.loc[21]["end_date"])
    logger.debug (df)
    return find_solar_term_and_index(df,target_date)

    # return solarterms_list[luna_month], luna_month+1

    # # if year > 11:
    # #     solarterms_list = solarterms_list.append(get_solar_terms(year + 1)[0])

    # # year = target_date.year
    # # month = target_date.month
    # # day = target_date.day
    # # solarterms_list = solarterms_list[:-2]

    # # last_two_objects = get_solar_terms(year + 1)
    # # last_two_objects = last_two_objects[-2:]

    # # solarterms_list = solarterms_list + last_two_objects

    # # Set the timezone of solarterms_list to be the same as target_date
    # solarterms_list = [dt.replace(tzinfo=target_date.tzinfo) for dt in solarterms_list]
    # logger.debug(f"Solarterms List {solarterms_list}")
    # # logger.debug(f"{solarterms_list}")
    # # Use bisect to find the insertion point in the sorted list
    # luna_month = bisect.bisect_left(solarterms_list, target_date)
    
    # solarterms_list = [
    #     "LiChun", "YuShui", "JingZhe", "ChunFen", "QingMing", "GuYu",
    #     "LiXia", "XiaoMan", "MangZhong", "XiaZhi", "XiaoShu", "DaShu",
    #     "LiQiu", "ChuShu", "BaiLu", "QiuFen", "HanLu", "ShuangJiang",
    #     "LiDong", "XiaoXue", "DaXue", "DongZhi", "XiaoHan", "DaHan", "LiChun"
    # ]  
    # logger.debug(f"Luna Month of {target_date} is - {luna_month} - Luna Calc is {year} {month} {day}")
    # # solarterms_list[luna_month]
    # if luna_month == 24:  
    #     logger.debug("############WARNING @############ Hard code to zero:")  
    #     return "DaHan", 25
    # else:
    #     return solarterms_list[luna_month], luna_month+1

def get_next_half_heavenly(heavenly_index):
    return (heavenly_index + 5) % 10

def get_next_half_earthly(earthly_index):
    return (earthly_index + 3) % 12

# def get_Luna_Month_With_Season(target_date):
    
#     year, month, day = convert_Solar_to_Luna (target_date.year, target_date.month,
#                                             target_date.day)
#     with i_lock:
#         solarterms_list = [
#             solarterm.LiChun(year), solarterm.YuShui(year), solarterm.JingZhe(year), solarterm.ChunFen(year),
#             solarterm.QingMing(year), solarterm.GuYu(year), solarterm.LiXia(year), solarterm.XiaoMan(year),
#             solarterm.MangZhong(year), solarterm.XiaZhi(year), solarterm.XiaoShu(year), solarterm.DaShu(year),
#             solarterm.LiQiu(year), solarterm.ChuShu(year), solarterm.BaiLu(year), solarterm.QiuFen(year),
#             solarterm.HanLu(year), solarterm.ShuangJiang(year), solarterm.LiDong(year), solarterm.XiaoXue(year),
#             solarterm.DaXue(year), solarterm.DongZhi(year), solarterm.XiaoHan(year), solarterm.DaHan(year)
#         ]

#     # Set the timezone of solarterms_list to be the same as target_date
#     solarterms_list = [dt.replace(tzinfo=target_date.tzinfo) for dt in solarterms_list]

#     # Use bisect to find the insertion point in the sorted list
#     luna_month = bisect.bisect_left(solarterms_list, target_date)
    
#     return 'XiaoXue', luna_month


# bazi get the thousand year pillars for any given day
def get_heavenly_branch_ymdh_pillars(year: int, month: int, day: int, hour: int):

      year_, month_, day_ = convert_Solar_to_Luna (year, month,day)

      # logger.debug(f"current_datetime luna {year_} {month_} {day_}")
      # logger.debug(f"{year} {month} {day}")
      # datetime(year, month, day)
      # with lock:
      heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
      # with lock:
      dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)

      # with lock:
      heavenly_stem, earthly_branch = calculate_year_heavenly(year, month, day)
      # with lock:
      heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_current(year, month, day, hour, 15)
      # with lock:
      heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)
      # with lock:
      dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem )


      # heavenly_month_stem  = heavenly_day_stem
      # earthly_month_stem = earthly_hour_stem
      # dark_month_stem = dark_hour_stem

      return {
              "時": resolveHeavenlyStem(heavenly_hour_stem) + resolveEarthlyBranch(earthly_hour_stem),
              "日": resolveHeavenlyStem(heavenly_day_stem) + resolveEarthlyBranch(earthly_day_stem),
              "-時": dark_hour_stem,
              "月": resolveHeavenlyStem(heavenly_month_stem) + resolveEarthlyBranch(earthly_month_stem),
              "年": resolveHeavenlyStem(heavenly_stem) + resolveEarthlyBranch(earthly_branch),
              "-月": dark_month_stem,
            }

# Calculate for normal 8w
def get_heavenly_branch_ymdh_pillars_base(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_baselife_time(year, month,day,hour)
    dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = calculate_year_heavenly(year, month, day)
    heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_base(year, month, day, hour, 15)
    heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)
    dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem )


    return {
            "時": resolveHeavenlyStem(heavenly_hour_stem) + resolveEarthlyBranch(earthly_hour_stem),
            "日": resolveHeavenlyStem(heavenly_day_stem) + resolveEarthlyBranch(earthly_day_stem),
            "-時": dark_hour_stem,
            "月": resolveHeavenlyStem(heavenly_month_stem) + resolveEarthlyBranch(earthly_month_stem),
            "年": resolveHeavenlyStem(heavenly_stem) + resolveEarthlyBranch(earthly_branch),
            "-月": dark_month_stem,
           }

# Calculate for normal 8w
def get_heavenly_branch_ymdh_pillars_current(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
    dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time(year, month, day)
    heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_current(year, month, day, hour, 15)
    heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)
    dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem )

    flip_pillar(year, month, day, hour, Pillar.YEAR)

    return {
            "時": resolveHeavenlyStem(heavenly_hour_stem) + resolveEarthlyBranch(earthly_hour_stem),
            "日": resolveHeavenlyStem(heavenly_day_stem) + resolveEarthlyBranch(earthly_day_stem),
            "-時": dark_hour_stem,
            "月": resolveHeavenlyStem(heavenly_month_stem) + resolveEarthlyBranch(earthly_month_stem),
            "年": resolveHeavenlyStem(heavenly_stem) + resolveEarthlyBranch(earthly_branch),
            "-月": dark_month_stem,
           }


# Calculate for normal 8w
def get_heavenly_branch_ymdh_pillars_current_Option_2(year: int, month: int, day: int, hour: int):
    heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
    dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_current(year, month, day, hour, 15)
    heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)
    dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem )


    return {
            "時": resolveHeavenlyStem(heavenly_hour_stem) + resolveEarthlyBranch(earthly_hour_stem),
            "日": resolveHeavenlyStem(heavenly_day_stem) + resolveEarthlyBranch(earthly_day_stem),
            "-時": dark_hour_stem,
            "月": resolveHeavenlyStem(heavenly_month_stem) + resolveEarthlyBranch(earthly_month_stem),
            "年": resolveHeavenlyStem(heavenly_stem) + resolveEarthlyBranch(earthly_branch),
            "-月": dark_month_stem,
           }

def get_heavenly_branch_ymdh_pillars_current_flip_Option_2(year: int, month: int, day: int, hour: int):
    # Calculate normal heavenly stems and earthly branches
    heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_baselife_time(year, month, day, hour)
    dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_base(year, month, day, hour, 15)
    heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)
    dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem)
    # # Calculate normal heavenly stems and earthly branches
    # heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
    # dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    # heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    # heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_current(year, month, day, hour, 15)
    # heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)
    # dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem)

    # Create the flipped pillars using the 'earthly_flip' function
    flipped_year_stem, flipped_year_branch = earthly_flip(year, month, day, hour, Pillar.YEAR, Direction.BACKWARD)
    flipped_month_stem, flipped_month_branch = earthly_flip(year, month, day, hour, Pillar.MONTH, Direction.BACKWARD)
    flipped_day_stem, flipped_day_branch = earthly_flip(year, month, day, hour, Pillar.DAY, Direction.FORWARD)
    flipped_hour_stem, flipped_hour_branch = earthly_flip(year, month, day, hour, Pillar.HOUR, Direction.FORWARD)

    # Return a dictionary with both original and flipped pillars
    return {
        "時": resolveHeavenlyStem(heavenly_hour_stem) + resolveEarthlyBranch(earthly_hour_stem),
        "日": resolveHeavenlyStem(heavenly_day_stem) + resolveEarthlyBranch(earthly_day_stem),
        "-時": dark_hour_stem,
        "月": resolveHeavenlyStem(heavenly_month_stem) + resolveEarthlyBranch(earthly_month_stem),
        "年": resolveHeavenlyStem(heavenly_stem) + resolveEarthlyBranch(earthly_branch),
        "-月": dark_month_stem,
        # Add flipped pillars to the output
        "合年": resolveHeavenlyStem(flipped_year_stem) + resolveEarthlyBranch(flipped_year_branch),
        "合月": resolveHeavenlyStem(flipped_month_stem) + resolveEarthlyBranch(flipped_month_branch),
        "合日": resolveHeavenlyStem(flipped_day_stem) + resolveEarthlyBranch(flipped_day_branch),
        "合時": resolveHeavenlyStem(flipped_hour_stem) + resolveEarthlyBranch(flipped_hour_branch),
    }


from enum import Enum
from datetime import datetime

# Define the 8wPillar ENUM
class Pillar(Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"


# Define the Direction ENUM for return values
class Direction(Enum):
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"

# Function to check whether the date is forward or backward
def pillar_forward_or_backward(year: int, month: int, day: int, hour: int, pillar: Pillar) -> Direction:
    input_time = datetime(year, month, day, hour)
    current_time = datetime.now()

    # Determine the difference based on the given Pillar
    if pillar == Pillar.HOUR:
        delta = (current_time - input_time).total_seconds() / 3600  # Difference in hours
    elif pillar == Pillar.DAY:
        delta = (current_time - input_time).days  # Difference in days
    elif pillar == Pillar.MONTH:
        delta = (current_time.year - input_time.year) * 12 + (current_time.month - input_time.month)  # Difference in months
    elif pillar == Pillar.YEAR:
        delta = current_time.year - input_time.year  # Difference in years

    # Return Direction enum: FORWARD if input_time is in the future, BACKWARD if in the past
    return Direction.FORWARD if delta < 0 else Direction.BACKWARD

# Flip pillar based on direction
def flip_pillar(year: int, month: int, day: int, hour: int, pillar: Pillar):
    # Call the relevant functions based on pillar
    if pillar == Pillar.MONTH:
        heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
        dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    elif pillar == Pillar.YEAR:
        heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    elif pillar == Pillar.DAY:
        heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_current(year, month, day, hour, 15)
    elif pillar == Pillar.HOUR:
        heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)
        dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem)

    # Call the direction checker
    direction = pillar_forward_or_backward(year, month, day, hour, pillar)

    # If the direction is forward, call earthly_flip
    earthly_flip(year, month, day, hour, pillar, direction)

earthly_branch_pairs = {
    EarthlyBranch.ZI: (EarthlyBranch.CHOU, 1),   # ZI -> CHOU is 1 step forward
    EarthlyBranch.YIN: (EarthlyBranch.HAI, 9),   # YIN -> HAI is 9 steps forward
    EarthlyBranch.MAO: (EarthlyBranch.XU, 7),    # MAO -> XU is 7 steps forward
    EarthlyBranch.CHEN: (EarthlyBranch.YOU, 5),  # CHEN -> YOU is 5 steps forward
    EarthlyBranch.SI: (EarthlyBranch.SHEN, 3),   # SI -> SHEN is 3 steps forward
    EarthlyBranch.WU: (EarthlyBranch.WEI, 1),    # WU -> WEI is 1 step forward

    # Reverse pairs
    EarthlyBranch.CHOU: (EarthlyBranch.ZI, 11),   # CHOU -> ZI is 11 steps backward
    EarthlyBranch.HAI: (EarthlyBranch.YIN, 3),    # HAI -> YIN is 3 steps backward
    EarthlyBranch.XU: (EarthlyBranch.MAO, 5),     # XU -> MAO is 5 steps backward
    EarthlyBranch.YOU: (EarthlyBranch.CHEN, 7),   # YOU -> CHEN is 7 steps backward
    EarthlyBranch.SHEN: (EarthlyBranch.SI, 9),    # SHEN -> SI is 9 steps backward
    EarthlyBranch.WEI: (EarthlyBranch.WU, 11)     # WEI -> WU is 11 steps backward
}

# Define the Heavenly Stems as an enumeration
class HeavenlyStem(Enum):
    JIA = 1   # 甲
    YI = 2    # 乙
    BING = 3  # 丙
    DING = 4  # 丁
    WU = 5    # 戊
    JI = 6    # 己
    GENG = 7  # 庚
    XIN = 8   # 辛
    REN = 9   # 壬
    GUI = 0   # 癸

def earthly_flip(year: int, month: int, day: int, hour: int, pillar: Pillar, direction: Direction):
    """
    This function adjusts the Heavenly Stem and Earthly Branch based on the selected pillar (year, month, day, or hour) 
    and the direction (forward or backward). The adjustments are based on defined relationships between 
    Earthly Branches and Heavenly Stems.
    
    Returns:
        new_stem (HeavenlyStem): The new Heavenly Stem after the flip.
        paired_earthly_branch (EarthlyBranch): The new Earthly Branch after the flip.
    """

    # Identify the Heavenly Stem and Earthly Branch based on the pillar type
    if pillar == Pillar.MONTH:
        heavenly_stem, earthly_branch = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
    elif pillar == Pillar.YEAR:
        heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    elif pillar == Pillar.DAY:
        heavenly_stem, earthly_branch = calculate_day_heavenly_current(year, month, day, hour, 15)
    elif pillar == Pillar.HOUR:
        heavenly_stem, earthly_branch = calculate_hour_heavenly(year, month, day, hour)

    # Convert to enum based on the new EarthlyBranch Enum (expects `earthly_branch` as an integer)
    earthly_branch_enum = EarthlyBranch(earthly_branch)

    # Define all Heavenly Stems in a list for cycle operations
    heavenly_stems = list(HeavenlyStem)

    # Get the associated pair and step count for the given Earthly Branch
    paired_earthly_branch, steps_forward = earthly_branch_pairs.get(earthly_branch_enum, (None, 0))

    # If there is no pair or step count, handle the error or set default
    if paired_earthly_branch is None:
        logger.debug(f"No pair found for earthly branch {earthly_branch_enum}")
        return None, None

    # Determine the number of steps to move based on direction
    if direction == Direction.FORWARD:
        step_count = steps_forward  # Move forward by the given steps
    else:
        step_count = 10 - steps_forward  # Move backward in a 12-branch cycle

    # Convert the current Heavenly Stem to its enum if necessary
    heavenly_stem_enum = HeavenlyStem(heavenly_stem)

    # Calculate the new Heavenly Stem index
    current_index = heavenly_stems.index(heavenly_stem_enum)  # Find the index of the current stem
    new_index = (current_index + step_count) % len(heavenly_stems)  # Calculate the new index with wrapping
    new_stem = heavenly_stems[new_index]  # Get the new Heavenly Stem
    old_stem = heavenly_stems[current_index]
    # Output the new Heavenly Stem for debugging purposes
    logger.debug(f"For Pillar {pillar} Original Heavenly Stem: {heavenly_stem_enum.name}, New Heavenly Stem: {new_stem.name}")

    # Return both the new Heavenly Stem and the paired Earthly Branch
    return new_stem, paired_earthly_branch

def earthly_flip_2(year: int, month: int, day: int, hour: int, pillar: Pillar, direction: Direction):


    # Identify the Heavenly Stem and Earthly Branch based on the pillar type
    if pillar == Pillar.MONTH:
        heavenly_stem, earthly_branch = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
    elif pillar == Pillar.YEAR:
        heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    elif pillar == Pillar.DAY:
        heavenly_stem, earthly_branch = calculate_day_heavenly_current(year, month, day, hour, 15)
    elif pillar == Pillar.HOUR:
        heavenly_stem, earthly_branch = calculate_hour_heavenly(year, month, day, hour)

    print(resolveHeavenlyStem(heavenly_stem))
    # Convert heavenly_stem to enum, assuming functions return strings
    heavenly_stem_enum = HeavenlyStemCN[resolveHeavenlyStem(heavenly_stem)]  # e.g., "甲" becomes HeavenlyStemCN.JIA
    earthly_branch_enum = EarthlyBranchCN[resolveEarthlyBranch(earthly_branch)]  # e.g., "子" becomes EarthlyBranchCN.ZI

    # List of all Heavenly Stem CNs in cycle order
    heavenly_stems = list(HeavenlyStemCN)

    # Get the associated pair and step count for the given earthly branch
    paired_earthly_branch, steps_forward = earthly_branch_pairs.get(earthly_branch_enum, (None, 0))

    # If there is no pair or step count, handle the error or set default
    if paired_earthly_branch is None:
        print(f"No pair found for earthly branch {earthly_branch_enum}")
        return

    # Determine the number of steps to move based on direction
    if direction == Direction.FORWARD:
        step_count = steps_forward  # Move forward by the given steps
    else:
        step_count = len(heavenly_stems) - steps_forward  # Move backward

    # Calculate the new position in the Heavenly Stem cycle
    current_index = heavenly_stems.index(heavenly_stem_enum)
    new_index = (current_index + step_count) % len(heavenly_stems)
    new_stem = heavenly_stems[new_index]

    # Output the new Heavenly Stem
    print(f"Original Heavenly Stem: {heavenly_stem_enum}, New Heavenly Stem: {new_stem}")
