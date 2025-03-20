#!/usr/bin/env python
"""
Simple test script to verify our JSON serialization fix works correctly.
This script tests serializing metadata with datetime objects.
"""

import json
from datetime import datetime

def test_json_serialization():
    """Test that we can properly serialize metadata with datetime objects"""
    print("Testing JSON serialization of metadata...")
    
    # Create a metadata dictionary similar to what we use in the main code
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    metadata = {
        'days_back': 50,
        'days_forward': 2,
        'forecast_months': 12,
        'creation_date': current_time
    }
    
    try:
        # Try to serialize it to JSON
        json_str = json.dumps(metadata)
        print("Successfully serialized metadata to JSON:")
        print(json_str)
        
        # Now try to deserialize it
        deserialized = json.loads(json_str)
        print("\nSuccessfully deserialized JSON back to dict:")
        print(f"  - Days back: {deserialized.get('days_back')}")
        print(f"  - Days forward: {deserialized.get('days_forward')}")
        print(f"  - Forecast months: {deserialized.get('forecast_months')}")
        print(f"  - Creation date: {deserialized.get('creation_date')}")
        
        return True
    except Exception as e:
        print(f"Error during JSON serialization: {str(e)}")
        return False

def test_with_direct_datetime():
    """Test what happens if we try to serialize a datetime object directly"""
    print("\nTesting with direct datetime object (should fail)...")
    
    metadata_with_datetime = {
        'days_back': 50,
        'days_forward': 2,
        'forecast_months': 12,
        'creation_date': datetime.now()  # Direct datetime object
    }
    
    try:
        json_str = json.dumps(metadata_with_datetime)
        print("This should not succeed - if you see this, something is wrong!")
        return False
    except Exception as e:
        print(f"Expected error occurred: {str(e)}")
        print("This is normal! We need to convert datetime to string first.")
        return True

if __name__ == "__main__":
    test_json_serialization()
    test_with_direct_datetime()
    
    print("\nConclusion:")
    print("To avoid the 'Object of type datetime is not JSON serializable' error,")
    print("always convert datetime objects to strings before JSON serialization.")
    print("Example: datetime.now().strftime('%Y-%m-%d %H:%M:%S')") 