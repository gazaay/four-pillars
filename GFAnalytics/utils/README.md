# GFAnalytics Utilities

This directory contains utility modules that provide common functionality used throughout the GFAnalytics framework.

## CSV Utilities (`csv_utils.py`)

The CSV utilities module provides functions to easily log DataFrames to CSV files for debugging and analysis purposes.

### Usage

```python
from GFAnalytics.utils.csv_utils import logdf, configure

# Log a DataFrame with default settings
logdf(my_dataframe, 'my_data')

# Log with custom options
logdf(my_dataframe, 'custom_data', index=False, float_format='%.2f')

# Configure with a specific config file
configure('path/to/config.yaml')

# Log with compression
logdf(large_dataframe, 'large_data', compression='gzip')
```

### Configuration

CSV logging can be configured in the main `config.yaml` file:

```yaml
# CSV Logging Configuration
csv_logging:
  enabled: true                # Enable/disable CSV logging
  output_dir: "csv_logs"       # Directory for CSV log files
  include_timestamp: true      # Add timestamp to filenames
  timestamp_format: "%Y%m%d_%H%M%S"  # Format for timestamp
  max_rows: 1000               # Maximum rows to log (0 for unlimited)
  index: true                  # Include DataFrame index in CSV
  compression: null            # Optional compression (null, 'gzip', 'bz2', 'zip', 'xz')
  float_format: "%.6g"         # Format for floating point numbers
  encoding: "utf-8"            # File encoding
```

### API Reference

#### `logdf(df, name, config_path=None, **kwargs)`

Log a DataFrame to a CSV file.

- `df`: The pandas DataFrame to log
- `name`: Name for the CSV file (without .csv extension)
- `config_path`: Optional path to configuration file
- `**kwargs`: Additional arguments passed to `DataFrame.to_csv()`

Returns the path to the saved CSV file, or None if logging is disabled.

#### `configure(config_path)`

Configure the global DataFrame logger with a specific configuration file.

- `config_path`: Path to configuration file

Returns the configured logger instance.

#### `DataFrameLogger` Class

For more advanced usage, you can create instances of the `DataFrameLogger` class directly:

```python
from GFAnalytics.utils.csv_utils import DataFrameLogger

# Create a logger with custom config
logger = DataFrameLogger('path/to/config.yaml')

# Log a DataFrame
logger.log_df(my_dataframe, 'my_data')
```

### Example

```python
import pandas as pd
from GFAnalytics.utils.csv_utils import logdf

# Create sample data
data = pd.DataFrame({
    'date': pd.date_range('2023-01-01', periods=10),
    'value': range(10),
    'category': ['A', 'B', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B']
})

# Log the DataFrame
csv_path = logdf(data, 'sample_data')
print(f"Data saved to: {csv_path}")

# Log a subset with custom options
filtered_data = data[data['category'] == 'A']
logdf(filtered_data, 'category_a_data', index=False)
``` 