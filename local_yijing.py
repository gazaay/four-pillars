#!/usr/bin/env python3
"""
Test script for the yijing module
This script demonstrates how to use the yijing module to convert phone numbers to hexagrams
"""

from app.yijing import phone_to_hexagram, format_hexagram, Hexagram, TRIGRAM_TO_HEXAGRAM

def test_specific_trigram_combination():
    """Test a specific trigram combination: (5, 5) which should result in XUN (57.䷸ 巽)"""
    hex_tuple = (5, 5)
    if hex_tuple in TRIGRAM_TO_HEXAGRAM:
        hexagram = TRIGRAM_TO_HEXAGRAM[hex_tuple]
        print(f"Trigram combination {hex_tuple} corresponds to: {format_hexagram(hexagram)}")
    else:
        print(f"No hexagram found for {hex_tuple}")

def test_phone_to_hexagram():
    """Test converting phone numbers to hexagrams"""
    test_numbers = [
        "1234 5678",  # Sample phone number
        "9876 5432",  # Another sample
        "2222 3333",  # Repeated digits
        "1111 1111",  # All same digit
        "5555 5555",  # Should give XUN (57.䷸ 巽) as 5+5+5+5=20, 20-8-8=4, 5+5+5+5=20, 20-8-8=4, (5,5)
        "1247 6789"   # Random digits
    ]
    
    for number in test_numbers:
        try:
            hexagram = phone_to_hexagram(number)
            print(f"Phone number {number} corresponds to: {format_hexagram(hexagram)}")
        except ValueError as e:
            print(f"Error processing {number}: {e}")

def test_example_from_requirements():
    """Test the specific example from requirements: (4, 5) should give HENG (32.䷟ 恒)"""
    hex_tuple = (4, 5)
    if hex_tuple in TRIGRAM_TO_HEXAGRAM:
        hexagram = TRIGRAM_TO_HEXAGRAM[hex_tuple]
        print(f"Example trigram combination {hex_tuple} corresponds to: {format_hexagram(hexagram)}")
    else:
        print(f"No hexagram found for {hex_tuple}")
    
    # Construct a phone number that would result in (4, 5)
    # First part should sum to a multiple of 8 + 4
    # Second part should sum to a multiple of 8 + 5
    # For example: 1111 (sum=4) and 1112 (sum=5)
    test_phone = "1111 1112"
    try:
        hexagram = phone_to_hexagram(test_phone)
        print(f"Phone number {test_phone} corresponds to: {format_hexagram(hexagram)}")
    except ValueError as e:
        print(f"Error processing {test_phone}: {e}")

def manual_input_test():
    """Allow user to input a phone number for testing"""
    print("\nManual Phone Number Test")
    print("=======================")
    while True:
        phone = input("Enter a Hong Kong phone number (8 digits) or 'q' to quit: ")
        if phone.lower() == 'q':
            break
        
        try:
            hexagram = phone_to_hexagram(phone)
            print(f"Result: {format_hexagram(hexagram)}")
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("TESTING YIJING HEXAGRAM CONVERSIONS")
    print("==================================")
    
    print("\nTest 1: Specific Trigram Combination (5, 5)")
    test_specific_trigram_combination()
    
    print("\nTest 2: Example from Requirements (4, 5)")
    test_example_from_requirements()
    
    print("\nTest 3: Sample Phone Numbers")
    test_phone_to_hexagram()
    
    # Uncomment to allow manual testing
    manual_input_test()
    
    print("\nTests completed.") 