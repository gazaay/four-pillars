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

def get_heavenly_stem_earthly_branch(year, month: int):
    if month == 0:
        offset = 1
    else: 
        offset = 0
    print(f"Month is {month} Offset is {offset}")
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
    heavenly_stem_index = (year - 3) % 10
    print(f"Heavenly Index is {heavenly_stem_index}")
    heavenly_stem = HeavenlyStem(heavenly_stem_index)
    print(f"Heavenly Stem {heavenly_stem.name}")
    key_month_heavenly_stem = (heavenly_stem.value + heavenly_stem.value + 1) % 10
    print(f"Key Month Heavenly Stem {key_month_heavenly_stem}")
    month_heavenly_stem = (key_month_heavenly_stem + month - 1 ) %10
    print(f"Month Heavenly Stem {month_heavenly_stem}")
    earthly_branch_stem = EarthlyBranch((month + 2)%12).value %12
    print(f"Month Earthly Branch Stem {earthly_branch_stem}")

    return HeavenlyStem(month_heavenly_stem), EarthlyBranch(earthly_branch_stem)

def calculate_day_heavenly(year, month, day):

    #Chinese calendar is solar calendar
    year, month, day = convert_Luna_to_Solar(year, month, day)

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


def convert_Luna_to_Solar(year, month, day):
    lunar = Lunar(year, month, day)
    print(f"This is Lunar year - {lunar}")
    solar = Converter.Solar2Lunar(lunar)
    print(f"This is Solar year - {solar}")
    return lunar.to_date().year, lunar.to_date().month, lunar.to_date().day

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
