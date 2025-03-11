
import json
from bazi import bazi


def test_wuxi_endpoint():
    # Test case parameters
    year = 2024
    month = 3
    day = 15
    hour = 9

    try:
        # Call the function directly
        # result = bazi.get_complete_wuxi_data(year, month, day, hour)
        
        # Print the result
        # print("\n=== Wuxi Data Test Results ===")
        # print(json.dumps(result, ensure_ascii=False, indent=2))
        # Test base bazi endpoint
        # print("\n=== Base Bazi Test Results ===")
        # base_result = bazi.get_dmdh_base(year, month, day, hour)
        # print(json.dumps(base_result, ensure_ascii=False, indent=2))

        # Test main get_base_bazi endpoint
        print("\n=== Main Base Bazi Test Results ===")
        from main import get_base_bazi
        base_api_result = get_base_bazi(year, month, day, hour)
        print(base_api_result)
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_wuxi_endpoint()