# Encoding Utilities

## Overview

The Encoding Utilities feature provides a robust framework for handling categorical data in GFAnalytics. It enables the seamless transformation of textual and categorical variables into numerical formats suitable for machine learning models, with built-in support for encoding/decoding operations throughout the data pipeline.

## Core Functionality

The encoding utilities address several critical needs in the data science workflow:

1. **Categorical Data Detection** - Automatically identify categorical columns in DataFrames
2. **Label Encoding** - Transform categorical variables into numerical representations
3. **Persistent Encoders** - Save and reuse encoders to ensure consistency between training and prediction
4. **Decoding** - Convert numerical predictions back to their original categorical formats
5. **Standardized Feature Preparation** - Consistent approach for preparing features across the pipeline

## Components

The encoding utilities consist of several key components:

### 1. Categorical Column Detection

```python
def get_categorical_columns(df, threshold=10):
    """
    Identify categorical columns in a DataFrame.
    
    Args:
        df (pandas.DataFrame): The input DataFrame
        threshold (int): Maximum number of unique values for a column to be considered categorical
        
    Returns:
        list: List of column names identified as categorical
    """
```

This function automatically detects which columns in a DataFrame should be treated as categorical based on:
- Object/string data types
- Number of unique values (below a configurable threshold)

### 2. Column Encoding

```python
def encode_column(df, column, encoder=None):
    """
    Encode a single column with a label encoder.
    
    Args:
        df (pandas.DataFrame): The input DataFrame
        column (str): The column to encode
        encoder (sklearn.preprocessing.LabelEncoder, optional): Pre-existing encoder
        
    Returns:
        tuple: (Encoded DataFrame, LabelEncoder instance)
    """
```

This function handles encoding of a specific column:
- Encodes categorical values to numeric integers
- Handles missing values
- Can use an existing encoder or create a new one

### 3. Data Processing and Encoding

```python
def process_encode_data(df, categorical_cols=None, encoders=None):
    """
    Process and encode the entire DataFrame.
    
    Args:
        df (pandas.DataFrame): The input DataFrame
        categorical_cols (list, optional): List of categorical columns to encode
        encoders (dict, optional): Dictionary of pre-existing encoders
        
    Returns:
        tuple: (Encoded DataFrame, Dictionary of encoders)
    """
```

This function manages the encoding process for the entire DataFrame:
- Automatically detects categorical columns if not specified
- Applies encoding to each categorical column
- Returns the transformed DataFrame and a dictionary of encoders

### 4. Prediction Decoding

```python
def decode_prediction_data(encoded_indices, encoder, error_value='UNKNOWN'):
    """
    Decode encoded prediction data back to original categories.
    
    Args:
        encoded_indices (list or array): Encoded prediction values
        encoder (sklearn.preprocessing.LabelEncoder): The encoder used for encoding
        error_value (str): Value to use for invalid indices
        
    Returns:
        list: Original categorical values
    """
```

This function converts encoded predictions back to human-readable categories:
- Takes numerical predictions and reverses the encoding
- Handles out-of-range or invalid indices
- Provides meaningful error values for invalid indices

### 5. Standardized Feature Preparation

```python
def prepare_feature_data(data, is_training=True):
    """
    Prepare feature data for model training or prediction by removing 
    non-feature columns and handling missing values.
    
    Args:
        data (pandas.DataFrame): The data to prepare.
        is_training (bool): Whether the data is for training (includes target column).
        
    Returns:
        tuple: A tuple containing (X, y) if is_training is True, otherwise (X, None).
    """
```

This function provides a standardized approach to prepare features across the entire pipeline:
- Removes non-feature columns (time, uuid, etc.)
- Handles missing and infinite values
- Separates target variable for training data
- Creates consistent feature sets across training, evaluation and prediction

## Standardized Feature Processing Pipeline

The GFAnalytics system uses a standardized approach for feature preparation across all components:

1. **Encoding Phase**: First, categorical features are encoded using `process_encode_data()`
2. **Feature Preparation Phase**: Then, encoded data is transformed into model-ready features using `prepare_feature_data()`

This standardized pipeline is used consistently in:

- **Model Training**: In `RandomForestModel._prepare_data()`
- **Model Prediction**: In `RandomForestModel.predict()`
- **Evaluation**: In `ModelEvaluator.evaluate()`
- **Future Data Generation**: In `FutureDataGenerator.generate()`
- **Prediction Pipeline**: In `Predictor.predict()`

This standardization ensures that:
- Features are processed consistently at every stage
- The same columns are included/excluded in all phases
- Missing values are handled identically throughout
- The feature transformation approach is maintained across components

## Usage Examples

### Basic Encoding

```python
import pandas as pd
from GFAnalytics.utils.encoding_utils import get_categorical_columns, process_encode_data
from GFAnalytics.utils.data_utils import prepare_feature_data

# Sample data
data = pd.DataFrame({
    'stock_code': ['AAPL', 'GOOGL', 'MSFT', 'AAPL'],
    'sector': ['Tech', 'Tech', 'Tech', 'Tech'],
    'trend': ['Up', 'Down', 'Flat', 'Up'],
    'price': [150.5, 2800.1, 340.2, 152.3]
})

# Step 1: Encode categorical columns
encoded_data, encoders = process_encode_data(data)

# Step 2: Prepare features using standardized utility 
X_features, y_target = prepare_feature_data(encoded_data, is_training=False)

# X_features will now contain only the features suitable for the model,
# with non-feature columns removed and missing values handled
```

### Using Pre-existing Encoders

```python
# New prediction data
new_data = pd.DataFrame({
    'stock_code': ['AMZN', 'AAPL', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Auto'],
    'trend': ['Up', 'Up', 'Up'],
    'price': [3400.5, 151.2, 900.1]
})

# Step 1: Re-use encoders from previous encoding
encoded_new_data, updated_encoders = process_encode_data(new_data, label_encoders=encoders)

# Step 2: Prepare features consistently
X_pred, _ = prepare_feature_data(encoded_new_data, is_training=False)
```

### Decoding Predictions

```python
from GFAnalytics.utils.encoding_utils import decode_prediction_data

# Assuming encoded predictions
predictions = [0, 1, 0, 2]

# Decode predictions back to original categories
trend_encoder = encoders['trend']
decoded_trends = decode_prediction_data(predictions, trend_encoder)
# Output: ['Up', 'Down', 'Up', 'Flat']
```

## Integration in GFAnalytics Workflow

The encoding utilities are integrated throughout the GFAnalytics pipeline:

1. **Training Phase**:
   - Categorical features are identified and encoded with `process_encode_data()`
   - Features are prepared with `prepare_feature_data()`
   - Encoders are saved along with the trained model

2. **Prediction Phase**:
   - Data for prediction is encoded using the same encoders
   - Features are prepared with the same standardized approach
   - Ensures consistency between training and prediction data

3. **Evaluation Phase**:
   - Encoded data is prepared using the same utility functions
   - Ensures the evaluation process mirrors the production prediction process

4. **Visualization Phase**:
   - Predictions are decoded back to original categories for interpretation
   - Enables meaningful visualization and reporting

## Edge Cases and Handling

The encoding utilities are designed to handle various edge cases:

1. **Unknown Categories**:
   - When new categorical values appear during prediction
   - Gracefully handles these by assigning them to an appropriate category

2. **Missing Values**:
   - Handles null/NaN values in categorical columns
   - Ensures consistent behavior for missing data

3. **Categorical vs. Numerical Detection**:
   - Smart detection of whether a column should be treated as categorical
   - Configurable thresholds for unique value counts

4. **Missing Features**:
   - When a feature exists in training but not in prediction data
   - Handled by adding the missing feature with default value (0)

5. **Extra Features**:
   - When prediction data contains columns not used in training
   - These columns are filtered out to ensure consistent feature sets

## Behind the Scenes

The encoding utilities leverage scikit-learn's `LabelEncoder` class but extend its functionality:

```python
from sklearn.preprocessing import LabelEncoder

# Standard encoding
encoder = LabelEncoder()
encoder.fit(['Up', 'Down', 'Flat'])
encoded = encoder.transform(['Up', 'Down', 'Flat', 'Up'])
# Output: [2, 0, 1, 2]

# Decoding
original = encoder.inverse_transform([2, 0, 1, 2])
# Output: ['Up', 'Down', 'Flat', 'Up']
```

The GFAnalytics implementation adds:
- Automatic detection of categorical columns
- DataFrame-level operations instead of just arrays
- Error handling for missing values and unknown categories
- Integration with the broader analytics pipeline
- Standardized feature preparation across all components

## Testing

The encoding utilities are thoroughly tested with unit tests in `tests/test_encoding_utils.py`, covering:

1. **Functionality Tests**:
   - Correct identification of categorical columns
   - Proper encoding of columns with and without existing encoders
   - Accurate decoding of predictions

2. **Edge Case Tests**:
   - Handling of missing values
   - Behavior with new categories during prediction
   - Corner cases like empty DataFrames or all-null columns

## Future Improvements

Potential enhancements to the encoding utilities include:

1. **One-Hot Encoding** - Add support for one-hot encoding as an alternative to label encoding
2. **Target Encoding** - Implement mean target encoding for high-cardinality features
3. **Custom Encoding Maps** - Allow manual specification of encoding mappings
4. **Feature Hashing** - Support for feature hashing techniques for high-cardinality features
5. **Automated Encoding Selection** - Smart selection of encoding technique based on data characteristics
6. **Feature Importance-Based Selection** - Automatic feature pruning based on importance scores 