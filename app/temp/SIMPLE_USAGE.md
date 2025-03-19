# Simple Usage Guide for Versioned Pillars Database

## Setup

1. Copy these three files to your project directory:
   - `pillar_db_handler.py` - Database handler that stores/retrieves data
   - `pillar_helper.py` - Helper functions for easy use
   - `test_pillar_db.py` - Command-line test script

2. Put them in the same directory for simplicity (e.g., in your project root or in a subdirectory)

## Testing the Database

Run the test script to create the pillars and save them to the database:

```bash
# Go to the directory with the scripts
cd /path/to/your/scripts

# Run the test script with default version "v1.0"
python test_pillar_db.py

# Or specify a different version
python test_pillar_db.py v2.0

# To force recalculation even if version exists
python test_pillar_db.py v1.0 --force
```

## Using in a Notebook

Add this to a notebook cell to retrieve data from the database:

```python
# Make sure the script directory is in Python's path
import sys
import os
sys.path.append('/path/to/your/scripts')  # Adjust this path

# Import the helper
from pillar_helper import get_pillars_dataset

# Set version and get dataset
pillar_version = "v1.0"  # Version identifier
force_recalculate = False  # Set to True to force recalculation

# Get the dataset
dataset = get_pillars_dataset(version=pillar_version, force_recalculate=force_recalculate)

print(f"Using pillars dataset version {pillar_version} with {len(dataset)} rows")
```

## How It Works

1. First run: Calculates pillars and saves to database
2. Later runs: Retrieves data from database (much faster)
3. New version: Use a different version string when calculation method changes

## Database Details

The data is stored in:
- Project: `stock8word`
- Dataset: `GG88`
- Table: `thousand_year_current_pillars` 