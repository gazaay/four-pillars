from datetime import datetime, timedelta
from app import bazi
from app import chengseng
import logging
from dateutil.relativedelta import relativedelta
import pytz

# Configure logging settings
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   filename='app.log',
                   filemode='w')

logger = logging.getLogger(__name__)

def format_bazi_output_3(data_dict):
    # Define the groups - now including negative entries
    basic_keys = ['時', '日', '-日', '-時', '月', '年', '-年', '-月']
    he_keys = ['合時', '合日', '-合日', '-合時', '合月', '合年', '-合年', '-合月']
    hai_keys = ['害時', '害日', '-害日', '-害時', '害月', '害年', '-害年', '-害月']
    po_keys = ['破時', '破日', '-破日', '-破時', '破月', '破年', '-破年', '-破月']

    def format_group(keys, values):
        first_row = []
        second_row = []
        for key in keys:
            if key in values:
                if key.startswith('-'):
                    first_row.append("  ")
                    second_row.append("  ")
                else:
                    if len(key) == 1:
                        first_row.append(key)
                        second_row.append(" ")
                    else:
                        first_row.append(key[0])
                        second_row.append(key[-1])

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

    groups = [
        (basic_keys, "Basic Pillars"),
        (he_keys, "He (合) Group"),
        (hai_keys, "Hai (害) Group"),
        (po_keys, "Po (破) Group")
    ]

    for keys, group_name in groups:
        rows = format_group(keys, data_dict)
        if any(row.strip() for row in rows):
            for row in rows:
                print(row)
            print()

def get_pillar_from_dict(data_dict, pillar_type):
    if pillar_type in data_dict:
        return data_dict[pillar_type]
    return None

def generate_bazi_analysis(input_date: datetime):
    print(f"##### {input_date.year}/{input_date.month}/{input_date.day} {input_date.hour}:00 #####")
    
    # Get and display current bazi
    bazi_data = bazi.get_ymdh_current(input_date.year, input_date.month, input_date.day, input_date.hour)
    print("Current Bazi:")
    format_bazi_output_3(bazi_data)
    
    # Get and display base bazi
    bazi_data = bazi.get_ymdh_base(input_date.year, input_date.month, input_date.day, input_date.hour)
    print("Base Bazi:")
    format_bazi_output_3(bazi_data)
    
    # Get pillars and print DaiYun
    year_pillar = get_pillar_from_dict(bazi_data, '年')
    month_pillar = get_pillar_from_dict(bazi_data, '月')
    bazi.print_daiYun("male", year_pillar, month_pillar, input_date)

def print_liu_xi_cycle(wu_xi_data):
    """
    Print WuXi cycles in a formatted layout.
    
    Args:
        wu_xi_data: Dictionary containing yearCycle and dayCycle data
    """
    def print_cycle(cycle_data, title):
        print(f"\n{title}")
        print("=" * 50)
        
        # Print center pillar and upper heavens
        heaven = cycle_data['centerPillar']['heaven']
        earth = cycle_data['centerPillar']['earth']
        upper_heavens = [stem.value if hasattr(stem, 'value') else stem for stem in cycle_data['upperHeavens']]
        
        print(f"Center Pillar: {heaven}{earth}")
        print(f"Upper Heavens: {' '.join(upper_heavens)}")
        
        # Print middle earths
        middle_earths = [earth.value if hasattr(earth, 'value') else earth for earth in cycle_data['middleEarths']]
        print(f"Middle Earths: {' '.join(middle_earths)}")
        
        # Print lower earths with months
        lower_earths = [earth.value if hasattr(earth, 'value') else earth for earth in cycle_data['lowerEarths']]
        chinese_months = cycle_data['chineseMonths']
        western_months = cycle_data['westernMonths']
        
        print("\nDetailed Monthly Layout:")
        print("-" * 50)
        print("Earth:   " + " ".join(f"{e:2}" for e in lower_earths))
        print("Chinese: " + " ".join(f"{m:2}" for m in chinese_months))
        print("Western: " + " ".join(f"{m:2}" for m in western_months))

    # Print both cycles
    print_cycle(wu_xi_data['yearCycle'], "Year Cycle (年氣)")
    print_cycle(wu_xi_data['dayCycle'], "Day Cycle (日氣)")

def print_wu_yun_cycle(wu_yun_data):
    """
    Print Wu Yun cycle in a formatted layout.
    """
    print("=" * 50)
    
    # Print pillar
    print(f"Center Pillar: {wu_yun_data['pillar']}")
    
    # Print elements with their emojis
    print("\nElements:")
    elements = [f"{e['name']}{e['emoji']}" for e in wu_yun_data['elements']]
    print(" | ".join(elements))
    
    # Print stems and month ranges in columns
    print("\nStems and Months:")
    print("-" * 50)
    stems = wu_yun_data['heavenlyStems']
    ranges = wu_yun_data['monthRanges']
    
    # Print in groups of two for better readability
    for i in range(0, len(stems), 2):
        stem_pair = f"{stems[i]}-{stems[i+1]}"
        month_range = ranges[i:i+2]
        print(f"{stem_pair:<8} {' '.join(month_range)}")

def print_complete_wu_yun_cycles(wu_yun_data):
    """
    Print both month and hour Wu Yun cycles.
    """
    print("\nMonth Cycle (月運)")
    print_wu_yun_cycle(wu_yun_data["monthCycle"])
    
    print("\nHour Cycle (時運)")
    print_wu_yun_cycle(wu_yun_data["hourCycle"])

def format_bazi_output_fourpillars(data_dict):
    # Define the groups with English keys
    basic_keys = ['time', 'day', 'dayHidden', 'timeHidden', 'month', 'year', 'yearHidden', 'monthHidden']
    
    # Map for converting English keys to Chinese display
    key_display = {
        'time': '時',
        'day': '日',
        'month': '月',
        'year': '年',
        'dayHidden': '  ',
        'timeHidden': '  ',
        'yearHidden': '  ',
        'monthHidden': '  '
    }
    
    def format_group(keys, values):
        first_row = []
        second_row = []
        for key in keys:
            if key in values:
                first_row.append(key_display[key])
                second_row.append(" ")

        third_row = []
        fourth_row = []
        for key in keys:
            if key in values:
                value = values[key]
                if isinstance(value, str):
                    third_row.append(value[0])
                    fourth_row.append(value[1])
                else:
                    third_row.append(str(value[0]))
                    fourth_row.append(str(value[1]))

        return [
            "".join(first_row),
            "".join(second_row),
            "".join(third_row),
            "".join(fourth_row)
        ]

    # Format and print the basic pillars
    rows = format_group(basic_keys, data_dict)
    for row in rows:
        print(row)
    print()

def print_complete_wuxi_data(wuxi_data):
    """
    Print the complete WuXi data in a formatted layout.
    """
    # Print solar term information
    print("Solar Term Information (節氣):")
    print("=" * 50)
    solar_term = wuxi_data["solarTerm"]
    print(f"Current Term: {solar_term['current']['name']}")
    print(f"Start Date: {solar_term['current']['date']}")
    print(f"Days Since Start: {solar_term['current']['daysSinceStart']}")
    print(f"Days to Next Term: {solar_term['current']['daysToNext']}")
    if solar_term['next']['name']:
        print(f"Next Term: {solar_term['next']['name']} ({solar_term['next']['date']})")
    print()
    
    # Print top grid
    print("Top Grid (八字):")
    print("=" * 50)
    format_bazi_output_fourpillars(wuxi_data["topGrid"])
    print()

    # Print WuXi pillars
    print("WuXi Pillars (五系):")
    print("=" * 50)
    wuxi_pillars = wuxi_data["topGrid"]["wuxipillar"]
    print(f"Year Pillar: {wuxi_pillars['year']}")
    print(f"Month Pillar: {wuxi_pillars['month']}")
    print(f"Day Pillar: {wuxi_pillars['day']}")
    print(f"Hour Pillar: {wuxi_pillars['hour']}")
    print()

    # Print cycle indices
    print("Cycle Indices:")
    print("=" * 50)
    print(f"Year Cycle Index: {wuxi_data['yearCycle']['index']}")
    print(f"Month Cycle Index: {wuxi_data['monthCycle']['index']}")
    print(f"Day Cycle Index: {wuxi_data['dayCycle']['index']}")
    print(f"Hour Cycle Index: {wuxi_data['hourCycle']['index']}")
    print()
    
    # Print year and day cycles (六氣)
    print_liu_xi_cycle(wuxi_data)
    
    # Print month and time cycles (五運)
    print_complete_wu_yun_cycles(wuxi_data)

# Example usage:
# wuxi_data = get_complete_wuxi_data(2024, 1, 1, 12)
# print_complete_wuxi_data(wuxi_data)

def print_all_solar_terms(year: int):
    """
    Print all solar terms for a given year.
    """
    print(f"\nSolar Terms for {year}:")
    print("=" * 50)
    solar_terms = bazi.get_solar_terms(year)
    
    for i, term_date in enumerate(solar_terms):
        # Convert to naive datetime before passing to get_Luna_Month_With_Season
        naive_date = datetime(term_date.year, term_date.month, term_date.day, 
                            term_date.hour, term_date.minute, term_date.second)
        # Adjust the date by adding one day to get the correct term
        adjusted_date = naive_date - timedelta(days=1)
        term_name, _ = bazi.get_Luna_Month_With_Season(adjusted_date)
        print(f"{term_name}: {term_date.strftime('%Y-%m-%d %H:%M:%S')}")

def test_get_Luna_Month_With_Season():
    """
    Test function to check get_Luna_Month_With_Season output for different dates
    """
    print("\nTesting get_Luna_Month_With_Season:")
    print("=" * 50)
    
    # Test dates
    test_dates = [
        datetime(2025, 1, 1, 12),  # Start of year
        datetime(2025, 2, 4, 12),  # Around LiChun
        datetime(2025, 3, 21, 12), # Around ChunFen
        datetime(2025, 6, 21, 12), # Around XiaZhi
        datetime(2025, 9, 23, 12), # Around QiuFen
        datetime(2025, 12, 22, 12) # Around DongZhi
    ]
    
    for date in test_dates:
        term_name, index = bazi.get_Luna_Month_With_Season(date)
        print(f"\nDate: {date.strftime('%Y-%m-%d %H:%M')}")
        print(f"Solar Term: {term_name}")
        print(f"Index: {index}")

def test_flip_pillars():
    """
    Test the flip pillar calculations with various scenarios
    """
    print("\nTesting Flip Pillars:")
    print("=" * 50)
    
    # Test cases with birth date and current date
    test_cases = [
        {
            "birth_date": datetime(1979, 4, 27, 13),
            "current_date": datetime(2025, 5, 1, 12),
            "gender": "male",
            "desc": "Male no flip"
        },
        {
            "birth_date": datetime(1979, 4, 27, 13),
            "current_date": datetime(2025, 1, 1, 12),
            "gender": "male",
            "desc": "Male with flip"
        },
        {
            "birth_date": datetime(1957, 3, 4, 21),
            "current_date": datetime(1967, 6, 21, 23),
            "gender": "male",
            "desc": "Male First FLip"
        },
        {
            "birth_date": datetime(1957, 3, 4, 21),
            "current_date": datetime(1988, 6, 21, 23),  # Test with base time only
            "gender": "male",
            "desc": "Male second flip"
        },
        {
            "birth_date": datetime(1980, 3, 21, 12),
            "current_date": datetime(2024, 3, 21, 12),
            "gender": "male",
            "desc": "Current time calculation"
        }
    ]
    
    for case in test_cases:
        print(f"\nTest Case: {case['desc']}")
        print("-" * 30)
        
        # Get base pillars first
        birth = case['birth_date']
        base = bazi.get_wuxi_ymdh_base(
            birth.year,
            birth.month,
            birth.day,
            birth.hour
        )
        
        # Get flipped pillars
        flipped = bazi.calculate_flip_pillars(
            birth.year,
            birth.month,
            birth.day,
            birth.hour,
            case['gender'],
            case['current_date']
        )
        
        # Print comparison
        print("Base Pillars:")
        format_bazi_output_3(base)
        print("\nFlipped Pillars:")
        format_bazi_output_3(flipped)

def test_siyun():
    """
    Test the SiYun and DaYun calculations with various scenarios
    """
    print("\nTesting SiYun and DaYun Calculations:")
    print("=" * 50)
    
    # Test cases with birth date and current date
    test_cases = [
        {
            "birth_date": datetime(1979, 4, 27, 13),  # wei時
            "current_date": datetime(2024, 1, 1, 23),
            "gender": "male",
            "desc": "Male at 子時 (23:00-01:00)"
        },
        {
            "birth_date": datetime(1979, 4, 27, 13),  #未時
            "current_date": datetime(2026, 1, 1, 23),
            "gender": "male",
            "desc": "Male at 子時 (23:00-01:00)"
        },
        {
            "birth_date": datetime(1957, 3, 4, 22),  # 子時
            "current_date": datetime(2026, 1, 1, 23),
            "gender": "male",
            "desc": "Male at 子時 (23:00-01:00)"
        },
        {
            "birth_date": datetime(1985, 6, 21, 12),  # 午時
            "current_date": datetime(2024, 6, 21, 12),
            "gender": "male",
            "desc": "Male at 午時 (11:00-13:00)"
        },
        {
            "birth_date": datetime(1995, 12, 22, 0),  # 子時
            "current_date": datetime(2024, 12, 22, 0),
            "gender": "female",
            "desc": "Female at 子時 (23:00-01:00)"
        }
    ]
    
    for case in test_cases:
        print(f"\nTest Case: {case['desc']}")
        print("-" * 30)
        
        # Get base pillars using birth date
        birth = case['birth_date']
        base = bazi.get_wuxi_ymdh_base(
            birth.year,
            birth.month,
            birth.day,
            birth.hour
        )
        
        print("\nSiYun Results:")
        print("-" * 30)
        # Print SiYun using birth hour pillar, birth year stem, and current date
        bazi.print_siyun(
            case['gender'],
            base['時'],  # Hour pillar from birth time
            base['年'][0],  # Year stem from birth time
            case['birth_date']  # Current date for age calculation
        )
        
        # Also test JSON output for SiYun
        json_result = bazi.json_siyun(
            case['gender'],
            base['時'],
            base['年'][0],
            case['birth_date']
        )
        
        print("\nSiYun JSON Format:")
        for i, entry in enumerate(json_result, 1):
            print(f"時運 {i}: {entry}")
            
        print("\nDaYun Results:")
        print("-" * 30)
        # Print DaYun using birth year and month pillars
        bazi.print_daiYun(
            case['gender'],
            base['年'],  # Year pillar from birth time
            base['月'],  # Month pillar from birth time
            case['birth_date']  # Current date for age calculation
        )

def main():
    # Add test function calls
    test_siyun()
    test_flip_pillars()
    
    # Print all solar terms for 2025
    print_all_solar_terms(2025)
    
    # Example birth date
    birth_date = datetime(1979, 4, 27, 13, tzinfo=pytz.timezone('Asia/Shanghai'))
    
    # Generate bazi analysis for birth date
    generate_bazi_analysis(birth_date)
    
    # Get and display solar terms for the birth year
    print("\nSolar Terms for birth year:")
    # solar_terms = bazi.get_solar_terms(birth_date.year)
    
    # # Find days to next solar term
    # days, next_term, term_name = bazi.find_days_to_next_solar_term(birth_date, solar_terms)
    # print(f"\nCurrent time: {birth_date}")
    # print(f"Next solar term: {next_term} - {term_name}")
    # print(f"Days until next solar term: {days:.2f} days")

    # Example: Calculate bazi for a specific date and time
    year = 2025
    month = 3
    day = 11
    hour = 10

    # Call get_ymdh_base
    # bazi_data = bazi.get_ymdh_base(year, month, day, hour)
    

    print("========This is the base bazi=========")
    
    # Print the results
    print(f"\nBazi calculation for {year}-{month:02d}-{day:02d} {hour:02d}:00")

    # format_bazi_output_fourpillars(bazi.get_ymdh_base(year, month, day, hour))

    # print_liu_xi_cycle(bazi.get_liu_xi_cycle(year, month, day, hour))

    # print_complete_wu_yun_cycles(bazi.get_wu_yun_cycle(year, month, day, hour))

    wuxi_data = bazi.get_complete_wuxi_data(year, month, day, hour)
    print_complete_wuxi_data(wuxi_data)

    print(wuxi_data)

    solar_terms = bazi.get_solar_terms(1979)  # Your existing solar terms list
    date = datetime(1979, 4, 27, 13, 30, tzinfo=pytz.timezone('Asia/Shanghai'))
    days, next_term, term_name = bazi.find_days_to_next_solar_term(date, solar_terms)

    print(f"Days: {days}, Next Term: {next_term}, Term Name: {term_name}")


if __name__ == "__main__":
    main()