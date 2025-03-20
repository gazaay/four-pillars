# Quick Start Guide: Versioned Pillars Database

## What This Does

This system stores thousand-year pillars data in a database so you don't need to calculate it every time. Key benefits:
- **Much faster execution** after the first run
- **Version tracking** for different calculation methods
- **Customizable date ranges** for different analysis needs

## Setup

1. Copy these files to your project folder:
   - `pillar_db_handler.py` - Core database handler
   - `pillar_helper.py` - Easy-to-use helper functions
   - `test_pillar_db.py` - Command-line tool
   - `test_month_calculation.py` - Month testing tool

## Common Tasks

### Create a Dataset

```bash
# Basic dataset with default date range
python test_pillar_db.py v1.0 --create-dataset

# Small dataset for quick testing
python test_pillar_db.py test-small --create-dataset --days-back 10 --days-forward 2 --forecast-months 1

# Large dataset for production
python test_pillar_db.py v2.0 --create-dataset --days-back 1525 --days-forward 220 --forecast-months 12
```

### Test Existing Dataset

```bash
# Test the default version
python test_pillar_db.py

# Test a specific version
python test_pillar_db.py v2.0 --test
```

### Manage Database Versions

```bash
# Force recalculation of existing version
python test_pillar_db.py v1.0 --force --create-dataset

# Remove a version from the database
python test_pillar_db.py old-version --remove-database
```

### Test Specific Date Calculation

```bash
# Test default date (2025-12-24)
python test_month_calculation.py

# Test a different date with debug info
python test_month_calculation.py --date 2026-01-15 --hour 15 --debug
```

## Using in Notebooks

Add this to your notebook:

```python
# Import the helper
import sys, os
sys.path.append('/path/to/scripts')  # Adjust path
from pillar_helper import get_pillars_dataset

# Get dataset with default parameters
dataset = get_pillars_dataset(version="v1.0")

# OR with custom date range
dataset = get_pillars_dataset(
    version="analysis-2024",
    days_back=100,       # 100 days back from today
    days_forward=10,     # 10 days forward
    forecast_months=6    # 6 months forecast
)

print(f"Dataset loaded with {len(dataset)} rows")
```

## Date Range Parameters

All tools directly accept these parameters with no file modification needed:

- `--days-back DAYS`: Days to look back (default: 50)
- `--days-forward DAYS`: Days to look forward (default: 2)
- `--forecast-months MONTHS`: Months to forecast (default: 12)

## How It Works

1. The system stores date range parameters as metadata with each version
2. Parameters are passed directly to calculation functions
3. First run: Calculates pillars and stores to database with metadata
4. Later runs: Retrieves data from database (much faster)

## Database Details

- Project: `stock8word`
- Dataset: `GG88`
- Tables: 
  - `thousand_year_current_pillars` (pillars data)
  - `thousand_year_current_pillars_metadata` (version info)

## Best Practices

1. **Use descriptive version names**: Include info about the parameters in version names
   - Example: `v1.0-1525days-12mo` for a large dataset
   - Example: `test-small-10days` for a small test dataset
2. **Small datasets for development**: Use small date ranges while testing
3. **Standard date ranges**: Agree on standard parameters for production use
4. **Match parameters when testing**: Use the same parameters when testing as you did when creating