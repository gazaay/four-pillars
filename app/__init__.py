# __init__.py
import logging

logging.basicConfig(level=logging.INFO)

import os
import sys

# Determine the directory of the script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Check if the 'app' directory is in the parent folder
parent_directory = os.path.abspath(os.path.join(script_directory, '..'))
app_directory = os.path.join(parent_directory, 'app')

if os.path.exists(app_directory) and os.path.isdir(app_directory):
    # If 'app' is in the parent folder and is a directory, add it to the Python path
    sys.path.append(parent_directory)