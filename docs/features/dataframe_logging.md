# DataFrame Logging

## Overview

The DataFrame Logging feature provides a simple and consistent way to log pandas DataFrames to CSV files throughout the GFAnalytics framework. This functionality is particularly useful for debugging, data analysis, and tracking how data changes across different stages of the prediction pipeline.

## Key Components

### CSV Utilities Module (`csv_utils.py`)

The core functionality is provided by the `csv_utils.py` module, which contains:

- `DataFrameLogger` class - Handles the CSV file creation and configuration
- `logdf()` function - A global utility function for easy DataFrame logging
- `configure()` function - For configuring the logging behavior

### Configuration

DataFrame logging is configured in the main `config.yaml` file under the `csv_logging` section:

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

## Usage

### Basic Usage

To log a DataFrame to a CSV file:

```python
from GFAnalytics.utils.csv_utils import logdf

# Log a DataFrame with default settings
logdf(my_dataframe, 'my_data')
```

This will create a timestamped CSV file in the configured output directory, e.g., `20240715_123456_my_data.csv`.

### Custom Options

You can customize the CSV output by passing additional parameters:

```python
# Log with custom options
logdf(my_dataframe, 'custom_data', 
      index=False,            # Don't include index
      float_format='%.2f',    # Format floats to 2 decimal places
      compression='gzip',     # Compress the output
      sep=';')                # Use semicolon delimiter
```

All parameters that can be passed to pandas' `to_csv()` method are supported.

### Using a Specific Configuration

To use a specific configuration file:

```python
from GFAnalytics.utils.csv_utils import configure, logdf

# Configure with a specific config file
configure('path/to/config.yaml')

# Now all logdf calls will use this configuration
logdf(my_dataframe, 'my_data')
```

### Advanced Usage with DataFrameLogger Class

For more advanced usage, you can create instances of the `DataFrameLogger` class directly:

```python
from GFAnalytics.utils.csv_utils import DataFrameLogger

# Create a logger with custom config
logger = DataFrameLogger('path/to/config.yaml')

# Log a DataFrame
logger.log_df(my_dataframe, 'my_data')
```

## Integration with Prediction Pipeline

The DataFrame logging feature is integrated throughout the prediction pipeline:

### FutureDataGenerator

The `FutureDataGenerator` class logs DataFrames at various stages:

- Initial future dates
- Bazi data generation
- Transformed data after each processing step
- Encoded data before prediction
- Error states when exceptions occur

### Predictor

The `Predictor` class logs:

- Raw input data
- Feature columns being used
- Missing features detected
- Final feature set for prediction
- Prediction results
- Error states during prediction

## Example Code

An example script is provided in `examples/prediction_logging_example.py` that demonstrates the DataFrame logging functionality:

```python
import pandas as pd
from GFAnalytics.prediction.future_data import FutureDataGenerator
from GFAnalytics.prediction.predictor import Predictor
from GFAnalytics.utils.csv_utils import configure, logdf

# Load configuration and configure logging
config, config_path = load_config()
configure(config_path)

# Create components
future_generator = FutureDataGenerator(config)
predictor = Predictor(config)

# Generate future data
future_data = future_generator.generate()

# Log the future data
logdf(future_data, 'example_future_data')

# Make predictions
predictions = predictor.predict(model, future_data)

# Log the predictions
logdf(predictions, 'example_predictions')
```

## Output Structure

The logged CSV files are organized as follows:

- Each file is saved in the configured output directory (default: `csv_logs/`)
- Files are named with a timestamp prefix by default: `YYYYMMDD_HHMMSS_name.csv`
- Row count is limited to the configured `max_rows` value (default: 1000)

## Testing

Unit tests for the DataFrame logging utility are provided in `tests/test_csv_utils.py`, covering:

- Basic logging functionality
- Custom options
- Error handling
- Compressed output
- Singleton pattern behavior

## Future Enhancements

Potential future enhancements to the DataFrame logging feature include:

1. Integration with cloud storage (e.g., Google Cloud Storage)
2. Support for other output formats (e.g., Parquet, Excel)
3. Advanced filtering options for what columns to include
4. Automatic data profiling and statistics generation
5. Web-based viewer for logged DataFrames
6. Integration with data visualization tools 