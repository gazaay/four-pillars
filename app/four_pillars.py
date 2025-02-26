from datetime import datetime
from enum import Enum

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

class EarthlyBranch(Enum):
    ZI = 1    # 子
    CHOU = 2  # 丑
    YIN = 3   # 寅
    MAO = 4   # 卯
    CHEN = 5  # 辰
    SI = 6    # 巳
    WU = 7    # 午
    WEI = 8   # 未
    SHEN = 9  # 申
    YOU = 10  # 酉
    XU = 11   # 戌
    HAI = 0   # 亥

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

def get_ymdh_base(year: int, month: int, day: int, hour: int) -> dict:
    """
    Calculate the basic four pillars (YMDH) for a given date and time.
    Returns in Chinese characters format.
    """
    # Calculate pillars (using previous logic)
    year_stem = HeavenlyStem((year - 3) % 10)
    year_branch = EarthlyBranch((year - 3) % 12)
    
    # month_stem = HeavenlyStem(((year % 10 + 2) * 2 + month) % 10)
    # month_branch = EarthlyBranch((month + 2) % 12)
    month_stem, month_branch = calculate_month_stem_branch(year, month, day, hour)
    day_stem, day_branch = calculate_day_pillar(year, month, day)
    
    hour_stem = HeavenlyStem(((day_stem.value * 2 + (hour + 1) // 2) - 2) % 10)
    hour_branch = EarthlyBranch(((hour + 1) // 2) % 12)
    
    # Convert to Chinese characters
    return {
        "時": HeavenlyStemCN[hour_stem.name].value + EarthlyBranchCN[hour_branch.name].value,
        "日": HeavenlyStemCN[day_stem.name].value + EarthlyBranchCN[day_branch.name].value,
        "月": HeavenlyStemCN[month_stem.name].value + EarthlyBranchCN[month_branch.name].value,
        "年": HeavenlyStemCN[year_stem.name].value + EarthlyBranchCN[year_branch.name].value,
    }

def calculate_day_pillar(year: int, month: int, day: int) -> tuple:
    """
    Calculate the day pillar using the day calculation formula.
    """
    if year >= 2000:
        intermediate = ((year % 100 + 100) * 5 + (year % 100 + 100) // 4 + 9 + day)
    else:
        intermediate = ((year % 100) * 5 + (year % 100) // 4 + 9 + day)
    
    # Month adjustments
    if month % 2 == 0:
        intermediate += 30
    
    # Adjustment factors for each month
    adjustment_factors = [0, 1, 2, 0, 1, 1, 2, 2, 3, 4, 4, 5, 5]
    intermediate += adjustment_factors[month]
    
    # Leap year adjustment
    if (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0)):
        if month in [1, 2]:
            intermediate -= 1
            
    stem = HeavenlyStem(intermediate % 10)
    branch = EarthlyBranch(intermediate % 12)
    
    return stem, branch 

def calculate_month_stem_branch(year: int, month: int, day: int, hour: int) -> tuple:
    """
    Calculate the month's heavenly stem and earthly branch based on solar terms.
    
    Args:
        year: Year
        month: Month (1-12)
        day: Day
        hour: Hour (0-23)
    
    Returns:
        Tuple[int, int]: (heavenly_stem, earthly_branch)
    """
    # Get solar term and index
    solar_term, solar_month_index = get_solar_term_and_index(datetime(year, month, day, hour, 15))
    
    # Convert solar term to index using solarterms dict
    solar_month_index = solarterms[solar_term]
    
    # Adjust year based on solar term
    if solar_term == "LiChun":
        year = get_lichun_year(year)
    else:
        year, _, _ = convert_lunar_date(year, month, day)
    
    # Calculate solar month index and quotient
    solar_month_index = solar_month_index + 1
    quotient_solar = solar_month_index // 2
    month = quotient_solar
    
    # Calculate heavenly stem
    month_heavenly_stem = ((year % 10 + 2) * 2 + month) % 10
    
    # Calculate earthly branch
    earthly_branch = (month + 2) % 12
    
    return month_heavenly_stem, earthly_branch



def get_solar_term_and_index(date: datetime) -> tuple:
    """
    Get the solar term and index for a given date.
    
    Args:
        date: Datetime object
        
    Returns:
        Tuple[str, int]: (solar_term_name, index)
    """
    # Get list of solar terms for the year
    solar_terms = get_solar_terms(date.year)
    
    # Find the current solar term
    for i, term_date in enumerate(solar_terms):
        if date < term_date:
            return solar_terms_list[i], i + 1
            
    return solar_terms_list[-1], len(solar_terms)

def get_lichun_year(year: int) -> int:
    """Get year based on LiChun solar term"""
    lichun_date = solarterm.LiChun(year)
    return lichun_date.year

def convert_lunar_date(year: int, month: int, day: int) -> tuple:
    """Convert solar date to lunar date"""
    solar = Solar(year, month, day)
    lunar = Converter.Solar2Lunar(solar)
    return lunar.year, lunar.month, lunar.day


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