
import json
from app import bazi


def test_wuxi_endpoint():
    # Test case parameters
    year = 2024
    month = 3
    day = 15
    hour = 9

    try:
        # Call the function directly
        result = bazi.get_wuxi_data(year, month, day, hour)
        
        # Print the result
        print("\n=== Wuxi Data Test Results ===")
        print(json.loads(result))
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_wuxi_endpoint()