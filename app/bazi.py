from enum import Enum
import datetime
from lunarcalendar import Converter, Solar, Lunar, DateNotExist

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

def SixtyStem(index: int) :

    index = index %60

    if index is 0:
        index = 60

    # Reverse the dictionary
    index_to_combination = {value: key for key, value in heavenly_earthly_dict.items()}

    # Now you can use an index to retrieve the corresponding combination
    combination = index_to_combination.get(index)

    if combination is not None:
        print("Combination:", combination)
    else:
        print("Index not found.")
    
    return combination

def getSixtyStemIndex(stem):
    return heavenly_earthly_dict[stem]

def calculate_year_heavenly(year, month: int):
    if month == 0:
        offset = 1
    else: 
        offset = 0

     #Chinese calendar is solar calendar
    # print(f"Year Pillar: Year: {year} month: {month} Offset is {offset}")
    year, month, day = convert_Solar_to_Luna(year, month, 1)
    heavenly_stem_index = (year - 3 - offset) % 10
    earthly_branch_index = (year - 3) % 12
    heavenly_stem = HeavenlyStem(heavenly_stem_index)
    print(f"Year Earthly Index {earthly_branch_index}")
    earthly_branch = EarthlyBranch(earthly_branch_index )
    print(f"Year Earthly Branch {earthly_branch.value}")
    return heavenly_stem.value, earthly_branch.value

def calculate_month_heavenly(year, month: int):
    # if month == 0:
    #     offset = 1
    # else: 
    #     offset = 0
    # print(f"Month is {month} Offset is {offset}")

    #Chinese calendar is solar calendar
    year, month, day = convert_Solar_to_Luna(year, month, 1)


    heavenly_stem_index = (year - 3) % 10
    print(f"Heavenly Index is {heavenly_stem_index} and team is { HeavenlyStem(heavenly_stem_index)}")
    year_heavenly_stem = HeavenlyStem(heavenly_stem_index)
    print(f"Heavenly Stem {year_heavenly_stem.name}")
    month_heavenly_stem = ((year % 10 + 2 )  * 2 + month) %10

    # month_heavenly_stem = (year_heavenly_stem.value + year_heavenly_stem.value + 1) % 10
    # month_heavenly_stem = (month_heavenly_stem + month - 1 ) % 10
    print(f"Month Heavenly Stem {month_heavenly_stem} ")
    earthly_branch_stem = EarthlyBranch((month + 2) %12).value 
    print(f"Month Earthly Branch Stem {earthly_branch_stem}")

    return HeavenlyStem(month_heavenly_stem), EarthlyBranch(earthly_branch_stem)

def calculate_heavenly_earthly(year, month, day):

    #Chinese calendar is solar calendar
    year, month, day = convert_Solar_to_Luna(year, month, day)

    # Calculate the intermediate value
    intermediate_value = (year % 100) * 5 + + (year // 100) + (year % 100) // 4 + 9 + day

    print(f"Intermediate value {intermediate_value %60}")
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
    adjustment_factors = [0, 1, 2, 0, 1, 1, 2, 3, 4, 4, 5, 5]
    adjustment_factor = adjustment_factors[month - 1]

    # Adjust for leap year
    if (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0)):
        if (month == 1) or (month == 2):
            adjustment_factor -= 1

    # Apply the adjustment factor
    intermediate_value += adjustment_factor

    print(f"Intermediate value {intermediate_value %60}")
    # Calculate Heavenly Stems and Earthly Branches
    heavenly_stem_index = (intermediate_value % 60) % 10
    earthly_branch_index = (intermediate_value % 60) % 12
    print(f"Intermediate value {intermediate_value %60}")

    # Define Heavenly Stems and Earthly Branches
    heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    heavenly_stem = heavenly_stems[heavenly_stem_index]
    earthly_branch = earthly_branches[earthly_branch_index]

    return heavenly_stem + earthly_branch


def calculate_day_heavenly(year, month, day):

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
    print("Earthly Branch Index is ", earthly_branch_index)
    return HeavenlyStem(heavenly_stem_index), EarthlyBranch(earthly_branch_index)


def convert_Solar_to_Luna(year, month, day):
    solar = Solar(year, month, day)
    # print(f":Luna_to_Solar: This is Solar year - {solar}")
    lunar = Converter.Solar2Lunar(solar)
    # print(f":Luna_to_Solar: This is Lunar year - {lunar.year}")
    print(f"Sending results {lunar.year} and month {lunar.month} and day {lunar.day}")
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
