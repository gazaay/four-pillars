from enum import Enum
from typing import Tuple, Dict, Any
import json

class Hexagram(Enum):
    # Format: enum_name = (number, symbol, chinese_name, (upper_trigram, lower_trigram))
    QIAN = (1, "䷀", "乾", (1, 1))
    KUN = (2, "䷁", "坤", (8, 8))
    ZHUN = (3, "䷂", "屯", (6, 4))
    MENG = (4, "䷃", "蒙", (7, 6))
    XU = (5, "䷄", "需", (6, 1))
    SONG = (6, "䷅", "訟", (1, 6))
    SHI = (7, "䷆", "師", (8, 6))
    BI = (8, "䷇", "比", (8, 6))
    XIAO_CHU = (9, "䷈", "小畜", (5, 1))
    LV = (10, "䷉", "履", (1, 2))
    TAI = (11, "䷊", "泰", (8, 1))
    PI = (12, "䷋", "否", (1, 8))
    TONG_REN = (13, "䷌", "同人", (1, 3))
    DA_YOU = (14, "䷍", "大有", (3, 1))
    QIAN_HEX = (15, "䷎", "謙", (8, 7))
    YU = (16, "䷏", "豫", (4, 8))
    SUI = (17, "䷐", "隨", (2, 4))
    GU = (18, "䷑", "蠱", (7, 5))  # (7,5) appears here
    LIN = (19, "䷒", "臨", (8, 2))
    GUAN = (20, "䷓", "觀", (5, 8))
    SHI_KE = (21, "䷔", "噬嗑", (3, 4))
    BI_HEX = (22, "䷕", "賁", (7, 3))
    BO = (23, "䷖", "剝", (7, 8))
    FU = (24, "䷗", "復", (8, 4))
    WU_WANG = (25, "䷘", "无妄", (1, 4))
    DA_CHU = (26, "䷙", "大畜", (7, 1))
    YI = (27, "䷚", "頤", (7, 4))
    DA_GUO = (28, "䷛", "大過", (2, 5))
    KAN = (29, "䷜", "坎", (6, 6))
    LI = (30, "䷝", "離", (3, 3))
    XIAN = (31, "䷞", "咸", (2, 7))
    HENG = (32, "䷟", "恒", (4, 5))
    DUN = (33, "䷠", "遯", (1, 7))
    DA_ZHUANG = (34, "䷡", "大壯", (4, 1))
    JIN = (35, "䷢", "晉", (3, 8))
    MING_YI = (36, "䷣", "明夷", (8, 3))
    JIA_REN = (37, "䷤", "家人", (5, 3))
    KUI = (38, "䷥", "睽", (3, 2))
    JIAN = (39, "䷦", "蹇", (6, 7))
    JIE = (40, "䷧", "解", (4, 6))
    SUN = (41, "䷨", "損", (7, 2))
    YI_HEX = (42, "䷩", "益", (5, 4))
    GUAI = (43, "䷪", "夬", (2, 1))
    GOU = (44, "䷫", "姤", (1, 5))
    CUI = (45, "䷬", "萃", (2, 8))
    SHENG = (46, "䷭", "升", (8, 5))
    KUN_HEX = (47, "䷮", "困", (2, 6))
    JING = (48, "䷯", "井", (6, 5))
    GE = (49, "䷰", "革", (2, 3))
    DING = (50, "䷱", "鼎", (3, 5))
    ZHEN = (51, "䷲", "震", (4, 4))
    GEN = (52, "䷳", "艮", (7, 7))
    JIAN_HEX = (53, "䷴", "漸", (5, 7))
    GUI_MEI = (54, "䷵", "歸妹", (4, 2))
    FENG = (55, "䷶", "豐", (4, 3))
    LV_HEX = (56, "䷷", "旅", (3, 7))
    XUN = (57, "䷸", "巽", (5, 5))
    DUI = (58, "䷹", "兌", (2, 2))
    HUAN = (59, "䷺", "渙", (5, 6))
    JIE_HEX = (60, "䷻", "節", (6, 2))
    ZHONG_FU = (61, "䷼", "中孚", (5, 2))
    XIAO_GUO = (62, "䷽", "小過", (4, 7))
    JI_JI = (63, "䷾", "既濟", (6, 3))
    WEI_JI = (64, "䷿", "未濟", (3, 6))

    def __init__(self, number, symbol, chinese_name, trigrams):
        self.number = number
        self.symbol = symbol
        self.chinese_name = chinese_name
        self.trigrams = trigrams  # (upper_trigram, lower_trigram)

# Dictionary mapping trigram tuples to hexagrams
TRIGRAM_TO_HEXAGRAM: Dict[Tuple[int, int], Hexagram] = {}

# Initialize the mapping
for hexagram in Hexagram:
    TRIGRAM_TO_HEXAGRAM[hexagram.trigrams] = hexagram

# Trigram names for reference
TRIGRAM_NAMES = {
    1: "天",
    2: "澤",
    3: "火",
    4: "雷",
    5: "風",
    6: "水",
    7: "山",
    8: "地"
}

def reduce_to_trigram_number(number: int) -> int:
    """Reduce a number to a value between 1 and 8 (inclusive)"""
    while number > 8:
        number -= 8
    return number

def phone_to_hexagram(phone_number: str) -> Hexagram:
    """
    Convert a Hong Kong phone number (8 digits) to a hexagram.
    
    Args:
        phone_number: An 8-digit HK phone number (can include spaces)
    
    Returns:
        The corresponding hexagram
    """
    # Remove any spaces or non-digit characters
    digits = ''.join(filter(str.isdigit, phone_number))
    
    if len(digits) != 8:
        raise ValueError("Hong Kong phone numbers must be 8 digits")
    
    # Split into two parts: first 4 digits and last 4 digits
    first_part = digits[:4]
    second_part = digits[4:]
    
    # Calculate the sum of the first part and reduce it to a number between 1 and 8
    first_sum = sum(int(digit) for digit in first_part)
    first_trigram = reduce_to_trigram_number(first_sum)
    
    # Calculate the sum of the second part and reduce it to a number between 1 and 8
    second_sum = sum(int(digit) for digit in second_part)
    second_trigram = reduce_to_trigram_number(second_sum)
    
    # Get the hexagram corresponding to these trigrams
    hexagram_tuple = (first_trigram, second_trigram)
    if hexagram_tuple in TRIGRAM_TO_HEXAGRAM:
        hexagram = TRIGRAM_TO_HEXAGRAM[hexagram_tuple]
        return hexagram
    else:
        raise ValueError(f"No hexagram found for trigram combination {hexagram_tuple}")

def format_hexagram(hexagram: Hexagram) -> str:
    """Format the hexagram for display"""
    upper_trigram = TRIGRAM_NAMES[hexagram.trigrams[0]]
    lower_trigram = TRIGRAM_NAMES[hexagram.trigrams[1]]
    return f"{hexagram.number}.{hexagram.symbol} {hexagram.chinese_name} ({upper_trigram}{hexagram.trigrams[0]},{lower_trigram}{hexagram.trigrams[1]})"

def phone_to_hexagram_json(phone_number: str) -> str:
    """
    Convert a Hong Kong phone number to a Yi Jing hexagram and return the result as JSON.
    
    Args:
        phone_number: An 8-digit Hong Kong phone number
        
    Returns:
        JSON string containing the hexagram information
    """
    try:
        hexagram = phone_to_hexagram(phone_number)
        
        # Get the trigram names
        upper_trigram_num = hexagram.trigrams[0]
        lower_trigram_num = hexagram.trigrams[1]
        upper_trigram_name = TRIGRAM_NAMES[upper_trigram_num]
        lower_trigram_name = TRIGRAM_NAMES[lower_trigram_num]
        
        # Create a dictionary with the hexagram information
        result = {
            "success": True,
            "phone_number": phone_number,
            "hexagram": {
                "number": hexagram.number,
                "symbol": hexagram.symbol,
                "name": hexagram.chinese_name,
                "upper_trigram": {
                    "number": upper_trigram_num,
                    "name": upper_trigram_name
                },
                "lower_trigram": {
                    "number": lower_trigram_num,
                    "name": lower_trigram_name
                },
                "formatted": format_hexagram(hexagram)
            }
        }
        
        # Convert to JSON
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except ValueError as e:
        error_result = {
            "success": False,
            "phone_number": phone_number,
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2) 