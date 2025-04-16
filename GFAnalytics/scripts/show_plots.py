#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line script to run GFAnalytics with plots displayed.
"""

import os
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """Run GFAnalytics with plots displayed."""
    # Get the command needed to run the main module with the show-plots option
    run_command = f"python -m GFAnalytics.main --show-plots"
    
    print(f"Running command: {run_command}")
    
    # Execute the command
    os.system(run_command)

if __name__ == "__main__":
    main() 