# Versioned Eight Pillars Database

This module provides database-backed caching for the eight pillars (Bazi) data used in the Four Pillars analysis. It stores the calculated pillars in a BigQuery database and retrieves them when needed, avoiding repeated calculations of the same data.

## Benefits

1. **Performance**: Dramatically reduces execution time for notebooks and scripts after the first calculation
2. **Versioning**: Tracks different versions of pillar calculations, allowing for methodological changes
3. **Consistency**: Ensures the same data is used across different analyses
4. **Efficiency**: Avoids unnecessary recalculation of the same data

## Components

- `pillar_db_handler.py`: Core database functionality for storing and retrieving pillar data
- `pillar_helper.py`: User-friendly wrapper functions for use in notebooks
- `test_pillar_db.py`: Command-line test script
- `demo_pillars_db.py`: Example usage and documentation

## Usage in Notebooks

To use in your notebooks (like GF_lite_v2_0.ipynb), replace the existing pillar calculation code with:

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

## Command-line Testing

You can test the database functionality from the command line:

```bash
# Test with default version (v1.0)
python app/temp/test_pillar_db.py

# Test with a specific version
python app/temp/test_pillar_db.py v2.0

# Force recalculation
python app/temp/test_pillar_db.py v1.0 --force
```

## Version Management

- Use a new version number when you change the pillar calculation logic
- Version format recommendation: `v1.0`, `v1.1`, `v2.0`, etc.
- When testing changes, you can use a development version like `dev-v1.0`

## Database Details

- Project: `stock8word`
- Dataset: `GG88`
- Table: `thousand_year_current_pillars`
- Schema includes:
  - `time`: TIMESTAMP
  - `version`: STRING
  - Various pillar columns (year_pillar, month_pillar, etc.)

## Error Handling

If the database operations fail for any reason, the system will automatically fall back to direct calculation without the database. 