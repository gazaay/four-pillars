#!/usr/bin/env python3
"""
Local development server for testing Firebase functions
"""

import functions_framework
import os
import sys

# Add parent directory to path to find the yijing module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the function from main.py
from main import api_handler

# Register the function with the Functions Framework
functions_framework.http(api_handler)

if __name__ == "__main__":
    # Start the local server
    print("Starting local server for testing...")
    print("Test the Yi Jing phone API with: http://localhost:8080/api/yijing/phone?phone=12345678")
    functions_framework.start() 