# @title Step 3-5: Get versioned pillars dataset from database

# First, make sure we can import our modules
import sys
import os
from pathlib import Path

# Add necessary paths to sys.path
current_dir = Path(os.getcwd())  # Current notebook directory
temp_dir = current_dir / "temp"  # temp directory in current dir
app_dir = current_dir / "app"    # app directory
app_temp_dir = app_dir / "temp"  # app/temp directory

# Try to add possible locations where the helper module might be
possible_paths = [temp_dir, app_temp_dir, app_dir, current_dir]
for path in possible_paths:
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.append(path_str)

# Try to import the helper
try:
    # Try direct import first
    from pillar_helper import get_pillars_dataset
except ImportError:
    try:
        # Try with temp prefix
        from temp.pillar_helper import get_pillars_dataset
    except ImportError:
        # Try with app.temp prefix
        from app.temp.pillar_helper import get_pillars_dataset

# Set version number - change this when you update the pillar calculation logic
pillar_version = "v1.0"  # Version identifier for this dataset

# Set to True if you want to force recalculation regardless of database status
force_recalculate = False  

# Get the dataset - this will either:
# 1. Fetch from database if version exists
# 2. Calculate and save to database if version doesn't exist
# 3. Force recalculation if force_recalculate=True
dataset = get_pillars_dataset(version=pillar_version, force_recalculate=force_recalculate)

print(f"Using pillars dataset version {pillar_version} with {len(dataset)} rows")
print(f"Date range: {dataset['time'].min()} to {dataset['time'].max()}")
print("First few rows:")
print(dataset.head()) 