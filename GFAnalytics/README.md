# GFAnalytics Framework

A machine learning framework for predicting stock market or indices pricing using Bazi (Chinese metaphysics) attributes.

## Overview

GFAnalytics uses machine learning algorithms to predict stock market movements by combining traditional financial data with Bazi (八字) attributes. The framework transforms time-based Bazi pillars into ChengShen (長生) attributes for training, creating a unique approach to market prediction.

## Project Structure

```
GFAnalytics/
├── config/                  # Configuration files
│   └── config.yaml          # Main configuration file
├── data/                    # Data processing modules
│   ├── stock_data.py        # Stock data retrieval from YFinance/ICE
│   ├── bazi_data.py         # Bazi data generation
│   └── data_storage.py      # BigQuery storage utilities
├── features/                # Feature engineering
│   ├── bazi_features.py     # Bazi feature transformation
│   ├── chengshen.py         # ChengShen transformation
│   └── encoders.py          # Data encoding utilities
├── models/                  # ML model implementation
│   ├── random_forest.py     # Random Forest implementation
│   ├── model_storage.py     # Google Drive model storage
│   └── evaluation.py        # Model evaluation metrics
├── prediction/              # Prediction utilities
│   ├── future_data.py       # Future dataset creation
│   └── predictor.py         # Prediction implementation
├── visualization/           # Visualization tools
│   └── plots.py             # Plotting utilities
├── utils/                   # Utility functions
│   ├── time_utils.py        # Time conversion utilities
│   └── gcp_utils.py         # Google Cloud Platform utilities
├── main.py                  # Main entry point
└── README.md                # Project documentation
```

## Rules

1. **Timezone Handling**:
   - All datetime values must be in GMT+8 (Asia/Hong_Kong)
   - When loading data from different sources, convert to GMT+8 before processing

2. **Bazi Representation**:
   - All Bazi pillars are represented in Chinese characters
   - Mapping is required to make the data machine learning friendly
   - ChengShen transformation is used to standardize Bazi attributes

3. **Data Storage**:
   - All data must be persisted in BigQuery
   - Use appropriate table schemas for different data types

4. **Configuration**:
   - The framework is configuration-driven
   - Configure stock codes, date ranges, training periods, etc. in config files
   - Store credentials securely

5. **File Organization**:
   - All files must be inside the GFAnalytics folder
   - Follow the project structure for organization

## Configuration Parameters

- `stock_code`: Stock or index code to analyze
- `date_range`: Date range for training data
- `period`: Trading period (1H, 2H, 1D, etc.)
- `gdrive_location`: Google Drive location for model storage
- `credentials`: Path to GCP credentials file
- `bigquery_dataset`: BigQuery dataset name
- `bigquery_tables`: Configuration for BigQuery tables

## Usage

```python
from GFAnalytics.main import GFAnalytics

# Initialize the framework with configuration
gf = GFAnalytics(config_path='config/config.yaml')

# Run the full pipeline
gf.run()

# Or run individual steps
gf.load_data()
gf.create_features()
gf.train_model()
gf.evaluate_model()
gf.predict_future()
gf.visualize_results()
``` 