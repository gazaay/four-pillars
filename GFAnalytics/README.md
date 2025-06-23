# GFAnalytics Framework

A machine learning framework for predicting stock market or indices pricing using Bazi (Chinese metaphysics) attributes.

## Overview

GFAnalytics uses machine learning algorithms to predict stock market movements by combining traditional financial data with Bazi (八字) attributes. The framework transforms time-based Bazi pillars into ChengShen (長生) attributes for training, creating a unique approach to market prediction.
# GFAnalytics - Stock Market Prediction with Traditional Chinese Metaphysics

GFAnalytics is an innovative stock market analysis and prediction framework that combines modern machine learning techniques with traditional Chinese metaphysical concepts, specifically **Bazi (Four Pillars of Destiny)** and **ChengShen** transformations.

## 🌟 What Makes GFAnalytics Unique

Unlike traditional technical analysis tools, GFAnalytics integrates:

- **Traditional Stock Analysis**: Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- **Bazi (四柱八字)**: Chinese astrological system based on birth pillars
- **ChengShen (乘神)**: Traditional Chinese metaphysical relationships
- **Wuxi (五行)**: Five Elements theory integration
- **Modern ML**: Random Forest and other machine learning algorithms

## 🚀 Key Features

### Core Functionality
- **Multi-Source Data Integration**: Combines stock market data with metaphysical attributes
- **Advanced Feature Engineering**: Automatic encoding of categorical features and creation of derived indicators
- **Machine Learning Models**: Random Forest regression with hyperparameter tuning
- **Future Prediction**: Generate predictions for specified time periods ahead
- **Comprehensive Evaluation**: Multiple metrics (MSE, RMSE, R², MedAE) and feature importance analysis

### Data Management
- **Google Cloud Integration**: BigQuery for data storage, Google Drive for model persistence
- **Batch Processing**: Track and manage analysis runs with unique identifiers
- **Comprehensive Logging**: Detailed CSV logs for every step of the analysis pipeline
- **Run Management**: List, view, and manage historical analysis runs

### Visualization & Analysis
- **Interactive Plots**: Prediction charts, feature importance, correlation heatmaps
- **Bazi Visualizations**: Specialized charts for metaphysical analysis
- **Export Capabilities**: Save plots and analysis results

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Google Cloud Platform account (for BigQuery and Drive integration)
- GCP service account credentials

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/four-pillars.git
   cd four-pillars/GFAnalytics
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure GCP credentials**:
   - Download your service account JSON key from Google Cloud Console
   - Place it in the `GFAnalytics` directory
   - Update the `credentials_path` in `config/config.yaml`

4. **Update configuration**:
   - Edit `config/config.yaml` with your stock preferences, date ranges, and GCP settings

## 📖 Configuration

The main configuration file is `config/config.yaml`. Key sections include:

```yaml
# Stock Configuration
stock:
  code: "HSI"  # Stock or index code
  ric_code: "^HSI"  # Reuters code
  listing_date: "1969-11-24 09:30:00"

# Analysis Periods
date_range:
  training:
    start_date: "2023-11-01"
    end_date: "2024-12-31"
  prediction:
    days_ahead: 90

# Model Configuration
model:
  type: "random_forest"
  features:
    use_bazi: true
    use_chengshen: true
    use_technical_indicators: true
```

## 🚀 Usage

### Basic Analysis
```bash
# Run complete analysis pipeline
python -m GFAnalytics.main

# Run with plots displayed at the end
python -m GFAnalytics.main --show-plots
```

### Run Management
```bash
# List all previous runs
python -m GFAnalytics.main --list-runs

# View logs for a specific run
python -m GFAnalytics.main --run-logs YYYYMMDD_HHMMSS_uuid
```

### Data Management
```bash
# Clean all tables
python -m GFAnalytics.main --clean-tables

# Clean specific table
python -m GFAnalytics.main --clean-table stock_data
```

### Programmatic Usage
```python
from GFAnalytics.main import GFAnalytics

# Initialize the framework
analyzer = GFAnalytics('config/config.yaml')

# Run complete analysis
results = analyzer.run()

# Access results
print(f"R² Score: {results['evaluation_results']['R2']}")
print(f"Predictions: {results['predictions']}")
print(f"Run ID: {results['run_id']}")
```

### Command-Line Arguments Reference

| Argument | Description |
|----------|-------------|
| `--clean` | Clean all BigQuery tables |
| `--clean-table <name>` | Clean a specific BigQuery table |
| `--show-plots` | Display plots during pipeline execution |
| `--display-plots` | Only display previously generated plots |
| `--list-runs` | List all available runs with timestamps and log counts |
| `--run-logs <run_id>` | Show detailed logs for a specific run ID |

## Pipeline Overview

When you run the complete pipeline (`python -m GFAnalytics.main`), the framework executes these steps:

1. **Data Loading**: Load stock data and generate Bazi attributes
2. **Feature Creation**: Transform Bazi data to ChengShen features
3. **Model Training**: Train a Random Forest model
4. **Model Evaluation**: Evaluate performance with various metrics
5. **Future Prediction**: Generate predictions for future dates
6. **Visualization**: Create comprehensive plots and charts

## Output and Logging

Each run generates:
- **Unique Run ID**: For tracking and reference (format: YYYYMMDD_HHMMSS_uuid)
- **CSV Logs**: Stored in `csv_logs/<run_id>/` directory
- **BigQuery Tables**: Data stored in configured BigQuery dataset
- **Model Files**: Saved to Google Drive and local backup
- **Visualization Plots**: Generated and optionally displayed

### Example Output

```
Starting new run with ID: 20241215_143022_a1b2c3d4
📊 Loading data...
🔮 Creating Bazi features...
🤖 Training model...
📈 Evaluating model performance...
🔮 Generating future predictions...
📊 Creating visualizations...

=== Analysis Complete ===
Run ID: 20241215_143022_a1b2c3d4
R² Score: 0.8542
RMSE: 156.23
Feature Count: 45
Predictions Generated: 90 days ahead
CSV Logs: csv_logs/20241215_143022_a1b2c3d4/
```

## 📊 Analysis Pipeline

1. **Data Loading**: Fetch stock data from configured sources
2. **Bazi Generation**: Create Four Pillars attributes for each timestamp
3. **Feature Engineering**: Apply ChengShen transformations and technical indicators
4. **Encoding**: Convert categorical features to numerical representations
5. **Model Training**: Train Random Forest with hyperparameter optimization
6. **Evaluation**: Calculate performance metrics and feature importance
7. **Future Prediction**: Generate predictions for specified future periods
8. **Visualization**: Create comprehensive analysis charts
9. **Storage**: Save results to BigQuery and generate detailed logs

## 🗂️ Project Structure

```
GFAnalytics/
├── GFAnalytics/
│   ├── config/           # Configuration files
│   ├── data/            # Data loading and storage modules
│   ├── features/        # Feature engineering (Bazi, ChengShen)
│   ├── models/          # Machine learning models
│   ├── prediction/      # Future data generation and prediction
│   ├── utils/           # Utility functions (encoding, logging, etc.)
│   ├── visualization/   # Plotting and visualization
│   └── main.py         # Main application entry point
├── tests/              # Unit tests
├── docs/               # Documentation
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_encoding_utils.py
python -m pytest tests/test_csv_utils.py
```

## 📈 Understanding the Output

### Evaluation Metrics
- **R² Score**: Coefficient of determination (closer to 1.0 is better)
- **RMSE**: Root Mean Square Error (lower is better)
- **MSE**: Mean Squared Error (lower is better)
- **MedAE**: Median Absolute Error (lower is better)

### Feature Importance
The framework analyzes which features contribute most to predictions:
- **Technical Indicators**: Traditional market indicators
- **Bazi Features**: Metaphysical attributes based on time and date
- **ChengShen Relations**: Interactions between base and current pillars

### Visualization Outputs
- **Prediction Charts**: Historical data with future predictions
- **Feature Importance**: Bar charts showing most influential features
- **Correlation Heatmaps**: Feature relationships and correlations

## 🔧 Advanced Features

### Custom Encoders
The framework includes sophisticated encoding utilities for handling categorical metaphysical data:
- Automatic categorical column detection
- Label encoding with missing value handling
- Encoder persistence for consistent predictions

### Logging System
Comprehensive logging tracks every step:
- **CSV Logs**: Detailed data at each pipeline stage
- **Run IDs**: Unique identifiers for each analysis run
- **Error Tracking**: Detailed error logs for debugging

### Batch Processing
Track and manage multiple analysis runs:
- Batch creation with metadata
- Status tracking (in_progress, completed, failed)
- Parameter storage for reproducibility

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Stock market predictions involve significant risk, and this tool should not be used as the sole basis for investment decisions. The integration of metaphysical concepts is experimental and should be approached with appropriate skepticism.

## 🙏 Acknowledgments

- Traditional Chinese metaphysical practitioners for the foundational concepts
- The scikit-learn community for excellent machine learning tools
- Google Cloud Platform for reliable data infrastructure
- The open-source Python community for the extensive libraries used

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Review the documentation in the `docs/` folder
- Check the test files for usage examples

---

**GFAnalytics** - Where ancient wisdom meets modern technology for stock market analysis.

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



## Troubleshooting

### Common Issues

1. **GCP Credentials**: Ensure your Google Cloud credentials are properly configured
2. **BigQuery Access**: Verify you have the necessary permissions for BigQuery operations
3. **Dependencies**: Make sure all required Python packages are installed
4. **Configuration**: Check that your `config.yaml` file is properly formatted

### Getting Help

For detailed logging information, check:
- Console output during execution
- Log files in the `csv_logs/<run_id>/` directory
- BigQuery tables for stored data

## API Usage

You can also use GFAnalytics programmatically:



### Command-Line Arguments Reference

| Argument | Description |
|----------|-------------|
| `--clean` | Clean all BigQuery tables |
| `--clean-table <name>` | Clean a specific BigQuery table |
| `--show-plots` | Display plots during pipeline execution |
| `--display-plots` | Only display previously generated plots |
| `--list-runs` | List all available runs with timestamps and log counts |
| `--run-logs <run_id>` | Show detailed logs for a specific run ID |

## Pipeline Overview

When you run the complete pipeline (`python main.py`), the framework executes these steps:

1. **Data Loading**: Load stock data and generate Bazi attributes
2. **Feature Creation**: Transform Bazi data to ChengShen features
3. **Model Training**: Train a Random Forest model
4. **Model Evaluation**: Evaluate performance with various metrics
5. **Future Prediction**: Generate predictions for future dates
6. **Visualization**: Create comprehensive plots and charts

## Output and Logging

Each run generates:
- **Unique Run ID**: For tracking and reference
- **CSV Logs**: Stored in `csv_logs/<run_id>/` directory
- **BigQuery Tables**: Data stored in configured BigQuery dataset
- **Model Files**: Saved to Google Drive
- **Visualization Plots**: Generated and optionally displayed

### Example Output

## Run Management Examples

### Listing Previous Runs

bash
$ python main.py --list-runs
Found 3 runs:
run_id timestamp_str logs_count
20241201_143022_abc123 2024-12-01 14:30:22 8
20241130_091545_def456 2024-11-30 09:15:45 7
20241129_165432_ghi789 2024-11-29 16:54:32 6


### Viewing Run Logs

bash
$ python main.py --run-logs "20241201_143022_abc123"
Found 8 logs for run ID: 20241201_143022_abc123
filename size_kb modified_time_str
stock_data.csv 45.2 2024-12-01 14:30:25
bazi_data.csv 123.7 2024-12-01 14:30:28
training_data.csv 234.1 2024-12-01 14:30:35
predictions.csv 12.3 2024-12-01 14:30:42



## Troubleshooting

### Common Issues

1. **GCP Credentials**: Ensure your Google Cloud credentials are properly configured
2. **BigQuery Access**: Verify you have the necessary permissions for BigQuery operations
3. **Dependencies**: Make sure all required Python packages are installed
4. **Configuration**: Check that your `config.yaml` file is properly formatted

### Getting Help

For detailed logging information, check:
- Console output during execution
- Log files in the `csv_logs/<run_id>/` directory
- BigQuery tables for stored data

## API Usage

You can also use GFAnalytics programmatically:
