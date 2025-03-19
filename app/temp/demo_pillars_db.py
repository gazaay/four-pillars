"""
Demo script for the versioned pillars database functionality.
This demonstrates how to use the database-backed pillars dataset in notebooks.

To use in your notebook:

```python
# Add this to your notebook in a new cell
import sys
sys.path.append('/path/to/your/project')  # Make sure the app directory is accessible

from app.temp.pillar_helper import get_pillars_dataset

# Get pillars dataset from database or calculate if not available
# Version number should reflect your calculation logic or data structure
version = "v1.0"  # Change this when you update your pillar calculation logic
dataset = get_pillars_dataset(version=version, force_recalculate=False)

# Now dataset contains all the pillars - no need to run chengseng.adding_8w_pillars
print(f"Dataset has {len(dataset)} rows")
print(dataset.head())
```

For GF_lite_v2_0.ipynb usage, replace this code:

```python
# @title Step 3: Define time range
today = datetime.now()
# Set the time to 9:30 AM
today = today.replace(hour=9, minute=00, second=0, microsecond=0)

start_date = today - timedelta(days=1525)
end_date = today + timedelta(days=220)
# @title Step 4: Create a blank data frame with time column
time_range = pd.date_range(start=start_date, end=end_date, freq='1H').union(pd.date_range(end_date, end_date + pd.DateOffset(months=12), freq='D'))
dataset = pd.DataFrame({'time': time_range})
# @title Step 5: Adding 8w pillars to the dataset
dataset = chengseng.adding_8w_pillars(dataset)
```

With this:

```python
# @title Step 3-5: Get pillars dataset from database with versioning
from app.temp.pillar_helper import get_pillars_dataset

# Set version number - change this when you update the pillar calculation logic
pillar_version = "v1.0"  # Version identifier for this dataset
force_recalculate = False  # Set to True if you want to ignore the database and recalculate

# Get the dataset - this will either fetch from database or calculate if needed
dataset = get_pillars_dataset(version=pillar_version, force_recalculate=force_recalculate)

print(f"Using pillars dataset version {pillar_version} with {len(dataset)} rows")
```

Benefits:
1. Only calculates pillars once per version, then reuses from database
2. Much faster execution after the first calculation
3. Version tagging allows you to track different calculation methods or dataset structures
4. Consistent results across multiple runs
"""

# Example usage
if __name__ == "__main__":
    # This part only runs if you run this file directly, not when imported
    import pandas as pd
    from app.temp.pillar_helper import get_pillars_dataset
    
    # Set version and get dataset
    version = "v1.0"
    dataset = get_pillars_dataset(version=version)
    
    # Show results
    print(f"Dataset version {version} has {len(dataset)} rows")
    print("\nFirst 5 rows:")
    print(dataset.head())
    
    # Show column names
    print("\nDataset columns:")
    print(dataset.columns.tolist()) 