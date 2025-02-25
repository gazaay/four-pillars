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
    # Define the groups - now including negative entries
    basic_keys = ['時', '日', '-日', '-時', '月', '年', '-年', '-月']
    
    def format_group(keys, values):
        first_row = []
        second_row = []
        for key in keys:
            if key in values:
                if len(key) == 1:  # Regular pillar
                    first_row.append(key)
                    second_row.append(" ")
                else:
                    first_row.append("  ")
                    second_row.append(" ")

        third_row = []
        fourth_row = []
        for key in keys:
            if key in values:
                value = values[key]
                third_row.append(value[0])
                fourth_row.append(value[1])

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
    # Print top grid
    print("Top Grid (八字):")
    print("=" * 50)
    format_bazi_output_fourpillars(wuxi_data["topGrid"])
    print()
    
    # Print year and day cycles (六氣)
    print_liu_xi_cycle(wuxi_data)
    
    # Print month and time cycles (五運)
    print_complete_wu_yun_cycles(wuxi_data)

# Example usage:
# wuxi_data = get_complete_wuxi_data(2024, 1, 1, 12)
# print_complete_wuxi_data(wuxi_data)


def main():
    # Example birth date
    birth_date = datetime(1979, 4, 27, 13, tzinfo=pytz.timezone('Asia/Shanghai'))
    
    # Generate bazi analysis for birth date
    generate_bazi_analysis(birth_date)
    
    # Get and display solar terms for the birth year
    print("\nSolar Terms for birth year:")
    solar_terms = bazi.get_solar_terms(birth_date.year)
    
    # Find days to next solar term
    days, next_term, term_name = bazi.find_days_to_next_solar_term(birth_date, solar_terms)
    print(f"\nCurrent time: {birth_date}")
    print(f"Next solar term: {next_term} - {term_name}")
    print(f"Days until next solar term: {days:.2f} days")

    # Example: Calculate bazi for a specific date and time
    year = 2024
    month = 7
    day = 14
    hour = 6

    # Call get_ymdh_base
    bazi_data = bazi.get_ymdh_base(year, month, day, hour)
    
    # Print the results
    print(f"\nBazi calculation for {year}-{month:02d}-{day:02d} {hour:02d}:00")

    format_bazi_output_fourpillars(bazi.get_ymdh_base(year, month, day, hour))

    print_liu_xi_cycle(bazi.get_liu_xi_cycle(year, month, day, hour))

    print_complete_wu_yun_cycles(bazi.get_wu_yun_cycle(year, month, day, hour))

    wuxi_data = bazi.get_complete_wuxi_data(year, month, day, hour)
    print_complete_wuxi_data(wuxi_data)

    print(wuxi_data)
if __name__ == "__main__":
    main()