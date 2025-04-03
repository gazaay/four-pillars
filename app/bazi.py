from enum import Enum
from lunarcalendar import Converter, Solar, Lunar, DateNotExist, zh_festivals, zh_solarterms
from . import solarterm
from threading import Lock
import logging
import bisect
import pandas as pd
from pytz import timezone
from datetime import datetime, timedelta
from typing import Union, Tuple
import pytz
from typing import List

__name__ = "bazi"

# Configure logging settings
logging.basicConfig(
    level=logging.INFO,  # Set the minimum level for displayed logs
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('app.log')  # Log to file in current directory
    ]
)

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

# Coefficients for the heavenly stems 
heavenly_stem_enum = {
    "乙": 2,
    "丙": 3,
    "丁": 4,
    "戊": 5,
    "己": 6,
    "庚": 7,
    "辛": 8,
    "壬": 9,
    "癸": 0,
    "甲": 1
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

class Polarity(Enum):
    YIN = "Yin"
    YANG = "Yang"

class Direction(Enum):
    CLOCKWISE = "Clockwise"
    ANTICLOCKWISE = "AntiClockwise"

class HeavenlyStemYinYang(Enum):
    JIA = (1, Polarity.YANG, "甲")
    YI = (2, Polarity.YIN, "乙")
    BING = (3, Polarity.YANG, "丙")
    DING = (4, Polarity.YIN, "丁")
    WU = (5, Polarity.YANG, "戊")
    JI = (6, Polarity.YIN, "己")
    GENG = (7, Polarity.YANG, "庚")
    XIN = (8, Polarity.YIN, "辛")
    REN = (9, Polarity.YANG, "壬")
    GUI = (0, Polarity.YIN, "癸")

    def __init__(self, value, polarity, chinese):
        self._value_ = value
        self.polarity = polarity
        self.chinese = chinese

    @property
    def is_yang(self):
        return self.polarity == Polarity.YANG

    @property
    def is_yin(self):
        return self.polarity == Polarity.YIN
    
    @classmethod
    def from_value(cls, value: int) -> 'HeavenlyStemYinYang':
        """Create HeavenlyStemYinYang instance from numeric value"""
        for stem in cls:
            if stem.value == value:
                return stem
        raise ValueError(f"{value} is not a valid HeavenlyStemYinYang value")
    
    @staticmethod
    def get_directions(stem1: 'HeavenlyStemYinYang', 
                      stem2: 'HeavenlyStemYinYang', 
                      polarity: Polarity) -> tuple[Direction, Direction]:
        """
        Determine the self and external directions based on two stems and a polarity.

        Args:
            stem1: First HeavenlyStemYinYang
            stem2: Second HeavenlyStemYinYang
            polarity: Target Polarity (Yin or Yang)

        Returns:
            tuple[Direction, Direction]: (SelfDirection, ExternalDirection)
        """
        # Get numeric values
        # val1 = stem1.value
        # val2 = stem2.value

        # Calculate the difference (considering circular nature 1-10)
        # diff = (val2 - val1) % 10

        # Determine if the movement is clockwise or anticlockwise
        # This is a placeholder logic - adjust according to actual rules
        if polarity == Polarity.YANG:
            if HeavenlyStemYinYang.from_value(stem2.value).is_yin:
                self_direction = Direction.CLOCKWISE
                external_direction = Direction.ANTICLOCKWISE
            else:
                self_direction = Direction.ANTICLOCKWISE
                external_direction = Direction.CLOCKWISE
        else:  # YIN
            if HeavenlyStemYinYang.from_value(stem2.value).is_yin:
                self_direction = Direction.ANTICLOCKWISE
                external_direction = Direction.CLOCKWISE
            else:
                self_direction = Direction.CLOCKWISE
                external_direction = Direction.ANTICLOCKWISE

        return (self_direction, external_direction)


# def calculate_dayun(gender, year_pillar, month_pillar):
#     """
#     Calculate 大運 sequence and starting ages
#     """
#     # Convert input pillars to enums
#     year_stem = cn_to_enum(year_pillar[0])
#     year_branch = cn_to_enum(year_pillar[1])
#     month_stem = cn_to_enum(month_pillar[0])
#     month_branch = cn_to_enum(month_pillar[1])

#     # Determine forward or backward counting based on gender and year stem
#     forward = (gender.lower() == 'male' and year_stem.value % 2 == 1) or \
#               (gender.lower() == 'female' and year_stem.value % 2 == 0)

#     # Calculate 大運 sequence
#     dayun_sequence = []
#     for i in range(8):  # Calculate 8 大運
#         if forward:
#             new_stem_value = ((month_stem.value + i) % 10) or 10
#             new_branch_value = ((month_branch.value + i) % 12) or 12
#         else:
#             new_stem_value = ((month_stem.value - i - 1) % 10) or 10
#             new_branch_value = ((month_branch.value - i - 1) % 12) or 12

#         new_stem = HeavenlyStem(new_stem_value)
#         new_branch = EarthlyBranch(new_branch_value)
#         dayun_sequence.append((new_stem, new_branch))

#     # Calculate starting ages
#     starting_ages = []
#     base_age = 0
#     for i in range(8):
#         starting_ages.append(base_age + (i+1) * 10)

#     return dayun_sequence, starting_ages


solarterms = {
        "LiChun":1, "YuShui":2, "JingZhe":3, "ChunFen":4, "QingMing":5, "GuYu":6,
        "LiXia":7, "XiaoMan":8, "MangZhong":9, "XiaZhi":10, "XiaoShu":11, "DaShu":12,
        "LiQiu":13, "ChuShu":14, "BaiLu":15, "QiuFen":16, "HanLu":17, "ShuangJiang":18,
        "LiDong":19, "XiaoXue":20, "DaXue":21, "DongZhi":22, "XiaoHan":23, "DaHan":24
    }

heavenly_earthly_dict  = {
    # Traditional 60 Jiazi combinations (1-60)
    "甲子": 1, "乙丑": 2, "丙寅": 3, "丁卯": 4, "戊辰": 5, "己巳": 6,
    "庚午": 7, "辛未": 8, "壬申": 9, "癸酉": 10, "甲戌": 11, "乙亥": 12,
    "丙子": 13, "丁丑": 14, "戊寅": 15, "己卯": 16, "庚辰": 17, "辛巳": 18,
    "壬午": 19, "癸未": 20, "甲申": 21, "乙酉": 22, "丙戌": 23, "丁亥": 24,
    "戊子": 25, "己丑": 26, "庚寅": 27, "辛卯": 28, "壬辰": 29, "癸巳": 30,
    "甲午": 31, "乙未": 32, "丙申": 33, "丁酉": 34, "戊戌": 35, "己亥": 36,
    "庚子": 37, "辛丑": 38, "壬寅": 39, "癸卯": 40, "甲辰": 41, "乙巳": 42,
    "丙午": 43, "丁未": 44, "戊申": 45, "己酉": 46, "庚戌": 47, "辛亥": 48,
    "壬子": 49, "癸丑": 50, "甲寅": 51, "乙卯": 52, "丙辰": 53, "丁巳": 54,
    "戊午": 55, "己未": 56, "庚申": 57, "辛酉": 58, "壬戌": 59, "癸亥": 60,

    # # Additional combinations (61-120)
    # "甲丑": 61, "甲寅": 62, "甲卯": 63, "甲辰": 64, "甲巳": 65,
    # "甲午": 66, "甲未": 67, "甲申": 68, "甲酉": 69, "甲戌": 70, "甲亥": 71,
    
    # "乙子": 72, "乙丑": 73, "乙寅": 74, "乙卯": 75, "乙辰": 76, "乙巳": 77,
    # "乙午": 78, "乙未": 79, "乙申": 80, "乙酉": 81, "乙戌": 82, "乙亥": 83,
    
    # "丙子": 84, "丙丑": 85, "丙寅": 86, "丙卯": 87, "丙辰": 88, "丙巳": 89,
    # "丙午": 90, "丙未": 91, "丙申": 92, "丙酉": 93, "丙戌": 94, "丙亥": 95,
    
    # "丁子": 96, "丁丑": 97, "丁寅": 98, "丁卯": 99, "丁辰": 100, "丁巳": 101,
    # "丁午": 102, "丁未": 103, "丁申": 104, "丁酉": 105, "丁戌": 106, "丁亥": 107,
    
    # "戊子": 108, "戊丑": 109, "戊寅": 110, "戊卯": 111, "戊辰": 112, "戊巳": 113,
    # "戊午": 114, "戊未": 115, "戊申": 116, "戊酉": 117, "戊戌": 118, "戊亥": 119,
    
    # "己子": 120
}

heavenly_earthly_wuxi_dict  = {
    # Traditional 60 Jiazi combinations (1-60)
    "甲子": 1, "乙丑": 2, "丙寅": 3, "丁卯": 4, "戊辰": 5, "己巳": 6,
    "庚午": 7, "辛未": 8, "壬申": 9, "癸酉": 10, "甲戌": 11, "乙亥": 12,
    "丙子": 13, "丁丑": 14, "戊寅": 15, "己卯": 16, "庚辰": 17, "辛巳": 18,
    "壬午": 19, "癸未": 20, "甲申": 21, "乙酉": 22, "丙戌": 23, "丁亥": 24,
    "戊子": 25, "己丑": 26, "庚寅": 27, "辛卯": 28, "壬辰": 29, "癸巳": 30,
    "甲午": 31, "乙未": 32, "丙申": 33, "丁酉": 34, "戊戌": 35, "己亥": 36,
    "庚子": 37, "辛丑": 38, "壬寅": 39, "癸卯": 40, "甲辰": 41, "乙巳": 42,
    "丙午": 43, "丁未": 44, "戊申": 45, "己酉": 46, "庚戌": 47, "辛亥": 48,
    "壬子": 49, "癸丑": 50, "甲寅": 51, "乙卯": 52, "丙辰": 53, "丁巳": 54,
    "戊午": 55, "己未": 56, "庚申": 57, "辛酉": 58, "壬戌": 59, "癸亥": 60,

    # Additional combinations (61-120)
    "甲丑": 61, "甲寅": 62, "甲卯": 63, "甲辰": 64, "甲巳": 65,
    "甲午": 66, "甲未": 67, "甲申": 68, "甲酉": 69, "甲戌": 70, "甲亥": 71,
    
    "乙子": 72, "乙丑": 73, "乙寅": 74, "乙卯": 75, "乙辰": 76, "乙巳": 77,
    "乙午": 78, "乙未": 79, "乙申": 80, "乙酉": 81, "乙戌": 82, "乙亥": 83,
    
    "丙子": 84, "丙丑": 85, "丙寅": 86, "丙卯": 87, "丙辰": 88, "丙巳": 89,
    "丙午": 90, "丙未": 91, "丙申": 92, "丙酉": 93, "丙戌": 94, "丙亥": 95,
    
    "丁子": 96, "丁丑": 97, "丁寅": 98, "丁卯": 99, "丁辰": 100, "丁巳": 101,
    "丁午": 102, "丁未": 103, "丁申": 104, "丁酉": 105, "丁戌": 106, "丁亥": 107,
    
    "戊子": 108, "戊丑": 109, "戊寅": 110, "戊卯": 111, "戊辰": 112, "戊巳": 113,
    "戊午": 114, "戊未": 115, "戊申": 116, "戊酉": 117, "戊戌": 118, "戊亥": 119,
    
    "己子": 120
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

class ChineseCalendarConverter:
    @staticmethod
    def chinese_to_enum(chinese_char: str) -> Union[HeavenlyStem, EarthlyBranch]:
        """
        Convert Chinese character to either HeavenlyStem or EarthlyBranch enum.

        Args:
            chinese_char (str): Chinese character

        Returns:
            Union[HeavenlyStem, EarthlyBranch]: Corresponding enum value

        Raises:
            ValueError: If character not found
        """
        # Try Heavenly Stem first
        heavenly_reverse = {stem.value: stem.name for stem in HeavenlyStemCN}
        if chinese_char in heavenly_reverse:
            return HeavenlyStem[heavenly_reverse[chinese_char]]

        # Try Earthly Branch
        earthly_reverse = {branch.value: branch.name for branch in EarthlyBranchCN}
        if chinese_char in earthly_reverse:
            return EarthlyBranch[earthly_reverse[chinese_char]]

        raise ValueError(f"Character {chinese_char} not found in Heavenly Stems or Earthly Branches")

    @staticmethod
    def enum_to_chinese(enum_value: Union[HeavenlyStem, EarthlyBranch]) -> str:
        """
        Convert enum value to Chinese character.

        Args:
            enum_value: HeavenlyStem or EarthlyBranch enum value

        Returns:
            str: Corresponding Chinese character
        """
        if isinstance(enum_value, HeavenlyStem):
            return HeavenlyStemCN[enum_value.name].value
        elif isinstance(enum_value, EarthlyBranch):
            return EarthlyBranchCN[enum_value.name].value
        else:
            raise ValueError("Input must be HeavenlyStem or EarthlyBranch enum")

# Example usage:
converter = ChineseCalendarConverter()


def calculate_dayun(gender, year_pillar, month_pillar, days_to_next_solar_term):
    """
    Calculate 大運 sequence and starting ages
    """
    my_converter = ChineseCalendarConverter()
    # Convert input pillars to enums
    year_stem = my_converter.chinese_to_enum(year_pillar[0])
    year_branch = my_converter.chinese_to_enum(year_pillar[1])
    month_stem = my_converter.chinese_to_enum(month_pillar[0])
    month_branch = my_converter.chinese_to_enum(month_pillar[1])

    # Determine forward or backward counting based on gender and year stem
    forward = (gender.lower() == 'male' and year_stem.value % 2 == 1) or \
              (gender.lower() == 'female' and year_stem.value % 2 == 0)

    # Calculate 大運 sequence
    dayun_sequence = []
    for i in range(8):  # Calculate 8 大運
        if forward:
            new_stem_value = ((month_stem.value + i) % 10) 
            new_branch_value = ((month_branch.value + i) % 12)
        else:
            new_stem_value = ((month_stem.value - i - 1) % 10) 
            new_branch_value = ((month_branch.value - i - 1) % 12) 

        new_stem = HeavenlyStem(new_stem_value)
        new_branch = EarthlyBranch(new_branch_value)
        dayun_sequence.append((resolveHeavenlyStem(new_stem.value) +resolveEarthlyBranch(new_branch.value)))
    # Calculate the number of days to the next solar term
    # next_solar_term_date = my_converter.get_next_solar_term(birth_date)
    # days_to_next_solar_term = 8
    # (next_solar_term_date - birth_date).days

    # Calculate the starting age of the first 大運
    starting_age_first_dayun = days_to_next_solar_term / 3.0  # 1 day = 3 months in BaZi
    # Calculate starting ages
    starting_ages = []
    base_age = days_to_next_solar_term
    for i in range(12):
        age = base_age + (i) * 10
        if age >= 1:
            starting_ages.append(age)

    return dayun_sequence, starting_ages

def print_daiYun(gender: str, year_pillar: str, month_pillar: str, date_to_examine: datetime ):
    gender = gender
    year_pillar = year_pillar
    month_pillar = month_pillar

    solar_terms = get_solar_terms(date_to_examine.year)  # Your existing solar terms list
    days, next_term, term_name = find_days_to_next_solar_term(date_to_examine, solar_terms)

    # Calculate 大運
    dayun_sequence, starting_ages = calculate_dayun( gender, year_pillar, month_pillar,days)

    # Print results
    print("\n大運 Calculation Results:")
    print("-" * 40)
    for i, ((stem, branch), age) in enumerate(zip(dayun_sequence, starting_ages)):
        year = date_to_examine.year + int(age)
        print(f"大運 {i+1}: {stem}{branch} "
              f"({stem}-{branch}) Starting age: {age} Year: {year}")

def json_daiYun(gender: str, year_pillar: str, month_pillar: str, date_to_examine: datetime):
    solar_terms = get_solar_terms(date_to_examine.year)
    days, next_term, term_name = find_days_to_next_solar_term(date_to_examine, solar_terms)

    # Calculate 大運
    dayun_sequence, starting_ages = calculate_dayun(gender, year_pillar, month_pillar, days)

    # Create result list
    result = []
    for (stem, branch), age in zip(dayun_sequence, starting_ages):
        result.append({
            "stem": stem,
            "branch": branch,
            "chinese": f"{stem}{branch}",
            "starting_age": round(age, 1)
        })

    return result

def SixtyStem(index: int) :

    index = index %60

    if index == 0:
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

def find_days_to_next_solar_term(current_time: datetime, solar_terms: List[datetime], is_yang: bool = True) -> tuple:
    """
    Find the next major solar term and calculate days until it occurs.
    Only considers major solar terms at start of each month.
    For yang energy looks forward, for yin energy looks backward.

    Args:
        current_time: The datetime to check from
        solar_terms: List of solar terms datetimes

    Returns:
        tuple: (days_to_next, next_solar_term, next_solar_term_name)
    """
    logger.debug(f"Finding days to next solar term for current_time: {current_time}, is_yang: {is_yang}")

    # Ensure current_time is timezone-aware
    if current_time.tzinfo is None:
        current_time = pytz.timezone('Asia/Shanghai').localize(current_time)
        logger.debug(f"Localized current_time to Asia/Shanghai: {current_time}")

    # Only major solar terms at start of months
    major_solar_terms = [
        "小寒 (Minor Cold)",      # 1月
        "立春 (Start of Spring)", # 2月  
        "驚蟄 (Awakening Insects)", # 3月
        "清明 (Pure Brightness)", # 4月
        "立夏 (Start of Summer)", # 5月
        "芒種 (Grain in Ear)",    # 6月
        "小暑 (Minor Heat)",      # 7月
        "立秋 (Start of Autumn)", # 8月
        "白露 (White Dew)",       # 9月
        "寒露 (Cold Dew)",        # 10月
        "立冬 (Start of Winter)", # 11月
        "大雪 (Major Snow)",      # 12月
    ]

    # Get only major solar terms (every other term starting at index 0)
    major_terms = solar_terms[1::2]
    logger.debug(f"Major solar terms: {[term.strftime('%Y-%m-%d') for term in major_terms]}")

    if is_yang:
        logger.debug("Using yang energy - looking forward for next major term")
        # Look forward for next major term
        next_term = None
        next_term_idx = 0
        for idx, term in enumerate(major_terms):
            if current_time < term:
                next_term = term
                next_term_idx = idx
                logger.debug(f"Found next major term: {term} at index {idx}")
                break
        
        if next_term is None:
            logger.error("No future major solar term found")
            raise ValueError("No future major solar term found")
            
    else:
        logger.debug("Using yin energy - looking backward for previous major term")
        # Look backward for previous major term
        prev_term = None
        next_term_idx = 0
        for idx in range(len(major_terms)-1, -1, -1):
            if current_time > major_terms[idx]:
                prev_term = major_terms[idx]
                next_term_idx = idx
                logger.debug(f"Found previous major term: {prev_term} at index {idx}")
                break
                
        if prev_term is None:
            logger.error("No previous major solar term found")
            raise ValueError("No previous major solar term found")
        next_term = prev_term

    # Calculate days difference
    time_diff = next_term - current_time
    days_to_next = abs(time_diff.total_seconds() / (24 * 3600)/3) # Convert to days and make positive
    logger.debug(f"Days to next/previous term: {days_to_next:.2f}")

    # Get the name of the next term
    next_term_name = major_solar_terms[next_term_idx % 12]
    logger.debug(f"Next term name: {next_term_name}")

    return days_to_next, next_term, next_term_name


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
    
    return HeavenlyStem(heavenly_stem.value), EarthlyBranch(earthly_branch.value)

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

    if solar_month_index > 24:
        year = year + 1
    heavenly_stem_index = (year - 3 - offset) % 10
    earthly_branch_index = (year - 3) % 12
    heavenly_stem = HeavenlyStem(heavenly_stem_index)
    logger.debug(f"Year Earthly Index {earthly_branch_index}")
    earthly_branch = EarthlyBranch(earthly_branch_index )
    logger.debug(f"Year Earthly Branch {earthly_branch.value}")
    
    # solar_month_index > 12
    if solar_month_index > 8 and solar_month_index < 24:
        return HeavenlyStem(get_next_half_heavenly(heavenly_stem_index)), EarthlyBranch(get_next_half_earthly(earthly_branch_index))
    else:   
        return HeavenlyStem(heavenly_stem.value), EarthlyBranch(earthly_branch.value)

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
        return HeavenlyStem(heavenly_stem.value), EarthlyBranch(earthly_branch.value)



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

def calculate_day_heavenly_with_half(year, month, day, hour, mins):

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
    logger.info(f"Input stem {stem} with {heavenly_index}")
    if earthly_index.value > 7:
        offset = -5
    else:
        offset = 5
    stemIndex = getSixtyStemIndex(stem)
    logger.info(f"output stem {SixtyStem(stemIndex + offset)}")
    return SixtyStem(stemIndex + offset)

def calculate_dark_stem(heavenly_index, earthly_index, direction: Direction = Direction.CLOCKWISE):
    """
    Calculate the dark stem based on heavenly and earthly indices and direction.

    Args:
        heavenly_index: The heavenly stem index
        earthly_index: The earthly branch index
        direction: Direction.CLOCKWISE or Direction.ANTICLOCKWISE (default: CLOCKWISE)

    Returns:
        SixtyStem: The calculated dark stem
    """
    stem = resolveHeavenlyStem(heavenly_index) + resolveEarthlyBranch(earthly_index)

    if direction == Direction.CLOCKWISE:
        offset = 5
    else:  # ANTICLOCKWISE
        offset = -5

    stemIndex = getSixtyStemIndex(stem)
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
    solarterms = [ "DongZhi", "XiaoHan", "DaHan", "LiChun",
        "YuShui", "JingZhe", "ChunFen", "QingMing", "GuYu",
        "LiXia", "XiaoMan", "MangZhong", "XiaZhi", "XiaoShu", "DaShu",
        "LiQiu", "ChuShu", "BaiLu", "QiuFen", "HanLu", "ShuangJiang",
        "LiDong", "XiaoXue", "DaXue", "DongZhi","XiaoHan", 
    ]
    # date_list = date_list[:-1]
    # Merge the three lists into a DataFrame
    df = pd.DataFrame(list(zip(solarterms, date_list, date_list[1:] + [date_list[0]])), columns=['solarterms', 'start_date', 'end_date'])
    
    df = df.iloc[:-1]
    # Update the end_date value for the row with index 21
    # df.loc[21, "end_date"] = solarterm.XiaoHan(target_date.year+1)

    logger.debug ("target_date is " + str(target_date))
    logger.debug(f"df.loc[21]['end_date'] is {df.loc[21]['end_date']}")
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


def half_pillar(hour_stem: HeavenlyStem, hour_branch: EarthlyBranch) -> str:
    """
    Calculate the half pillar value by adding 15 to the combined value of heavenly stem and earthly branch.
    If the result exceeds 60, it wraps around to the beginning.
    
    Args:
        hour_stem: HeavenlyStem enum value
        hour_branch: EarthlyBranch enum value
        
    Returns:
        int: The calculated half pillar value
    """
    # Get the Chinese characters for the stem and branch
    stem_cn = HeavenlyStemCN[hour_stem.name].value
    branch_cn = EarthlyBranchCN[hour_branch.name].value
    
    # Combine them to get the key for heavenly_earthly_dict
    combined = stem_cn + branch_cn
    
    # Get the base value from the dictionary
    base_value = heavenly_earthly_dict[combined]
    
    # Add 15 and handle wrapping around
    result = base_value + 15
    if result > 60:
        result = result - 60
        
    return SixtyStem(result)

def hidden_pillar(hour_stem: HeavenlyStem, hour_branch: EarthlyBranch, direction: Direction = Direction.CLOCKWISE) -> str:
    """
    Calculate the hidden pillar value by moving 5 positions forward or backward.
    
    Args:
        hour_stem: HeavenlyStem enum value
        hour_branch: EarthlyBranch enum value
        direction: Direction enum value (CLOCKWISE for forward, ANTICLOCKWISE for backward)
        
    Returns:
        str: The calculated hidden pillar value
    """
    # Get the Chinese characters for the stem and branch
    stem_cn = HeavenlyStemCN[hour_stem.name].value
    branch_cn = EarthlyBranchCN[hour_branch.name].value
    
    # Combine them to get the key for heavenly_earthly_dict
    combined = stem_cn + branch_cn
    
    # Get the base value from the dictionary
    base_value = heavenly_earthly_dict[combined]
    
    # Add or subtract 5 based on direction
    if direction == Direction.CLOCKWISE:
        result = base_value + 5
    else:
        result = base_value - 5
    
    # Handle wrapping around (both forward and backward)
    if result > 60:
        result = result - 60
    elif result <= 0:
        result = result + 60
        
    return SixtyStem(result)

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
      heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_with_half(year, month, day, hour, 15)
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
    heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_with_half(year, month, day, hour, 15)
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
    heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_with_half(year, month, day, hour, 15)
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
def get_ymdh_current(year: int, month: int, day: int, hour: int): 
    return get_heavenly_branch_ymdh_pillars_current_flip_Option_2(year, month, day, hour, True)
    
def get_ymdh_base(year: int, month: int, day: int, hour: int): 
    print("===============base===============")
    return get_heavenly_branch_ymdh_pillars_current_flip_Option_2(year, month, day, hour, False)

def get_heavenly_branch_ymdh_pillars_current_flip_Option_2(year: int, month: int, day: int, hour: int,
    is_current: bool = False):
    # Calculate normal heavenly stems and earthly branches
    input_date =  datetime(year, month, day, hour)

    if (is_current):
        heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
        heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_with_half(year, month, day, hour, 15)
        # heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
        heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time(year, month, day)
    else:
        heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_baselife_time(year, month, day, hour)
        heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_base(year, month, day, hour, 15)
        heavenly_stem, earthly_branch = calculate_year_heavenly(year, month, day)
        

    heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)

    self_dir, external_dir = HeavenlyStemYinYang.get_directions(heavenly_day_stem, heavenly_stem, Polarity.YANG)
    
    dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem, self_dir)
    dark_day_stem = calculate_dark_stem(heavenly_day_stem, earthly_day_stem, self_dir)
    dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem, external_dir)
    dark_year_stem = calculate_dark_stem(heavenly_stem, earthly_branch,external_dir )

    # Create the flipped pillars using the 'earthly_flip' function
    haaped_year_stem, haaped_year_branch = haap_po_xin(heavenly_stem,  earthly_branch, external_dir, JoinType.HAAP)
    haaped_month_stem, haaped_month_branch = haap_po_xin(heavenly_month_stem,  earthly_month_stem, external_dir, JoinType.HAAP)
    haaped_day_stem, haaped_day_branch = haap_po_xin(heavenly_day_stem,  earthly_day_stem, self_dir, JoinType.HAAP)
    haaped_hour_stem, haaped_hour_branch = haap_po_xin(heavenly_hour_stem,  earthly_hour_stem, self_dir, JoinType.HAAP)

    haaped_dark_year_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_year_stem[0]),  converter.chinese_to_enum(dark_year_stem[1]), external_dir, JoinType.HAAP)
    haaped_dark_month_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_month_stem[0]),  converter.chinese_to_enum(dark_month_stem[1]), external_dir, JoinType.HAAP)
    haaped_dark_day_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_day_stem[0]),  converter.chinese_to_enum(dark_day_stem[1]), self_dir, JoinType.HAAP)
    haaped_dark_hour_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_hour_stem[0]),  converter.chinese_to_enum(dark_hour_stem[1]), self_dir, JoinType.HAAP)
    # haaped_dark_hour_stem = calculate_dark_stem(haaped_hour_stem, haaped_hour_branch, self_dir)
    # haaped_dark_day_stem = calculate_dark_stem(haaped_day_stem, haaped_day_branch, self_dir)
    # haaped_dark_month_stem = calculate_dark_stem(haaped_month_stem, haaped_month_branch, external_dir)
    # haaped_dark_year_stem = calculate_dark_stem(haaped_year_stem, haaped_year_branch,external_dir )

    # Create the flipped pillars using the 'earthly_flip' function
    hai_year_stem, hai_year_branch = haap_po_xin(heavenly_stem,  earthly_branch, external_dir, JoinType.HAI)
    hai_month_stem, hai_month_branch = haap_po_xin(heavenly_month_stem,  earthly_month_stem, external_dir, JoinType.HAI)
    hai_day_stem, hai_day_branch =  haap_po_xin(heavenly_day_stem,  earthly_day_stem, self_dir, JoinType.HAI)
    hai_hour_stem, hai_hour_branch = haap_po_xin(heavenly_hour_stem,  earthly_hour_stem, self_dir, JoinType.HAI)


    hai_dark_year_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_year_stem[0]),  converter.chinese_to_enum(dark_year_stem[1]), external_dir, JoinType.HAI)
    hai_dark_month_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_month_stem[0]),  converter.chinese_to_enum(dark_month_stem[1]), external_dir, JoinType.HAI)
    hai_dark_day_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_day_stem[0]),  converter.chinese_to_enum(dark_day_stem[1]), self_dir, JoinType.HAI)
    hai_dark_hour_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_hour_stem[0]),  converter.chinese_to_enum(dark_hour_stem[1]), self_dir, JoinType.HAI)

    # hai_dark_hour_stem = calculate_dark_stem(hai_hour_stem, hai_hour_branch, self_dir)
    # hai_dark_day_stem = calculate_dark_stem(hai_day_stem, hai_day_branch, self_dir)
    # hai_dark_month_stem = calculate_dark_stem(hai_month_stem, hai_month_branch, external_dir)
    # hai_dark_year_stem = calculate_dark_stem(hai_year_stem, hai_year_branch,external_dir )



    # Create the flipped pillars using the 'earthly_flip' function
    po_year_stem, po_year_branch =haap_po_xin(heavenly_stem,  earthly_branch, external_dir, JoinType.PO)
    po_month_stem, po_month_branch = haap_po_xin(heavenly_month_stem,  earthly_month_stem, external_dir, JoinType.PO)
    po_day_stem, po_day_branch = haap_po_xin(heavenly_day_stem,  earthly_day_stem, self_dir, JoinType.PO)
    po_hour_stem, po_hour_branch = haap_po_xin(heavenly_hour_stem,  earthly_hour_stem, self_dir, JoinType.PO)

    po_dark_year_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_year_stem[0]),  converter.chinese_to_enum(dark_year_stem[1]), external_dir, JoinType.PO)
    po_dark_month_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_month_stem[0]),  converter.chinese_to_enum(dark_month_stem[1]), external_dir, JoinType.PO)
    po_dark_day_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_day_stem[0]),  converter.chinese_to_enum(dark_day_stem[1]), self_dir, JoinType.PO)
    po_dark_hour_stem = to_pillar_haap_po_xin(converter.chinese_to_enum(dark_hour_stem[0]),  converter.chinese_to_enum(dark_hour_stem[1]), self_dir, JoinType.PO)
    # po_dark_hour_stem = calculate_dark_stem( po_hour_stem,  po_hour_branch, self_dir)
    # po_dark_day_stem = calculate_dark_stem( po_day_stem,  po_day_branch, self_dir)
    # po_dark_month_stem = calculate_dark_stem( po_month_stem,  po_month_branch, external_dir)
    # po_dark_year_stem = calculate_dark_stem( po_year_stem, po_year_branch,external_dir )

    daiYun = json_daiYun("male", resolveHeavenlyStem(heavenly_stem) + resolveEarthlyBranch(earthly_branch),
                         resolveHeavenlyStem(heavenly_month_stem) + resolveEarthlyBranch(earthly_month_stem), 
                         input_date)

    # Calculate flip pillars
    flip_pillars = calculate_flip_pillars(
        base_year=year,
        base_month=month,
        base_day=day,
        base_hour=hour,
        gender="male",
        current_date=datetime.now(),
        is_current=False
    )
    # Calculate SiYun sequence using same parameters as DaYun
    siyun = calculate_siyun(
        gender="male", 
        hour_pillar=resolveHeavenlyStem(heavenly_hour_stem) + resolveEarthlyBranch(earthly_hour_stem),
        year_stem=resolveHeavenlyStem(heavenly_stem),
        base_date=input_date
    )
    # Format siyun results same as daiYun
    siyun_formatted = []
    for pillar, age in zip(siyun[0], siyun[1]):
        siyun_formatted.append({
            "stem": pillar[0],
            "branch": pillar[1], 
            "chinese": pillar,
            "starting_age": round(age, 1)
        })
    return {
        "時": resolveHeavenlyStem(heavenly_hour_stem) + resolveEarthlyBranch(earthly_hour_stem),
        "日": resolveHeavenlyStem(heavenly_day_stem) + resolveEarthlyBranch(earthly_day_stem),
        "-日": dark_day_stem,
        "-時": dark_hour_stem,
        "月": resolveHeavenlyStem(heavenly_month_stem) + resolveEarthlyBranch(earthly_month_stem),
        "年": resolveHeavenlyStem(heavenly_stem) + resolveEarthlyBranch(earthly_branch),
        "-年": dark_year_stem,
        "-月": dark_month_stem,
  

        # Add haap pillars to the output
        "合時": resolveHeavenlyStem(haaped_hour_stem) + resolveEarthlyBranch(haaped_hour_branch),
        "合日": resolveHeavenlyStem(haaped_day_stem) + resolveEarthlyBranch(haaped_day_branch),
        "-合日": haaped_dark_day_stem, ## resolveHeavenlyStem(haaped_day_stem) + resolveEarthlyBranch(haaped_day_branch),
        "-合時": haaped_dark_hour_stem, ## resolveHeavenlyStem(haaped_hour_stem) + resolveEarthlyBranch(haaped_hour_branch),
        "合月": resolveHeavenlyStem(haaped_month_stem) + resolveEarthlyBranch(haaped_month_branch),
        "合年": resolveHeavenlyStem(haaped_year_stem) + resolveEarthlyBranch(haaped_year_branch),
        "-合年": haaped_dark_year_stem, ##resolveHeavenlyStem(haaped_day_stem) + resolveEarthlyBranch(haaped_day_branch),
        "-合月": haaped_dark_month_stem,##resolveHeavenlyStem(haaped_hour_stem) + resolveEarthlyBranch(haaped_hour_branch),
         
        
        
        # Add hai pillars to the output
        "害時": resolveHeavenlyStem(hai_hour_stem) + resolveEarthlyBranch(hai_hour_branch),
        "害日": resolveHeavenlyStem(hai_day_stem) + resolveEarthlyBranch(hai_day_branch),
        "-害日": hai_dark_day_stem, #resolveHeavenlyStem(hai_day_stem) + resolveEarthlyBranch(hai_day_branch),
        "-害時": hai_dark_hour_stem, ##resolveHeavenlyStem(hai_hour_stem) + resolveEarthlyBranch(hai_hour_branch),
        "害月": resolveHeavenlyStem(hai_month_stem) + resolveEarthlyBranch(hai_month_branch),
        "害年": resolveHeavenlyStem(hai_year_stem) + resolveEarthlyBranch(hai_year_branch),
        "-害年": hai_dark_year_stem, ##resolveHeavenlyStem(hai_year_stem) + resolveEarthlyBranch(hai_year_branch),
        "-害月": hai_dark_month_stem, ##resolveHeavenlyStem(hai_month_stem) + resolveEarthlyBranch(hai_month_branch),

        # Add po pillars to the output
        "破時": resolveHeavenlyStem(po_hour_stem) + resolveEarthlyBranch(po_hour_branch),
        "破日": resolveHeavenlyStem(po_day_stem) + resolveEarthlyBranch(po_day_branch),
        "-破日": po_dark_day_stem, ##resolveHeavenlyStem(po_day_stem) + resolveEarthlyBranch(po_day_branch),
        "-破時": po_dark_hour_stem, ##resolveHeavenlyStem(po_hour_stem) + resolveEarthlyBranch(po_hour_branch),
        "破月": resolveHeavenlyStem(po_month_stem) + resolveEarthlyBranch(po_month_branch),
        "破年": resolveHeavenlyStem(po_year_stem) + resolveEarthlyBranch(po_year_branch),
        "-破年": po_dark_year_stem, ##resolveHeavenlyStem(po_year_stem) + resolveEarthlyBranch(po_year_branch),
        "-破月": po_dark_month_stem, ##resolveHeavenlyStem(po_month_stem) + resolveEarthlyBranch(po_month_branch),
# 刑,衝,破,害 
        "大運": daiYun,
        "時運": siyun_formatted,

        # Add flip pillars with Chinese word "fan"
        "反時": flip_pillars["時"],
        "反日": flip_pillars["日"], 
        "-反日": flip_pillars["-日"],
        "-反時": flip_pillars["-時"],
        "反月": flip_pillars["月"],
        "反年": flip_pillars["年"],
        "-反年": flip_pillars["-年"],
        "-反月": flip_pillars["-月"], 

    }


from enum import Enum
from datetime import datetime

# Define the 8wPillar ENUM
class Pillar(Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"

class JoinType(Enum):
    HAAP = "HAAP"
    PO = "PO"
    XIN = "XIN"
    HAI = "HAI"

# # Define the Direction ENUM for return values
# class Direction(Enum):
#     FORWARD = "FORWARD"
#     BACKWARD = "BACKWARD"

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
    return Direction.CLOCKWISE if delta < 0 else Direction.ANTICLOCKWISE

# Flip pillar based on direction
def flip_pillar(year: int, month: int, day: int, hour: int, pillar: Pillar):
    # Call the relevant functions based on pillar
    if pillar == Pillar.MONTH:
        heavenly_month_stem, earthly_month_stem = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
        dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    elif pillar == Pillar.YEAR:
        heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    elif pillar == Pillar.DAY:
        heavenly_day_stem, earthly_day_stem = calculate_day_heavenly_with_half(year, month, day, hour, 15)
    elif pillar == Pillar.HOUR:
        heavenly_hour_stem, earthly_hour_stem = calculate_hour_heavenly(year, month, day, hour)
        dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem)

    # Call the direction checker
    direction = pillar_forward_or_backward(year, month, day, hour, pillar)

    # If the direction is forward, call earthly_flip
    # TODO: What should FLIP DO? 
    earthly_haap_po_xin_old(year, month, day, hour, pillar, direction, JoinType.HAAP)

earthly_branch_haap_pairs = {
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

earthly_branch_xin_pairs = {
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

earthly_branch_chong_pairs = {
    EarthlyBranch.ZI: (EarthlyBranch.CHOU, 1),   # ZI -> CHOU is 1 step forward
    EarthlyBranch.YIN: (EarthlyBranch.HAI, 9),   # YIN -> HAI is 9 steps forward
    EarthlyBranch.MAO: (EarthlyBranch.XU, 7),    # MAO -> XU is 7 steps forward
    EarthlyBranch.CHEN: (EarthlyBranch.YOU, 5),  # CHEN -> YOU is 5 steps forward
    EarthlyBranch.SI: (EarthlyBranch.SHEN, 3),   # SI -> SHEN is 3 steps forward
    EarthlyBranch.WU: (EarthlyBranch.WEI, 1),    # WU -> WEI is 1 step forward
    EarthlyBranch.CHOU: (EarthlyBranch.ZI, 11),   # CHOU -> ZI is 11 steps backward
    EarthlyBranch.HAI: (EarthlyBranch.YIN, 3),    # HAI -> YIN is 3 steps backward
    EarthlyBranch.XU: (EarthlyBranch.MAO, 5),     # XU -> MAO is 5 steps backward
    EarthlyBranch.YOU: (EarthlyBranch.CHEN, 7),   # YOU -> CHEN is 7 steps backward
    EarthlyBranch.SHEN: (EarthlyBranch.SI, 9),    # SHEN -> SI is 9 steps backward
    EarthlyBranch.WEI: (EarthlyBranch.WU, 11)     # WEI -> WU is 11 steps backward
}

earthly_branch_po_pairs = {
    EarthlyBranch.ZI: (EarthlyBranch.YOU, 9),   # ZI -> CHOU is 1 step forward
    EarthlyBranch.CHOU: (EarthlyBranch.CHEN, 3),   # YIN -> HAI is 9 steps forward
    EarthlyBranch.YIN: (EarthlyBranch.HAI, 9),    # MAO -> XU is 7 steps forward
    EarthlyBranch.MAO: (EarthlyBranch.WU, 3),  # CHEN -> YOU is 5 steps forward
    EarthlyBranch.CHEN: (EarthlyBranch.CHOU, 9),  # CHEN -> YOU is 5 steps forward
    EarthlyBranch.SI: (EarthlyBranch.SHEN, 3),   # SI -> SHEN is 3 steps forward
    EarthlyBranch.WU: (EarthlyBranch.MAO, 9),   # SI -> SHEN is 3 steps forward
    EarthlyBranch.WEI: (EarthlyBranch.XU, 3),    # WU -> WEI is 1 step forward
    EarthlyBranch.SHEN: (EarthlyBranch.SI, 9),    # WU -> WEI is 1 step forward
    EarthlyBranch.YOU: (EarthlyBranch.ZI, 3),    # WU -> WEI is 1 step forward
    EarthlyBranch.XU: (EarthlyBranch.WEI, 9),    # WU -> WEI is 1 step forward
    EarthlyBranch.HAI: (EarthlyBranch.YIN, 3),    # WU -> WEI is 1 step forward

}

earthly_branch_hai_pairs = {
    EarthlyBranch.ZI: (EarthlyBranch.WEI, 7),   # ZI -> CHOU is 1 step forward
    EarthlyBranch.CHOU: (EarthlyBranch.WU, 5),   # YIN -> HAI is 9 steps forward
    EarthlyBranch.YIN: (EarthlyBranch.SI, 3),    # MAO -> XU is 7 steps forward
    EarthlyBranch.MAO: (EarthlyBranch.CHEN, 1),  # CHEN -> YOU is 5 steps forward
    EarthlyBranch.CHEN: (EarthlyBranch.MAO, 1),  # CHEN -> YOU is 5 steps forward
    EarthlyBranch.SI: (EarthlyBranch.YIN, 9),   # SI -> SHEN is 3 steps forward
    EarthlyBranch.WU: (EarthlyBranch.CHOU, 7),   # SI -> SHEN is 3 steps forward
    EarthlyBranch.WEI: (EarthlyBranch.ZI, 5),    # WU -> WEI is 1 step forward
    EarthlyBranch.SHEN: (EarthlyBranch.HAI, 3),    # WU -> WEI is 1 step forward
    EarthlyBranch.YOU: (EarthlyBranch.XU, 1),    # WU -> WEI is 1 step forward
    EarthlyBranch.XU: (EarthlyBranch.YOU, 1),    # WU -> WEI is 1 step forward
    EarthlyBranch.HAI: (EarthlyBranch.SHEN, 9),    # WU -> WEI is 1 step forward
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

    
def earthly_haap_po_xin_old(year: int, month: int, day: int, hour: int, pillar: Pillar, direction: Direction, type: JoinType ):
    """
    This function adjusts the Heavenly Stem and Earthly Branch based on the selected pillar (year, month, day, or hour) 
    and the direction (forward or backward). The adjustments are based on defined relationships between 
    Earthly Branches and Heavenly Stems.
    
    Returns:
        new_stem (HeavenlyStem): The new Heavenly Stem 
        paired_earthly_branch (EarthlyBranch): The new Earthly Branch
    """

    # Identify the Heavenly Stem and Earthly Branch based on the pillar type
    if pillar == Pillar.MONTH:
        heavenly_stem, earthly_branch = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
    elif pillar == Pillar.YEAR:
        heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    elif pillar == Pillar.DAY:
        heavenly_stem, earthly_branch = calculate_day_heavenly_with_half(year, month, day, hour, 15)
    elif pillar == Pillar.HOUR:
        heavenly_stem, earthly_branch = calculate_hour_heavenly(year, month, day, hour)
    # elif pillar == Pillar.DARKMONTH:
    #     dark_month_stem = calculate_dark_stem(heavenly_month_stem, earthly_month_stem)
    # elif pillar == Pillar.DARKHOUR:
    #     dark_hour_stem = calculate_dark_stem(heavenly_hour_stem, earthly_hour_stem)
    # elif pillar == Pillar.DARKYEAR:
    #     dark_year_stem = calculate_dark_stem(heavenly_stem, earthly_branch)
    return haap_po_xin(heavenly_stem, earthly_branch, direction, type)       
def to_pillar_haap_po_xin (heavenly_stem: HeavenlyStem,  earthly_branch: EarthlyBranch, direction: Direction, type: JoinType ):
    out_heavenly, out_earthly = haap_po_xin(heavenly_stem,  earthly_branch, direction, type )
    return resolveHeavenlyStem(out_heavenly) + resolveEarthlyBranch(out_earthly)
    
def haap_po_xin(heavenly_stem: HeavenlyStem,  earthly_branch: EarthlyBranch, direction: Direction, type: JoinType ):

    # Convert to enum based on the new EarthlyBranch Enum (expects `earthly_branch` as an integer)
    earthly_branch_enum = EarthlyBranch(earthly_branch)

    # Define all Heavenly Stems in a list for cycle operations
    heavenly_stems = list(HeavenlyStem)

    match type:
        case JoinType.XIN:
            # Get the associated pair and step count for the given Earthly Branch
            paired_earthly_branch, steps_forward = earthly_branch_xin_pairs.get(earthly_branch_enum, (None, 0))
        case JoinType.PO:
            # Get the associated pair and step count for the given Earthly Branch
            paired_earthly_branch, steps_forward = earthly_branch_po_pairs.get(earthly_branch_enum, (None, 0))
            logger.debug(f"Earthly : {earthly_branch_enum}")
        case JoinType.HAI:
            # Get the associated pair and step count for the given Earthly Branch
            paired_earthly_branch, steps_forward = earthly_branch_hai_pairs.get(earthly_branch_enum, (None, 0))
        case JoinType.HAAP: 
            # Get the associated pair and step count for the given Earthly Branch
            paired_earthly_branch, steps_forward = earthly_branch_haap_pairs.get(earthly_branch_enum, (None, 0))

    # If there is no pair or step count, handle the error or set default
    if paired_earthly_branch is None:
        logger.debug(f"No pair found for earthly branch {earthly_branch_enum}")
        return None, None

    # Determine the number of steps to move based on direction
    if direction == Direction.CLOCKWISE:
        step_count = steps_forward  # Move forward by the given steps
    else:
        match type:
            case JoinType.XIN:
                # Get the associated pair and step count for the given Earthly Branch
                reverse_earthly_branch, steps_forward = earthly_branch_xin_pairs.get(paired_earthly_branch, (None, 0))
            case JoinType.PO:
                # Get the associated pair and step count for the given Earthly Branch
                reverse_earthly_branch, steps_forward = earthly_branch_po_pairs.get(paired_earthly_branch, (None, 0))
            case JoinType.HAI:
                # Get the associated pair and step count for the given Earthly Branch
                reverse_earthly_branch, steps_forward = earthly_branch_hai_pairs.get(paired_earthly_branch, (None, 0))
            case JoinType.HAAP: 
                # Get the associated pair and step count for the given Earthly Branch
                reverse_earthly_branch, steps_forward = earthly_branch_haap_pairs.get(paired_earthly_branch, (None, 0))
        step_count = -1 * steps_forward  # Move backward in a 12-branch cycle

    # Convert the current Heavenly Stem to its enum if necessary
    heavenly_stem_enum = HeavenlyStem(heavenly_stem)

    # Calculate the new Heavenly Stem index
    current_index = heavenly_stems.index(heavenly_stem_enum)  # Find the index of the current stem
    new_index = (current_index + step_count) % len(heavenly_stems)  # Calculate the new index with wrapping
    new_stem = heavenly_stems[new_index]  # Get the new Heavenly Stem
    old_stem = heavenly_stems[current_index]
    logger.debug(f"new steam : {new_stem, paired_earthly_branch}")

    # Return both the new Heavenly Stem and the paired Earthly Branch
    return new_stem, paired_earthly_branch

def earthly_flip_2(year: int, month: int, day: int, hour: int, pillar: Pillar, direction: Direction):


    # Identify the Heavenly Stem and Earthly Branch based on the pillar type
    if pillar == Pillar.MONTH:
        heavenly_stem, earthly_branch = calculate_month_heavenly_withSeason_for_current_time(year, month, day, hour)
    elif pillar == Pillar.YEAR:
        heavenly_stem, earthly_branch = calculate_year_heavenly_for_current_time_Option_2(year, month, day)
    elif pillar == Pillar.DAY:
        heavenly_stem, earthly_branch = calculate_day_heavenly_with_half(year, month, day, hour, 15)
    elif pillar == Pillar.HOUR:
        heavenly_stem, earthly_branch = calculate_hour_heavenly(year, month, day, hour)

    print(resolveHeavenlyStem(heavenly_stem))
    # Convert heavenly_stem to enum, assuming functions return strings
    heavenly_stem_enum = HeavenlyStemCN[resolveHeavenlyStem(heavenly_stem)]  # e.g., "甲" becomes HeavenlyStemCN.JIA
    earthly_branch_enum = EarthlyBranchCN[resolveEarthlyBranch(earthly_branch)]  # e.g., "子" becomes EarthlyBranchCN.ZI

    # List of all Heavenly Stem CNs in cycle order
    heavenly_stems = list(HeavenlyStemCN)

    # Get the associated pair and step count for the given earthly branch
    paired_earthly_branch, steps_forward = earthly_branch_haap_pairs.get(earthly_branch_enum, (None, 0))

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

@staticmethod
def get_directions(stem1: 'HeavenlyStemYinYang', 
                  stem2: 'HeavenlyStemYinYang', 
                  polarity: Polarity) -> tuple[Direction, Direction]:
    """
    Determine the self and external directions based on two stems and a polarity.

    Rules:
    1. If stem1 is Yang and stem2 is Yin:
       - For Yang polarity: [Clockwise, AntiClockwise]
       - For Yin polarity: [AntiClockwise, Clockwise]

    2. If both stems are Yin:
       - For Yang polarity: [Clockwise, Clockwise]
       - For Yin polarity: [AntiClockwise, AntiClockwise]

    Args:
        stem1: First HeavenlyStemYinYang
        stem2: Second HeavenlyStemYinYang
        polarity: Target Polarity (Yin or Yang)

    Returns:
        tuple[Direction, Direction]: (SelfDirection, ExternalDirection)
    """
    # Case 1: stem1 is Yang and stem2 is Yin
    if stem1.is_yang and stem2.is_yin:
        if polarity == Polarity.YANG:
            return (Direction.CLOCKWISE, Direction.ANTICLOCKWISE)
        else:  # Yin polarity
            return (Direction.ANTICLOCKWISE, Direction.CLOCKWISE)

    # Case 2: both stems are Yin
    elif stem1.is_yin and stem2.is_yin:
        if polarity == Polarity.YANG:
            return (Direction.CLOCKWISE, Direction.CLOCKWISE)
        else:  # Yin polarity
            return (Direction.ANTICLOCKWISE, Direction.ANTICLOCKWISE)

    # Default case (both Yang or other combinations)
    if polarity == Polarity.YANG:
        return (Direction.CLOCKWISE, Direction.CLOCKWISE)
    else:  # Yin polarity
        return (Direction.ANTICLOCKWISE, Direction.ANTICLOCKWISE)
    
# if __name__ == "__main__":
# # Test Case 1: Yang stem1, Yin stem2, Yang polarity
# print("Test Case 1: Yang stem1, Yin stem2, Yang polarity")
# result = HeavenlyStemYinYang.get_directions(
#     HeavenlyStemYinYang.JIA,  # Yang
#     HeavenlyStemYinYang.YI,   # Yin
#     Polarity.YANG
# )
# print(f"Result: {[d.value for d in result]}\n")

# # Test Case 2: Yang stem1, Yin stem2, Yin polarity
# print("Test Case 2: Yang stem1, Yin stem2, Yin polarity")
# result = HeavenlyStemYinYang.get_directions(
#     HeavenlyStemYinYang.JIA,  # Yang
#     HeavenlyStemYinYang.YI,   # Yin
#     Polarity.YIN
# )
# print(f"Result: {[d.value for d in result]}\n")

# # Test Case 3: Both Yin stems, Yang polarity
# print("Test Case 3: Both Yin stems, Yang polarity")
# result = HeavenlyStemYinYang.get_directions(
#     HeavenlyStemYinYang.YI,   # Yin
#     HeavenlyStemYinYang.DING, # Yin
#     Polarity.YANG
# )
# print(f"Result: {[d.value for d in result]}\n")

# # Test Case 4: Both Yin stems, Yin polarity
# print("Test Case 4: Both Yin stems, Yin polarity")
# result = HeavenlyStemYinYang.get_directions(
#     HeavenlyStemYinYang.YI,   # Yin
#     HeavenlyStemYinYang.DING, # Yin
#     Polarity.YIN
# )
# print(f"Result: {[d.value for d in result]}")



def get_wuxi_ymdh_base(year: int, month: int, day: int, hour: int) -> dict:
    """
    Calculate the basic four pillars (YMDH) for a given date and time.
    Returns in Chinese characters format.
    """
    # Calculate pillars (using previous logic)
    # year_stem = HeavenlyStem((year - 3) % 10)
    # year_branch = EarthlyBranch((year - 3) % 12)
    year_stem, year_branch = calculate_year_heavenly(year, month, day)

    # month_stem = HeavenlyStem(((year % 10 + 2) * 2 + month) % 10)
    # month_branch = EarthlyBranch((month + 2) % 12)
    month_stem, month_branch = calculate_month_heavenly_withSeason_for_baselife_time(year, month, day, hour)
    day_stem, day_branch = calculate_day_heavenly_base(year, month, day, hour, 15)
    
    hour_stem, hour_branch =   calculate_hour_heavenly(year, month, day, hour)

    # Get hidden stems based on year stem polarity
    is_yang = year_stem.value % 2 == 1
    hd_direction = Direction.ANTICLOCKWISE if is_yang else Direction.CLOCKWISE
    my_direction = Direction.CLOCKWISE if is_yang else Direction.ANTICLOCKWISE
    # Calculate hidden stems for each pillar using consistent direction
    
    hour_hidden = hidden_pillar(hour_stem, hour_branch, hd_direction)
    day_hidden = hidden_pillar(day_stem, day_branch, hd_direction)
    month_hidden = hidden_pillar(month_stem, month_branch, my_direction)
    year_hidden = hidden_pillar(year_stem, year_branch, my_direction)
    # Convert to Chinese characters
    return {
        "時": HeavenlyStemCN[hour_stem.name].value + EarthlyBranchCN[hour_branch.name].value,
        "日": HeavenlyStemCN[day_stem.name].value + EarthlyBranchCN[day_branch.name].value,
        "-時": hour_hidden,
        "-日": day_hidden,
        "月": HeavenlyStemCN[month_stem.name].value + EarthlyBranchCN[month_branch.name].value,
        "年": HeavenlyStemCN[year_stem.name].value + EarthlyBranchCN[year_branch.name].value,
        "-年": year_hidden,
        "-月": month_hidden,
    }


def get_stem_pairs(stem: HeavenlyStem, branch: EarthlyBranch) -> list:
    """
    Get the heavenly stem pairs in the correct order based on the element cycle,
    with branches determined by the input branch and its +15 cycle.
    
    Args:
        stem: HeavenlyStem enum value
        branch: EarthlyBranch enum value
        
    Returns:
        list: List of stem-branch pairs following the element cycle
    """
    # Determine starting element and element order
    if stem in [HeavenlyStem.JIA]:
        element_order = ["earth", "gold", "water", "wood", "fire"]
        
    elif stem in [HeavenlyStem.YI]:
        element_order = ["gold", "water", "wood", "fire", "earth"]
    elif stem in [HeavenlyStem.BING]:
        element_order = ["water", "wood", "fire", "earth", "gold"]
    elif stem in [ HeavenlyStem.DING]:
        element_order = ["wood", "fire", "earth", "gold", "water"]
    elif stem in [HeavenlyStem.WU]:
        element_order = [ "fire", "earth", "gold", "water", "wood"]
    elif stem in [HeavenlyStem.JI]:
        element_order = ["earth", "gold", "water", "wood", "fire"]
    elif stem in [HeavenlyStem.GENG]:
        element_order = ["gold", "water", "wood", "fire", "earth"]
    elif stem in [HeavenlyStem.XIN]:
        element_order =  ["water", "wood", "fire", "earth", "gold"]
    elif stem in [HeavenlyStem.REN]:
        element_order = ["wood", "fire", "earth", "gold", "water"]
    else:  # REN, GUI
        element_order = [ "fire", "earth", "gold", "water", "wood"]

    # Get the initial stem-branch combination
    initial_stem_cn = resolveHeavenlyStem(stem)
    initial_branch_cn = resolveEarthlyBranch(branch)
    initial_combo = initial_stem_cn + initial_branch_cn
    
    # Get the base value from heavenly_earthly_dict
    base_value = heavenly_earthly_dict[initial_combo]
    
    # Calculate the +15 value
    plus_15_value = ((base_value + 15 - 1) % 60) + 1
    
    # Get the stem-branch combination for +15
    plus_15_combo = SixtyStem(plus_15_value)
    
    # First 5 pairs use original branch
    first_five_branches = []
    current_branch_idx = branch.value
    for i in range(5):
        next_branch = EarthlyBranch((current_branch_idx) % 12)
        first_five_branches.append(resolveEarthlyBranch(next_branch))
    
    # Second 5 pairs use +15 branch
    second_five_branches = []
    plus_15_branch_idx = earthly_branch_enum[plus_15_combo[1]]
    for i in range(5):
        next_branch = EarthlyBranch((plus_15_branch_idx) % 12)
        second_five_branches.append(resolveEarthlyBranch(next_branch))
    
    # Define positive stems
    positive_stems = [HeavenlyStem.JIA, HeavenlyStem.BING, HeavenlyStem.WU, 
                     HeavenlyStem.GENG, HeavenlyStem.REN]
    
    # All possible stem pairs organized by elements
    element_pairs = {
        "fire": ("戊", "癸"),
        "earth": ("甲", "己"),
        "gold": ("庚", "乙"),
        "water": ("丙", "辛"),
        "wood": ("壬", "丁")
    }
    
    # Get stems in correct order
    ordered_pairs = [element_pairs[element] for element in element_order]
    if stem not in positive_stems:
        ordered_pairs = [(pair[1], pair[0]) for pair in ordered_pairs]
    
    # Combine stems with their respective branches
    result = []
    for i, pair in enumerate(ordered_pairs):
        if i < 2:
            result.extend([f"{pair[0]}{first_five_branches[i]}", 
                         f"{pair[1]}{first_five_branches[i]}"])
        elif i == 2:
            result.extend([f"{pair[0]}{first_five_branches[i]}", 
                         f"{pair[1]}{second_five_branches[i-5]}"])
        else:
            result.extend([f"{pair[0]}{second_five_branches[i-5]}", 
                         f"{pair[1]}{second_five_branches[i-5]}"])
    
    return result

def generate_hour_ranges(start_date: datetime) -> list:
    """
    Generate 10 time ranges within the hour, each spanning 6 minutes
    Each range is 60/10 = 6 minutes
    """
    ranges = []
    minutes_per_segment = 120 / 10  # 6 minutes per segment
    
    # Keep the hour fixed and only adjust minutes
    base_hour = start_date.replace(minute=0, second=0, microsecond=0)
    
    for i in range(10):
        range_start = base_hour + timedelta(minutes=i * minutes_per_segment)
        range_end = base_hour + timedelta(minutes=(i + 1) * minutes_per_segment)
        ranges.append(f"{range_start.strftime('%H:%M')}-{range_end.strftime('%H:%M')}")
    
    return ranges

def calculate_wu_yun(stem: HeavenlyStem, branch: EarthlyBranch, current_date: datetime, is_hour_cycle: bool = False) -> dict:
    """
    Calculate the Wu Yun (五運) cycle for a given stem and branch.
    
    Args:
        stem: HeavenlyStem enum value
        branch: EarthlyBranch enum value
        current_date: Current datetime to calculate ranges from
        is_hour_cycle: If True, calculate ranges for hour cycle (時運) instead of month cycle (月運)
        
    Returns:
        dict: Structure containing all components of the Wu Yun cycle
    """
    elements = get_element_cycle(stem)
    stems = get_stem_pairs(stem, branch)
    
    # Get current solar term information
    current_term_name, current_term_start, days_since_start = get_current_solar_term(current_date)
    
    # Get next solar term information
    solar_terms = get_solar_terms(current_date.year)
    days_to_next, next_solar_term_date_time, next_term_name = find_days_to_next_solar_term(current_date, solar_terms)
    
    # Find the index of current term in solar terms list
    current_term_index = None
    for i, term_date in enumerate(solar_terms):
        if term_date == current_term_start:
            current_term_index = i
            break
    
    # Check if previous term exists and is in the same month
    start_date = current_term_start
    if current_term_index is not None and current_term_index > 0:
        prev_term_date = solar_terms[current_term_index - 1]
        if prev_term_date.month == current_term_start.month:
            start_date = prev_term_date
    
    # Generate month ranges based on start date
    month_ranges = []

    if is_hour_cycle:
        # For hour cycle, start from 00:00 of the current day
        day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        month_ranges = generate_hour_ranges(day_start)
    else:
        for i in range(10):
            range_start = start_date + timedelta(days=i*3)
            range_end = range_start + timedelta(days=3)
            month_ranges.append(f"{range_start.strftime('%m/%d')}-{range_end.strftime('%m/%d')}")
    
    # Get Chinese characters for the pillar
    stem_cn = HeavenlyStemCN[stem.name].value
    branch_cn = EarthlyBranchCN[branch.name].value
    
    # Format dates as strings
    current_term_start_str = current_term_start.strftime('%Y-%m-%d %H:%M:%S')
    next_term_date_str = next_solar_term_date_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(next_solar_term_date_time, datetime) else None
    
    return {
        "pillar": f"{stem_cn}{branch_cn}",
        "elements": elements,
        "heavenlyStems": stems,
        "monthRanges": month_ranges,
        "solarTerm": {
            "current": {
                "name": current_term_name,
                "startDate": current_term_start_str,
                "daysSinceStart": days_since_start
            },
            "next": {
                "name": next_term_name,
                "startDate": next_term_date_str,
                "daysToNext": days_to_next
            }
        }
    }

def calculate_liu_qi(stem: HeavenlyStem, branch: EarthlyBranch) -> dict:
    """
    Calculate 六氣 (Liu Qi) based on a given stem and branch.
    
    Args:
        stem: HeavenlyStem enum value
        branch: EarthlyBranch enum value
        
    Returns:
        dict: Structure containing all components of the Liu Qi cycle
    """
    # Convert stem and branch to Chinese characters
    stem_cn = resolveHeavenlyStem(stem)
    branch_cn = resolveEarthlyBranch(branch)
    
    # Calculate upper heavens (stem and stem + 5)
    heavenly_stems = list(HeavenlyStemCN)
    current_stem_idx = [s.value for s in HeavenlyStemCN].index(stem_cn)
    upper_heaven_stems = [
        HeavenlyStemCN[heavenly_stems[current_stem_idx].name].value,
        HeavenlyStemCN[heavenly_stems[(current_stem_idx + 5) % 10].name].value  
    ]
    
    # Calculate middle earths (branch -1 to +4)
    earthly_branches = list(EarthlyBranchCN)
    current_branch_idx = [b.value for b in EarthlyBranchCN].index(branch_cn)
    middle_earths = [
        EarthlyBranchCN[earthly_branches[(current_branch_idx + i) % 12].name].value
        for i in range(-1, 5)  # -1, 0, 1, 2, 3, 4
    ]
    
    # Generate lower earths (starting from 子)
    zi_idx = [b.value for b in EarthlyBranchCN].index('子')
    lower_earths = [
        EarthlyBranchCN[earthly_branches[(zi_idx + i) % 12].name].value
        for i in range(12)
    ]
    
    # Chinese months (starting from 正)
    chinese_months = ['十一', '十二', '正', '二', '三', '四', '五', '六', 
                     '七', '八', '九', '十',  ]
    
    # Western months (starting from 11)
    western_months = [(i % 12) + 1 for i in range(11, 23)]
    
    return {
        "centerPillar": {
            "heaven": stem_cn,
            "earth": branch_cn
        },
        "upperHeavens": upper_heaven_stems,
        "middleEarths": middle_earths,
        "lowerEarths": lower_earths,
        "chineseMonths": chinese_months,
        "westernMonths": western_months
    }

def get_liu_xi_cycle(year: int, month: int, day: int, hour: int) -> dict:
    """
    Calculate the complete WuXi (五運六氣) cycles for a given date and time.
    
    Args:
        year: Year
        month: Month
        day: Day
        hour: Hour
        
    Returns:
        dict: Complete WuXi cycles for year and day
    """
    # Get the year and day pillars
    year_stem, year_branch = calculate_year_heavenly(year, month, day)
    day_stem, day_branch = calculate_day_heavenly_base(year, month, day, hour, 15)
    
    # Calculate cycles for both year and day
    year_cycle = calculate_liu_qi(year_stem, year_branch)
    day_cycle = calculate_liu_qi(day_stem, day_branch)
    
    return {
        "yearCycle": year_cycle,
        "dayCycle": day_cycle
    }


def get_element_cycle(stem: HeavenlyStem) -> list:
    """
    Get the five elements cycle starting from the element associated with the stem.
    """
    # Define the base elements with their emojis
    all_elements = [
        {"name": "木", "emoji": "🌳"},
        {"name": "火", "emoji": "🔥"},
        {"name": "土", "emoji": "🌎"},
        {"name": "金", "emoji": "🌟"},
        {"name": "水", "emoji": "💧"}
    ]
    
    # Determine starting index based on stem
    if stem in [HeavenlyStem.DING, HeavenlyStem.REN]:
        start_idx = 0  # Wood
    elif stem in [HeavenlyStem.WU, HeavenlyStem.GUI]:
        start_idx = 1  # Fire
    elif stem in [HeavenlyStem.JIA, HeavenlyStem.JI]:
        start_idx = 2  # Earth
    elif stem in [HeavenlyStem.GENG, HeavenlyStem.YI]:
        start_idx = 3  # Gold
    else:  # REN, GUI
        start_idx = 4  # Water
    
    # Rotate elements to start from the correct element
    return all_elements[start_idx:] + all_elements[:start_idx]

# def get_stem_pairs(stem: HeavenlyStem) -> list:
#     """
#     Get the heavenly stem pairs in the correct order based on the element cycle
#     and whether the input stem is positive or negative.
#     """
#     # Define positive stems
#     positive_stems = [HeavenlyStem.JIA, HeavenlyStem.BING, HeavenlyStem.WU, 
#                      HeavenlyStem.GENG, HeavenlyStem.REN]
    
#     # All possible pairs organized by elements
#     element_pairs = {
#         "fire": ("戊", "癸"),
#         "earth": ("甲", "己"),
#         "gold": ("庚", "乙"),
#         "water": ("丙", "辛"),
#         "wood": ("壬", "丁")
#     }
    
#     # Determine starting element based on stem
#     if stem in [HeavenlyStem.JIA, HeavenlyStem.YI]:
#         element_order = ["wood", "fire", "earth", "gold", "water"]
#     elif stem in [HeavenlyStem.BING, HeavenlyStem.DING]:
#         element_order = ["fire", "earth", "gold", "water", "wood"]
#     elif stem in [HeavenlyStem.WU, HeavenlyStem.JI]:
#         element_order = ["earth", "gold", "water", "wood", "fire"]
#     elif stem in [HeavenlyStem.GENG, HeavenlyStem.XIN]:
#         element_order = ["gold", "water", "wood", "fire", "earth"]
#     else:  # REN, GUI
#         element_order = ["water", "wood", "fire", "earth", "gold"]
    
#     # Get pairs in correct order
#     ordered_pairs = [element_pairs[element] for element in element_order]
    
#     # Reverse pairs if stem is not positive
#     if stem not in positive_stems:
#         ordered_pairs = [(pair[1], pair[0]) for pair in ordered_pairs]
    
#     # Flatten the pairs into a single list
#     return [stem for pair in ordered_pairs for stem in pair]

# def calculate_wu_yun(stem: HeavenlyStem, branch: EarthlyBranch) -> dict:
#     """
#     Calculate the Wu Yun (五運) cycle for a given stem and branch.
#     """
#     elements = get_element_cycle(stem)
#     stems = get_stem_pairs(stem)
    
#     # Generate month ranges
#     base_ranges = ['4-6', '7-9', '10-12', '13-15', '15-17', '18-20', '21-23', '24-26', '27-29', '30-1']
#     month_ranges = []
#     for i in range(10):  # Need 10 ranges for 10 stems
#         month_ranges.append(base_ranges[i % 10])
    
#     return {
#         "pillar": resolveHeavenlyStem(stem) + resolveEarthlyBranch(branch),
#         "elements": elements,
#         "heavenlyStems": stems,
#         "monthRanges": month_ranges
#     }

def get_wu_yun_cycle(year: int, month: int, day: int, hour: int) -> dict:
    """
    Calculate the Wu Yun (五運) cycles for month and hour pillars.
    
    Args:
        year: Year
        month: Month
        day: Day
        hour: Hour
        
    Returns:
        dict: Complete Wu Yun cycles for month and hour
    """
    current_date = datetime(year, month, day, hour)
    
    # Get the month and hour pillars
    month_stem, month_branch = calculate_month_heavenly_withSeason_for_baselife_time(year, month, day, hour)
    hour_stem, hour_branch = calculate_hour_heavenly(year, month, day, hour)
    
    # Calculate cycles for both month and hour
    month_cycle = calculate_wu_yun(month_stem, month_branch, current_date)
    hour_cycle = calculate_wu_yun(hour_stem, hour_branch, current_date, True)
    
    return {
        "monthCycle": month_cycle,
        "hourCycle": hour_cycle
    }

def get_complete_wuxi_data(year: int = None, month: int = None, day: int = None, hour: int = None, minutes: int = 0) -> dict:
    # Set current_date to today if no date provided
    current_timeline_date = datetime.now()
    if all(x is None for x in [year, month, day, hour]):
        year = current_date.year
        month = current_date.month
        day = current_date.day
        hour = current_date.hour
    """
    Combine LiuXi (六氣), base Bazi, and WuYun (五運) calculations into a complete dataset.
    
    Args:
        year: Year
        month: Month
        day: Day
        hour: Hour
        
    Returns:
        dict: Complete WuXi data structure
    """
    current_date = datetime(year, month, day, hour)
    
    # Get base Bazi data
    bazi_data = get_wuxi_ymdh_base(year, month, day, hour)
    
    # Create topGrid from Bazi data
    top_grid = {
        "time": bazi_data['時'],
        "day": bazi_data['日'],
        "dayHidden": bazi_data['-日'],
        "timeHidden": bazi_data['-時'],
        "month": bazi_data['月'],
        "year": bazi_data['年'],
        "yearHidden": bazi_data['-年'],
        "monthHidden": bazi_data['-月']
    }
    
    # Get current solar term info
    current_term_name, current_term_start, days_since_start = get_current_solar_term(current_date)
    solar_terms = get_solar_terms(year)
    days_to_next, next_solar_term_date_time, next_term_name = find_days_to_next_solar_term(current_date, solar_terms)
    
    # Get LiuXi cycles
    liu_xi_data = get_liu_xi_cycle(year, month, day, hour)
    year_cycle = liu_xi_data['yearCycle']
    
    # Convert solar date to lunar date using convert_Solar_to_Luna
    lunar_year, lunar_month, lunar_day = convert_Solar_to_Luna(year, month, day)
    
    # Determine middle earth based on 6 parts of year using lunar month
    if lunar_month == 11 or lunar_month == 12:
        year_middle_earth_index = 0  # First part (Lunar Nov-Dec)
    elif lunar_month == 1 or lunar_month == 2:
        year_middle_earth_index = 1  # Second part (Lunar Jan-Feb)
    elif lunar_month == 3 or lunar_month == 4:
        year_middle_earth_index = 2  # Third part (Lunar Mar-Apr)
    elif lunar_month == 5 or lunar_month == 6:
        year_middle_earth_index = 3  # Fourth part (Lunar May-Jun)
    elif lunar_month == 7 or lunar_month == 8:
        year_middle_earth_index = 4  # Fifth part (Lunar Jul-Aug)
    else:
        year_middle_earth_index = 5  # Sixth part (Lunar Sep-Oct)

    # Determine lower earth based on 12 parts of year
    if lunar_month == 12:
        year_lower_earth_index = 0  # December
    elif lunar_month == 1:
        year_lower_earth_index = 1  # January
    elif lunar_month == 2:
        year_lower_earth_index = 2  # February
    elif lunar_month == 3:
        year_lower_earth_index = 3  # March
    elif lunar_month == 4:
        year_lower_earth_index = 4  # April
    elif lunar_month == 5:
        year_lower_earth_index = 5  # May
    elif lunar_month == 6:
        year_lower_earth_index = 6  # June
    elif lunar_month == 7:
        year_lower_earth_index = 7  # July
    elif lunar_month == 8:
        year_lower_earth_index = 8  # August
    elif lunar_month == 9:
        year_lower_earth_index = 9  # September
    elif lunar_month == 10:
        year_lower_earth_index = 10  # October
    else:
        year_lower_earth_index = 11  # November
        
    # Determine upper heaven based on 2 parts of year
    is_first_half = lunar_month <= 6
    centerPillar = year_cycle['centerPillar']
    upper_heaven = year_cycle['upperHeavens'][0] if is_first_half else year_cycle['upperHeavens'][1]
    # Combine into year pillar
    year_pillar = upper_heaven + year_cycle['middleEarths'][year_middle_earth_index]


    # Get day cycle data
    day_cycle = liu_xi_data['dayCycle']
    
    # Determine middle earth based on 6 parts of day (4 hour blocks)
    if hour >= 23 or hour < 3:
        middle_earth_index = 0  # 23:00-03:00
    elif hour >= 3 and hour < 7:
        middle_earth_index = 1  # 03:00-07:00
    elif hour >= 7 and hour < 11:
        middle_earth_index = 2  # 07:00-11:00
    elif hour >= 11 and hour < 15:
        middle_earth_index = 3  # 11:00-15:00
    elif hour >= 15 and hour < 19:
        middle_earth_index = 4  # 15:00-19:00
    else:
        middle_earth_index = 5  # 19:00-23:00

    # Determine lower earth based on 12 parts of day (2 hour blocks)
    if hour >= 23 or hour < 1:
        day_lower_earth_index = 0  # 23:00-01:00
    elif hour >= 1 and hour < 3:
        day_lower_earth_index = 1  # 01:00-03:00
    elif hour >= 3 and hour < 5:
        day_lower_earth_index = 2  # 03:00-05:00
    elif hour >= 5 and hour < 7:
        day_lower_earth_index = 3  # 05:00-07:00
    elif hour >= 7 and hour < 9:
        day_lower_earth_index = 4  # 07:00-09:00
    elif hour >= 9 and hour < 11:
        day_lower_earth_index = 5  # 09:00-11:00
    elif hour >= 11 and hour < 13:
        day_lower_earth_index = 6  # 11:00-13:00
    elif hour >= 13 and hour < 15:
        day_lower_earth_index = 7  # 13:00-15:00
    elif hour >= 15 and hour < 17:
        day_lower_earth_index = 8  # 15:00-17:00
    elif hour >= 17 and hour < 19:
        day_lower_earth_index = 9  # 17:00-19:00
    elif hour >= 19 and hour < 21:
        day_lower_earth_index = 10  # 19:00-21:00
    else:
        day_lower_earth_index = 11  # 21:00-23:00
        
    # # Determine upper heaven based on 2 parts of day (12 hour blocks)
    is_first_half = hour < 12
    upper_heaven = day_cycle['upperHeavens'][0] if is_first_half else day_cycle['upperHeavens'][1]
    # Combine into day pillar
    day_pillar = upper_heaven + day_cycle['middleEarths'][middle_earth_index]
    
    # Get WuYun cycles
    wu_yun_data = get_wu_yun_cycle(year, month, day, hour)
    # Get major solar terms for month cycle calculation
    solar_terms = get_solar_terms(year)
    major_terms = solar_terms[1::2]  # Get every other term starting at index 1
    
    # Create datetime object from input parameters and make it timezone naive
    target_date = datetime(year, month, day, hour)
    if target_date.tzinfo:
        target_date = target_date.replace(tzinfo=None)
    
    # Convert major terms to naive datetimes for comparison
    major_terms = [term.replace(tzinfo=None) for term in major_terms]
    
    # Find the previous and current major term period
    previous_term_start = None
    current_term_start = None
    
    # First check if we're between two terms
    for i in range(len(major_terms)-1):
        if major_terms[i] <= target_date < major_terms[i+1]:
            # Check which term is closer
            days_to_prev = (target_date - major_terms[i]).total_seconds() / (24 * 3600)
            days_to_next = (major_terms[i+1] - target_date).total_seconds() / (24 * 3600)
            
            if days_to_prev <= days_to_next:
                previous_term_start = major_terms[i-1] if i > 0 else major_terms[-1]
                current_term_start = major_terms[i]
                logger.debug(f"Previous term starts at: {previous_term_start}")
                logger.debug(f"Current term starts at: {current_term_start}")
            else:
                previous_term_start = major_terms[i]
                current_term_start = major_terms[i+1]
                logger.debug(f"Previous term starts at: {previous_term_start}")
                logger.debug(f"Current term starts at: {current_term_start}")
            break
            
    # Handle edge case at end of year
    if not current_term_start:
        if target_date >= major_terms[-1]:
            previous_term_start = major_terms[-2]
            current_term_start = major_terms[-1]
            logger.debug(f"Previous term starts at: {previous_term_start}")
            logger.debug(f"Current term (year end) starts at: {current_term_start}")
        else:
            previous_term_start = major_terms[-1]
            current_term_start = major_terms[0]
            logger.debug(f"Previous term (last year) starts at: {previous_term_start}")
            logger.debug(f"Current term (year start) starts at: {current_term_start}")
            
    # Calculate days since start of current term
    days_elapsed = (target_date - previous_term_start).total_seconds() / (24 * 3600)
    
    # Calculate total days in this term period
    total_days = (current_term_start - previous_term_start).total_seconds() / (24 * 3600)
    logger.debug(f"Total days in term period: {total_days}")
    # Calculate month pillar index based on days elapsed
    # Each month cycle is approximately 30.44 days (365.25/12)
    days_per_month = total_days/10 # Divide term into 12 parts for months
    month_cycle_index = int(days_elapsed / days_per_month)
    logger.debug(f"Days per month: {days_per_month}")
    logger.debug(f"Initial month cycle index: {month_cycle_index}")
    
    # Get month cycle data and select pillar based on index
    month_cycle = wu_yun_data['monthCycle']
    logger.debug(f"Days elapsed: {days_elapsed}")
    logger.debug(f"Month cycle data: {month_cycle}")
    logger.debug(f"Month cycle index before mod: {month_cycle_index}")
    
    # Ensure index is within bounds of heavenly stems array (0-9)
    month_cycle_index = month_cycle_index % len(month_cycle['heavenlyStems'])
    logger.debug(f"Final month cycle index: {month_cycle_index}")
    
    month_pillar = month_cycle['heavenlyStems'][month_cycle_index]
    logger.debug(f"Selected month pillar: {month_pillar}")


    # Calculate hour pillar based on dividing 120 minutes into 10 parts
    minutes_per_part = 120 / 10  # Each part is 12 minutes
    
    # Convert hour to minutes since start of 2-hour block
    if hour >= 23 or hour < 1:
        minutes_from_start = (hour - 23) * 60 if hour >= 23 else (hour + 1) * 60  # 23:00-01:00
    elif hour >= 1 and hour < 3:
        minutes_from_start = (hour - 1) * 60  # 01:00-03:00 
    elif hour >= 3 and hour < 5:
        minutes_from_start = (hour - 3) * 60  # 03:00-05:00
    elif hour >= 5 and hour < 7:
        minutes_from_start = (hour - 5) * 60  # 05:00-07:00
    elif hour >= 7 and hour < 9:
        minutes_from_start = (hour - 7) * 60  # 07:00-09:00
    elif hour >= 9 and hour < 11:
        minutes_from_start = (hour - 9) * 60  # 09:00-11:00
    elif hour >= 11 and hour < 13:
        minutes_from_start = (hour - 11) * 60  # 11:00-13:00
    elif hour >= 13 and hour < 15:
        minutes_from_start = (hour - 13) * 60  # 13:00-15:00
    elif hour >= 15 and hour < 17:
        minutes_from_start = (hour - 15) * 60  # 15:00-17:00
    elif hour >= 17 and hour < 19:
        minutes_from_start = (hour - 17) * 60  # 17:00-19:00
    elif hour >= 19 and hour < 21:
        minutes_from_start = (hour - 19) * 60  # 19:00-21:00
    else:  # 21:00-23:00
        minutes_from_start = (hour - 21) * 60

    hour_cycle_index = int(minutes_from_start / minutes_per_part)
    
    # Get hour cycle data and select pillar based on index
    hour_cycle = wu_yun_data['hourCycle']
    hour_pillar = hour_cycle['heavenlyStems'][hour_cycle_index]
    
    # Add solar term info with datetime objects converted to strings
    solar_term_info = {
        "current": {
            "name": current_term_name,
            "date": current_term_start.strftime("%Y-%m-%d %H:%M:%S") if current_term_start else None,
            "daysSinceStart": round(days_since_start, 2),
            "daysToNext": round(days_to_next, 2)
        },
        "next": {
            "name": next_term_name if next_solar_term_date_time else None,
            "date": next_solar_term_date_time.strftime("%Y-%m-%d %H:%M:%S") if next_solar_term_date_time else None
        }
    }
    # Calculate indices for each cycle based on the pillars
    # Add indices to the cycles using the previously calculated indices
    year_cycle['index'] = year_lower_earth_index
    month_cycle['index'] = month_cycle_index
    day_cycle['index'] = day_lower_earth_index
    hour_cycle['index'] = hour_cycle_index
    top_grid['wuxipillar'] = {
        "year":  year_pillar,
        "month": month_pillar,
        "day": day_pillar,
        "hour": hour_pillar
    }
    # Calculate flip pillars using the dedicated method with male gender
    flip_pillars = calculate_flip_pillars(
        base_year=current_date.year,
        base_month=current_date.month, 
        base_day=current_date.day,
        base_hour=current_date.hour,
        gender="male",
        current_date=current_timeline_date,
        is_current=True
    )

    return {
        "topGrid": top_grid,
        "yearCycle": year_cycle,
        "monthCycle": month_cycle,
        "dayCycle": day_cycle,
        "hourCycle": hour_cycle,
        "solarTerm": solar_term_info,
        "flipPillars": flip_pillars
    }

def get_wuxi_current(year: int = None, month: int = None, day: int = None, hour: int = None) -> dict:
    """
    Get the heavenly branch pillars for year, month, day and hour with their hidden stems.
    This is a simplified version that only returns the wuxipillar data.

    Args:
        year: Year (defaults to current year if None)
        month: Month (defaults to current month if None) 
        day: Day (defaults to current day if None)
        hour: Hour (defaults to current hour if None)

    Returns:
        dict: Dictionary containing the pillars and their hidden stems
    """
    # Get the complete wuxi data
    wuxi_data = get_complete_wuxi_data(year, month, day, hour)
    
    # Extract the wuxipillar data
    wuxipillar = wuxi_data['topGrid']['wuxipillar']
    
    # Calculate hidden stems for each pillar using converter
    hour_stem = converter.chinese_to_enum(wuxipillar['hour'][0])
    hour_branch = converter.chinese_to_enum(wuxipillar['hour'][1])
    # hour_hidden = hidden_pillar(hour_stem, hour_branch, Direction.CLOCKWISE)

    day_stem = converter.chinese_to_enum(wuxipillar['day'][0]) 
    day_branch = converter.chinese_to_enum(wuxipillar['day'][1])
    # day_hidden = hidden_pillar(day_stem, day_branch, Direction.CLOCKWISE)

    month_stem = converter.chinese_to_enum(wuxipillar['month'][0])
    month_branch = converter.chinese_to_enum(wuxipillar['month'][1]) 
    # month_hidden = hidden_pillar(month_stem, month_branch, Direction.CLOCKWISE)

    year_stem = converter.chinese_to_enum(wuxipillar['year'][0])
    year_branch = converter.chinese_to_enum(wuxipillar['year'][1])
    # year_hidden = hidden_pillar(year_stem, year_branch, Direction.CLOCKWISE)
    return {
        "時運": wuxipillar['hour'],
        "日運": wuxipillar['day'],
        # "-日運": day_hidden,
        # "-時運": hour_hidden,
        "月運": wuxipillar['month'],
        "年運": wuxipillar['year'],
        # "-年運": year_hidden,
        # "-月運": month_hidden,
    }


def get_current_solar_term(target_date: datetime) -> tuple[str, datetime, float]:
    """
    Get the current solar term information based on the target date.
    
    Args:
        target_date (datetime): The target date to check
        
    Returns:
        tuple: (current_term_name, current_term_start_date, days_since_start)
            - current_term_name (str): Name of the current solar term
            - current_term_start_date (datetime): Start date of the current term
            - days_since_start (float): Number of days since the start of current term
    """
    solar_terms = get_solar_terms(target_date.year)
    
    # Convert target_date to naive datetime if it has timezone
    if target_date.tzinfo:
        target_date = target_date.replace(tzinfo=None)
    
    # Find the current term by checking which period we're in
    current_term_start = None
    current_term_name = None
    
    for i, term_date in enumerate(solar_terms):
        # Convert term_date to naive datetime for comparison
        naive_term_date = term_date.replace(tzinfo=None)
        if naive_term_date > target_date:
            if i > 0:
                current_term_start = solar_terms[i-1]
                # Get the term name using the start date
                adjusted_date = current_term_start.replace(tzinfo=None) - timedelta(days=1)
                current_term_name, _ = get_Luna_Month_With_Season(adjusted_date)
            break
    
    # If we haven't found a term, we might be in the last term of the previous year
    if not current_term_start:
        prev_year_terms = get_solar_terms(target_date.year - 1)
        current_term_start = prev_year_terms[-1]
        adjusted_date = current_term_start.replace(tzinfo=None) - timedelta(days=1)
        current_term_name, _ = get_Luna_Month_With_Season(adjusted_date)
    
    # Calculate days since the start of the current term
    # Convert both dates to naive for timedelta calculation
    naive_current_term_start = current_term_start.replace(tzinfo=None)
    days_since_start = (target_date - naive_current_term_start).total_seconds() / (24 * 3600)
    
    return current_term_name, current_term_start, days_since_start

def get_time_branch_part(hour: int, minute: int) -> tuple[EarthlyBranch, int, tuple[int, int]]:
    """
    Calculate which 時辰 (2-hour period) and which part (1-10) within that 時辰 a time falls into.
    Each 時辰 is 120 minutes, divided into 10 parts of 12 minutes each.
    
    Args:
        hour: Hour in 24-hour format (0-23)
        minute: Minute (0-59)
        
    Returns:
        tuple: (
            EarthlyBranch for the 時辰,
            int for the part number 1-10,
            tuple[int, int] for start time of current 時辰 (hour, minute)
        )
    """
    # Convert hour to 0-11 range for 12 two-hour periods
    adjusted_hour = hour % 24
    branch_index = (adjusted_hour + 1) // 2 % 12
    
    # Get the start of the current 時辰
    branch_start_hour = (adjusted_hour // 2) * 2
    
    # Calculate minutes since start of current 時辰
    minutes_since_branch_start = ((adjusted_hour - branch_start_hour) * 60) + minute
    
    # Calculate which part (1-10) we're in
    # Each part is 12 minutes (120/10)
    part_number = (minutes_since_branch_start // 12) + 1
    if part_number > 10:  # Handle edge case at branch boundary
        part_number = 10
        
    # Convert branch_index to EarthlyBranch
    # Note: Branch order starts with 子(ZI) at 23:00-01:00
    if branch_index == 0:
        branch = EarthlyBranch.ZI
        # Special case for ZI (23:00-01:00)
        branch_start_hour = 23 if adjusted_hour >= 23 else 23
    else:
        branch = EarthlyBranch(branch_index)
    
    return branch, part_number, (branch_start_hour, 0)

def calculate_flip_pillars(base_year: int, base_month: int, base_day: int, base_hour: int, 
                      gender: str, current_date: datetime = None, is_current: bool = False) -> dict:
    """
    Calculate the flipped pillars based on the given rules.
    
    Args:
        base_year: Birth year
        base_month: Birth month
        base_day: Birth day
        base_hour: Birth hour
        gender: 'male' or 'female'
        current_date: Current datetime for calculations. If None, uses base time.
        
    Returns:
        dict: Dictionary containing the flipped pillars
    """
    logger.debug(f" Starting flip pillar calculation for {base_year}-{base_month}-{base_day} {base_hour}")
    
    # Get base pillars first
    base_pillars = get_wuxi_ymdh_base(base_year, base_month, base_day, base_hour)
    base_date = datetime(base_year, base_month, base_day, base_hour)
    
    # Initialize flipped pillars with base values
    flipped_pillars = base_pillars.copy()
    
    # 1. Determine directions for each pillar
    year_stem = converter.chinese_to_enum(base_pillars['年'][0])
    is_yang_stem = year_stem.value % 2 == 1
    
    if is_current:
        logger.debug(f"Current time calculation - all pillars clockwise for {base_year}-{base_month}-{base_day} {base_hour}")
        hour_direction = Direction.CLOCKWISE
        day_direction = Direction.CLOCKWISE
        month_direction = Direction.CLOCKWISE
        year_direction = Direction.CLOCKWISE
    else:
        # For male: Yang stem -> anticlockwise, Yin stem -> clockwise
        # For female: opposite of male
        # For male with Yang stem or female with Yin stem -> clockwise
        clockwise = ((gender.lower() == 'male') == is_yang_stem)
        logger.debug(f"Clockwise: {clockwise} and gender: {gender} and is_yang_stem: {is_yang_stem}")
        
        # Hour and day pillars move opposite to month and year
        hour_direction = Direction.ANTICLOCKWISE if clockwise else Direction.CLOCKWISE
        day_direction = Direction.ANTICLOCKWISE if clockwise else Direction.CLOCKWISE
        month_direction = Direction.CLOCKWISE if clockwise else Direction.ANTICLOCKWISE  
        year_direction = Direction.CLOCKWISE if clockwise else Direction.ANTICLOCKWISE
        logger.debug(f" Directions for {base_year}-{base_month}-{base_day} {base_hour}: {hour_direction}, {day_direction}, {month_direction}, {year_direction}")
    # 2. Calculate DaYun and SiYun
    logger.debug("Calculating DaYun...")
    date_to_examine = datetime(base_year, base_month, base_day, base_hour)
    solar_terms = get_solar_terms(date_to_examine.year)
    days, next_term, term_name = find_days_to_next_solar_term(date_to_examine, solar_terms)
    dayun_sequence, starting_ages = calculate_dayun(gender, base_pillars['年'], base_pillars['月'], days)
    logger.debug(f"DaYun sequence: {dayun_sequence}")
    logger.debug(f"Starting ages: {starting_ages}")
    logger.debug(f"next term: {next_term}")

    # 3. Calculate SiYun
    logger.debug("Calculating SiYun...")
    siyun_sequence, _ = calculate_siyun(gender, base_pillars['時'], base_pillars['年'][0], base_date)
    logger.debug(f"SiYun sequence: {siyun_sequence}")
    
    # Get current solar term info
    current_term_name, current_term_start, days_since_start = get_current_solar_term(base_date)
    logger.debug(f"Current solar term: {current_term_name}")
    
    # Check if current time touches target branches
    # Create test year from current date components
    flip_year_test = datetime(current_date.year, base_month, base_day, base_hour).year
    # Check if current date is past the base date in the same year
    if (current_date.month > base_month or 
        (current_date.month == base_month and current_date.day > base_day)):
        # Check if we're in a sequence year
        for i, age in enumerate(starting_ages):
            sequence_year = int(base_year + age)
            if sequence_year == flip_year_test + 1:
                # Add one year since we've passed the base date
                flip_year_test += 1
                logger.debug(f"Adjusted flip year test to {flip_year_test} since current date is past base date")
                break

    # Find largest year in siyun sequence that has 子 or 亥 branch and store pillar
    max_siyun_target_year = -1
    siyun_target_pillar = None
    for i, pillar in enumerate(siyun_sequence):
        branch = pillar[1]
        if branch in ['子', '亥']:
            # Calculate year for this pillar using base year + starting age
            pillar_year = int(base_year  + starting_ages[i])
            if pillar_year > max_siyun_target_year:
                max_siyun_target_year = pillar_year
                siyun_target_pillar = pillar

    # Find largest year in dayun sequence that has 子 or 亥 branch and store pillar  
    max_dayun_target_year = -1
    dayun_target_pillar = None
    for i, pillar in enumerate(dayun_sequence):
        branch = pillar[1]
        if branch in ['子', '亥']:
            # Calculate year for this pillar using base year + starting age
            logger.info(f"DaYun index {i}: {dayun_sequence} {branch} Calculating pillar year {pillar_year} from base year {base_year} :{starting_ages} ")
            pillar_year = int(base_year + starting_ages[i])
            if pillar_year > max_dayun_target_year:
                max_dayun_target_year = pillar_year
                dayun_target_pillar = pillar

    # Set target flags based on comparisons
    touches_siyun_target = max_siyun_target_year >= 0 and flip_year_test >= max_siyun_target_year
    touches_dayun_target = max_dayun_target_year >= 0 and flip_year_test >= max_dayun_target_year
    logger.debug(f"Touches SiYun target: {touches_siyun_target} (test year {flip_year_test} vs target year {max_siyun_target_year})")
    logger.debug(f"Touches DaYun target: {touches_dayun_target} (test year {flip_year_test} vs target year {max_dayun_target_year})")

    # Log the pillar pairs for the test year
    logger.debug(f"Test year {flip_year_test} pillar pairs:")
    if siyun_target_pillar:
        logger.debug(f"SiYun pillar: {siyun_target_pillar[0]}{siyun_target_pillar[1]}")
    if dayun_target_pillar:
        logger.debug(f"DaYun pillar: {dayun_target_pillar[0]}{dayun_target_pillar[1]}")

    # Find the closest sequence number that flip_year_test has just passed
    logger.debug(f"Finding closest sequence number for flip_year_test: {flip_year_test}")
    logger.debug(f"Max SiYun target year: {max_siyun_target_year}")
    logger.debug(f"Max DaYun target year: {max_dayun_target_year}")
    
    # Find which sequence index we're currently at based on flip_year_test
    temp_index = 0
    target_index = 0
    siyun_last_target = False
    dayun_last_target = False

    # Since both sequences use same years, just check one sequence
    for i, pillar_year in enumerate([int(base_year + age) for age in starting_ages]):
        if pillar_year <= flip_year_test:
            temp_index = i
            # Check if this index hits target branch in either sequence
            if is_yang_stem:
                # For yang stem, siyun looks for 亥, dayun looks for 子
                if siyun_sequence[i][1] == '亥':
                    target_index = i
                    siyun_last_target = True
                if dayun_sequence[i][1] == '子':
                    target_index = i
                    dayun_last_target = True
            else:
                # For yin stem, siyun looks for 子, dayun looks for 亥
                if siyun_sequence[i][1] == '子':
                    target_index = i
                    siyun_last_target = True
                if dayun_sequence[i][1] == '亥':
                    target_index = i
                    dayun_last_target = True
            logger.debug(f"At index {i}, year {pillar_year}: SiYun hit: {siyun_last_target}, DaYun hit: {dayun_last_target}")
        else:
            break

    # Use whichever sequence had the most recent target hit
    if siyun_last_target and not dayun_last_target:
        logger.debug(f"Using SiYun sequence - last target at index {target_index}")
    elif dayun_last_target and not siyun_last_target:
        logger.debug(f"Using DaYun sequence - last target at index {target_index}")
    else:
        logger.debug(f"Both sequences hit target at index {target_index}")

    if (touches_dayun_target or touches_siyun_target):
        # Use same index to get corresponding pillar from siyun sequence
        flipped_pillars['月'] = dayun_sequence[target_index]
        flipped_pillars['時'] = siyun_sequence[target_index]
        logger.debug(f"月: {dayun_sequence[target_index]}")
        logger.debug(f"時: {siyun_sequence[target_index]}")


    # Apply the rules
    if touches_siyun_target:
        # Move hour pillar based on SiYun calculation
        logger.debug("Moving hour pillar based on SiYun")
        # # Find the last pillar in sequence that has the target branch based on direction
        # target_branch = '子' if hour_direction == Direction.CLOCKWISE else '亥'
        # for pillar in reversed(siyun_sequence):
        #     branch = pillar[1]
        #     if branch == target_branch:
        #         flipped_pillars['時'] = pillar
        #         logger.debug(f"Flipped hour pillar: {pillar}")
        #         break
        # flipped_pillars['時'] = siyun_target_pillar
        # Move day pillar by one step
        logger.debug("Moving day pillar by one step")
        current_index = heavenly_earthly_dict[base_pillars['日']]
        if day_direction == Direction.CLOCKWISE:
            new_index = (current_index % 60) + 1
        else:
            new_index = current_index - 1 if current_index > 1 else 60
            
        # Find the pillar with the new index
        for pillar, idx in heavenly_earthly_dict.items():
            if idx == new_index:
                flipped_pillars['日'] = pillar
                logger.debug(f"Flipped day pillar: {pillar}")
                break

    
    if touches_dayun_target:
        # target_branch = '子' if month_direction == Direction.CLOCKWISE else '亥'
        # for pillar in reversed(dayun_sequence):
        #     branch = pillar[1]
        #     if branch == target_branch:
        #         flipped_pillars['月'] = pillar
        #         logger.debug(f"Flipped month pillar: {pillar}")
        #         break
        # flipped_pillars['月'] = dayun_target_pillar
        # Move year pillar by one step
        logger.debug("Moving year pillar by one step")
        current_index = heavenly_earthly_dict[base_pillars['年']]
        logger.debug(f"Flipped year index: {current_index}")


        if year_direction == Direction.CLOCKWISE:
            new_index = (current_index % 60) + 1
        else:
            new_index = current_index - 1 if current_index > 1 else 60
            
        # Find the pillar with the new index
        for pillar, idx in heavenly_earthly_dict.items():
            if idx == new_index:
                flipped_pillars['年'] = pillar
                logger.debug(f"Flipped year pillar: {pillar}")
                break
        

    

    # Calculate hidden stems for flipped pillars
    for pillar_key in ['時', '日', '月', '年']:
        if pillar_key in flipped_pillars:
            # Convert Chinese characters to enums
            stem = converter.chinese_to_enum(flipped_pillars[pillar_key][0])
            branch = converter.chinese_to_enum(flipped_pillars[pillar_key][1])
            
            # Calculate hidden stems using same direction as main pillars
            # TODO: need to check if this is correct with mail or female, cannot hardcode. 
            # direction = Direction.CLOCKWISE
            if pillar_key == '時' or pillar_key == '日':
                direction = hour_direction if pillar_key == '時' else day_direction
            else:
                direction = month_direction if pillar_key == '月' else year_direction
                
            # Add hidden stems to flipped pillars
            flipped_pillars[f'-{pillar_key}'] = hidden_pillar(stem, branch, direction)
            logger.debug(f"Added hidden stems for {pillar_key}: {flipped_pillars[f'-{pillar_key}']}")
    return flipped_pillars

def calculate_siyun(gender: str, hour_pillar: str, year_stem: str, base_date: datetime) -> tuple[list, list]:
    """
    Calculate 時運 sequence and starting ages
    
    Args:
        gender: 'male' or 'female'
        hour_pillar: Hour pillar in Chinese characters (e.g., '甲子')
        year_stem: Year stem in Chinese character (e.g., '甲')
        base_date: Base datetime for age calculation
        
    Returns:
        tuple: (list of SiYun pillars, list of starting ages)
    """
    logger.debug(f"Calculating SiYun for gender: {gender}, hour pillar: {hour_pillar}, year stem: {year_stem}")
    
    # Convert hour pillar to enums
    hour_stem = converter.chinese_to_enum(hour_pillar[0])
    hour_branch = converter.chinese_to_enum(hour_pillar[1])
    
    # Determine counting direction based on gender and year stem
    year_stem_enum = converter.chinese_to_enum(year_stem)
    is_yang_stem = year_stem_enum.value % 2 == 1
    
    # For male: Yang stem -> anticlockwise, Yin stem -> clockwise
    # For female: opposite of male
    clockwise = (gender.lower() == 'male') != is_yang_stem
    
    # Generate sequence
    sequence = []
    current_stem = hour_stem
    current_branch = hour_branch
    
    for _ in range(8):  # Generate 8 pillars
        # Move to next pillar using heavenly_earthly_dict
        current_pillar = resolveHeavenlyStem(current_stem.value) + resolveEarthlyBranch(current_branch.value)
        current_index = heavenly_earthly_dict[current_pillar]
        
        if clockwise:
            new_index = (current_index % 60) + 1
        else:
            new_index = current_index - 1 if current_index > 1 else 60
            
        # Find the pillar with the new index
        for pillar, idx in heavenly_earthly_dict.items():
            if idx == new_index:
                current_stem = converter.chinese_to_enum(pillar[0])
                current_branch = converter.chinese_to_enum(pillar[1])
                break
        sequence.append(resolveHeavenlyStem(current_stem.value) + resolveEarthlyBranch(current_branch.value))
    
    # Calculate starting ages (similar to DaYun)
    starting_ages = []
    solar_terms = get_solar_terms(base_date.year)
    days, next_term, term_name = find_days_to_next_solar_term(base_date, solar_terms)
    base_age = days
    for _ in range(8):
        if base_age >= 1:
            starting_ages.append(base_age)
        base_age += 10
    
    return sequence, starting_ages

def print_siyun(gender: str, hour_pillar: str, year_stem: str, date_to_examine: datetime):
    """
    Print 時運 calculation results
    
    Args:
        gender: 'male' or 'female'
        hour_pillar: Hour pillar in Chinese characters
        year_stem: Year stem in Chinese character
        date_to_examine: Current datetime for age calculation
    """
    # Calculate 時運
    siyun_sequence, starting_ages = calculate_siyun(gender, hour_pillar, year_stem, date_to_examine)
    
    # Print results
    print("\n時運 Calculation Results:")
    print("-" * 40)
    for i, ((stem, branch), age) in enumerate(zip(siyun_sequence, starting_ages)):
        year = date_to_examine.year + int(age)
        print(f"時運 {i+1}: {stem}{branch} "
              f"({stem}-{branch}) Starting age: {age} Year: {year}")

def json_siyun(gender: str, hour_pillar: str, year_stem: str, date_to_examine: datetime) -> list:
    """
    Return 時運 calculation results in JSON format
    
    Args:
        gender: 'male' or 'female'
        hour_pillar: Hour pillar in Chinese characters
        year_stem: Year stem in Chinese character
        date_to_examine: Current datetime for age calculation
        
    Returns:
        list: List of dictionaries containing SiYun information
    """
    # Calculate 時運
    siyun_sequence, starting_ages = calculate_siyun(gender, hour_pillar, year_stem, date_to_examine)
    
    # Create result list
    result = []
    for (stem, branch), age in zip(siyun_sequence, starting_ages):
        result.append({
            "stem": stem,
            "branch": branch,
            "chinese": f"{stem}{branch}",
            "starting_age": round(age, 1)
        })
    
    return result