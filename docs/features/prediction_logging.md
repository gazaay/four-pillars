# Prediction Pipeline Logging

## Overview

The Prediction Pipeline Logging feature extends the DataFrame Logging functionality to provide comprehensive diagnostic and analytical capabilities throughout the prediction workflow in GFAnalytics. This feature enables developers and data scientists to inspect data at each stage of the prediction process, troubleshoot issues, and analyze how data transforms from raw inputs to final predictions.

## Components

The Prediction Pipeline Logging is implemented in two key components:

1. **FutureDataGenerator** (`future_data.py`) - Generates future dates and prepares data for prediction
2. **Predictor** (`predictor.py`) - Uses the prepared data to generate predictions

## Logging Points in FutureDataGenerator

The `FutureDataGenerator` class logs DataFrames at the following points:

| Log Name | Description | Typical Filename |
|----------|-------------|------------------|
| `future_generator_dates` | Initial list of future dates | `TIMESTAMP_future_generator_dates.csv` |
| `future_generator_dates_details` | Detailed information about generated dates | `TIMESTAMP_future_generator_dates_details.csv` |
| `future_generator_initial_data` | Basic DataFrame with dates and stock code | `TIMESTAMP_future_generator_initial_data.csv` |
| `future_generator_bazi_input_dates` | Dates passed to the Bazi generator | `TIMESTAMP_future_generator_bazi_input_dates.csv` |
| `future_generator_bazi_data` | Generated Bazi attributes | `TIMESTAMP_future_generator_bazi_data.csv` |
| `future_generator_bazi_generated_data` | Complete Bazi data after generation | `TIMESTAMP_future_generator_bazi_generated_data.csv` |
| `future_generator_merged_data` | Data after merging dates with Bazi attributes | `TIMESTAMP_future_generator_merged_data.csv` |
| `future_generator_bazi_transformed_data` | Data after Bazi feature transformation | `TIMESTAMP_future_generator_bazi_transformed_data.csv` |
| `future_generator_chengshen_transformed_data` | Data after ChengShen transformation | `TIMESTAMP_future_generator_chengshen_transformed_data.csv` |
| `future_generator_with_listing_bazi` | Data after adding stock listing Bazi attributes | `TIMESTAMP_future_generator_with_listing_bazi.csv` |
| `future_generator_encoded_data` | Final encoded data ready for prediction | `TIMESTAMP_future_generator_encoded_data.csv` |
| `future_generator_encoders_info` | Information about label encoders used | `TIMESTAMP_future_generator_encoders_info.csv` |

### Error Logging

In addition to normal workflow logging, the `FutureDataGenerator` also logs error states:

| Error Log Name | Description |
|----------------|-------------|
| `future_generator_bazi_transform_error_data` | Data that caused an error during Bazi transformation |
| `future_generator_chengshen_transform_error_data` | Data that caused an error during ChengShen transformation |
| `future_generator_listing_bazi_error_data` | Data when an error occurred adding listing date Bazi |
| `future_generator_bazi_error_info` | Error information from Bazi data generation |
| `future_generator_bazi_fallback_data` | Fallback empty data created after an error |
| `future_generator_encoding_error_data` | Data that caused an error during encoding |

## Logging Points in Predictor

The `Predictor` class logs DataFrames at the following points:

| Log Name | Description | Typical Filename |
|----------|-------------|------------------|
| `predictor_raw_future_data` | Initial raw data received for prediction | `TIMESTAMP_predictor_raw_future_data.csv` |
| `predictor_incoming_data` | Data at the start of feature preparation | `TIMESTAMP_predictor_incoming_data.csv` |
| `predictor_feature_columns` | List of feature columns to be used | `TIMESTAMP_predictor_feature_columns.csv` |
| `predictor_derived_feature_columns` | Feature columns derived from configuration | `TIMESTAMP_predictor_derived_feature_columns.csv` |
| `predictor_final_features` | Final feature set ready for model input | `TIMESTAMP_predictor_final_features.csv` |
| `predictor_prepared_features` | Features after preparation, ready for prediction | `TIMESTAMP_predictor_prepared_features.csv` |
| `predictor_predictions` | Raw prediction results | `TIMESTAMP_predictor_predictions.csv` |
| `predictor_predictions_with_confidence` | Predictions with confidence intervals (if available) | `TIMESTAMP_predictor_predictions_with_confidence.csv` |

### Error Logging

The `Predictor` also logs error states:

| Error Log Name | Description |
|----------------|-------------|
| `predictor_missing_features` | Features that were expected but missing from input data |
| `predictor_error_data` | Data that caused an error during prediction |

## Implementation Details

### FutureDataGenerator Logging Implementation

Logging in the `FutureDataGenerator` is implemented at key points in the data generation process:

```python
# Example: Logging future dates
future_dates_df = pd.DataFrame({'future_dates': future_dates})
logdf(future_dates_df, 'future_generator_dates')

# Example: Logging transformed data
logdf(future_data, 'future_generator_bazi_transformed_data')

# Example: Error logging
except Exception as e:
    self.logger.error(f"Failed to apply Bazi transformation: {str(e)}")
    # Log the data that caused the error
    logdf(future_data, 'future_generator_bazi_transform_error_data')
```

### Predictor Logging Implementation

Logging in the `Predictor` is implemented to track the feature preparation and prediction process:

```python
# Example: Logging incoming data
logdf(data, 'predictor_incoming_data')

# Example: Logging feature columns
feature_cols_df = pd.DataFrame({'feature_columns': feature_cols})
logdf(feature_cols_df, 'predictor_feature_columns')

# Example: Logging predictions
logdf(predictions, 'predictor_predictions')
```

## Use Cases

### Debugging

The comprehensive logging enables debugging of various issues:

1. **Missing Features** - Identify which features are missing in the prediction data
2. **Encoding Issues** - Debug problems with label encoding by examining the encoded data
3. **Transformation Errors** - Locate where transformations fail in the pipeline
4. **Model Input Validation** - Verify that the data going into the model is correctly formatted

### Analysis

The logs can be used for in-depth analysis:

1. **Data Distribution** - Analyze the distribution of features at different pipeline stages
2. **Feature Engineering** - Examine how raw data is transformed into model features
3. **Model Performance** - Compare predictions with features to understand model behavior
4. **Pipeline Optimization** - Identify bottlenecks or redundant steps in the pipeline

## Best Practices

When working with prediction pipeline logging:

1. **Selective Logging** - For performance reasons, consider disabling logging in production environments
2. **Compression** - Use compression for large DataFrames to save disk space
3. **Row Limiting** - Use appropriate row limits to avoid excessive log sizes
4. **Log Rotation** - Implement a strategy to archive or delete old log files

## Future Improvements

Potential future enhancements include:

1. **Selective Column Logging** - Only log specific columns of interest in large DataFrames
2. **Performance Metrics** - Log timing information for each stage of the pipeline
3. **Automated Analysis** - Tools to automatically analyze logs for anomalies or patterns
4. **Distributed Logging** - Support for logging in distributed computing environments
5. **Interactive Visualization** - Tools to visualize the transformation of data through the pipeline 