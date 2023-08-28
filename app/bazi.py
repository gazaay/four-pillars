from enum import Enum
from datetime import datetime
from lunarcalendar import Converter, Solar, Lunar, DateNotExist, zh_festivals, zh_solarterms
from . import solarterm

import logging

__name__ = "bazi"

# Configure logging settings
logging.basicConfig(level=logging.DEBUG,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)



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

     #Chinese calendar is solar calendar
    # print(f"Year Pillar: Year: {year} month: {month} Offset is {offset}")
    year, month, day = convert_Solar_to_Luna(year, month, day)
    heavenly_stem_index = (year - 3 - offset) % 10
    earthly_branch_index = (year - 3) % 12
    heavenly_stem = HeavenlyStem(heavenly_stem_index)
    logger.debug(f"Year Earthly Index {earthly_branch_index}")
    earthly_branch = EarthlyBranch(earthly_branch_index )
    logger.debug(f"Year Earthly Branch {earthly_branch.value}")
    return heavenly_stem.value, earthly_branch.value

def calculate_month_heavenly(year, month: int, day):
    # #Chinese calendar is solar calendar
    # year, month, day = convert_Solar_to_Luna(year, month, day)
    # if month == 0:
    #     offset = 1
    # else: 
    #     offset = 0
    # print(f"Month is {month} Offset is {offset}")

    solar_term, solar_month_index = get_Luna_Month_With_Season(datetime(year, month, day, 9, 15)) 

    quotient_solar = solar_month_index // 2
    reminder = solar_month_index % 2

    logger.info(f"The month with Season is {quotient_solar}")

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

    return HeavenlyStem(month_heavenly_stem), EarthlyBranch(earthly_branch_stem)

def calculate_day_heavenly(year, month, day):

    #Chinese calendar is solar calendar
    # year, month, day = convert_Solar_to_Luna(year, month, day)


    if year >= 2000:
    # Calculate the intermediate value
        intermediate_value = (year % 100 + 100) * 5 + (year % 100 + 100) // 4 + 9 + day
    else:
        intermediate_value = (year % 100) * 5 + (year % 100 ) // 4 + 9 + day

    # logger.info(f"Intermediate value {intermediate_value %60}")
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
            logger.info("It is Leap Year!")
            adjustment_factor -= 1

    # Apply the adjustment factor
    intermediate_value += adjustment_factor

    # logger.info(f"Intermediate value after Leap year Adjusted. {intermediate_value %60} with {SixtyStem(intermediate_value %60)}")
    # # Calculate Heavenly Stems and Earthly Branches
    heavenly_stem_index = (intermediate_value % 60) % 10
    earthly_branch_index = (intermediate_value % 60) % 12

    # Define Heavenly Stems and Earthly Branches
    heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    heavenly_stem = heavenly_stems[heavenly_stem_index]
    earthly_branch = earthly_branches[earthly_branch_index]

    return HeavenlyStem(heavenly_stem_index) , EarthlyBranch(earthly_branch_index)

def calculate_dark_stem(heavenly_index, earthly_index):
    stem = resolveHeavenlyStem(heavenly_index) + resolveEarthlyBranch(earthly_index)
    print(f"Input stem {stem} with {heavenly_index}")
    if earthly_index.value > 7:
        offset = -5
    else:
        offset = 5
    stemIndex = getSixtyStemIndex(stem)
    print(f"output stem {SixtyStem(stemIndex + offset)}")
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
    heavenly_stem, earthly_branch = calculate_day_heavenly(year, month, day)
    heavenly_stem_index = ((((heavenly_stem.value*2 + (hour+1) // 2) -2) % 10) + 1)%10
    earthly_branch_index = (((((hour + 1) // 2) ) % 12) + 1)%12
    logger.debug("Earthly Branch Index is ", earthly_branch_index)
    return HeavenlyStem(heavenly_stem_index), EarthlyBranch(earthly_branch_index)


def convert_Solar_to_Luna(year, month, day):
    solar = Solar(year, month, day)
    # print(f":Luna_to_Solar: This is Solar year - {solar}")
    lunar = Converter.Solar2Lunar(solar)
    # print(f":Luna_to_Solar: This is Lunar year - {lunar.year}")
    logger.info(f"Solar Date {year}-{month}-{day} converted to {lunar.year} and month {lunar.month} and day {lunar.day}")
    return lunar.year, lunar.month, lunar.day

def resolveHeavenlyStem(number):
    return str(HeavenlyStemCN[HeavenlyStem(number).name].value)

def resolveEarthlyBranch(number ):
    return str(EarthlyBranchCN[EarthlyBranch(number).name].value)


# Example usage
print(HeavenlyStem.JIA)  # Output: HeavenlyStem.JIA
print(EarthlyBranch.ZI)  # Output: EarthlyBranch.ZI
print(FiveElement.WOOD)  # Output: FiveElement.WOOD
print(YinYang.YIN)       # Output: YinYang.YIN
print(TenGod.FRIEND)     # Output: TenGod.FRIEND


def get_Luna_Month_With_Season(current_datetime):

    year, month, day = convert_Solar_to_Luna (current_datetime.year, current_datetime.month,
                                            current_datetime.day)

    specific_datetime = datetime(year, month, day, current_datetime.hour,current_datetime.minute, current_datetime.second)                                        
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
        method = getattr(solarterm, solar_term)  # Assuming the methods are defined in the same module
        current_solarterm_datetime = method(specific_datetime.year)
        luna_solar_term = solar_term
        
        date_string = current_solarterm_datetime
        format_string = "%Y-%m-%d %H:%M:%S.%f%z"

        # datetime_object = datetime.strptime(date_string, format_string)
        current_datetime = current_datetime.replace(tzinfo=current_solarterm_datetime.tzinfo)

        if (current_datetime > current_solarterm_datetime):
            i = i+1
            logger.debug(f"{i} on specific date {specific_datetime} date {current_solarterm_datetime}")
        else: 
            luna_month = i
            break
        
    print(f" The Solar term is {luna_solar_term} and {luna_month}")
    return luna_solar_term, luna_month


