# GFAnalytics Changelog

This file contains a chronological log of changes made to the GFAnalytics framework.

## [Unreleased]

### Added
- Comprehensive DataFrame logging functionality for debugging and analysis
- Integrated logging throughout prediction and future data generation pipeline
- Documentation folder structure for better organization of project documentation

## [0.2.0] - 2024-07-15

### Added
- DataFrame CSV logging utility (`csv_utils.py`) for exporting DataFrames to CSV files
- Configurable CSV logging options in the main config.yaml file
- Global logdf() function for easy DataFrame logging throughout the codebase
- Integration of DataFrame logging in the FutureDataGenerator and Predictor classes
- Detailed error logging for troubleshooting prediction issues
- Example script for demonstrating prediction with logging (prediction_logging_example.py)
- Unit tests for CSV logging utilities (test_csv_utils.py)

### Changed
- Updated main.py to use DataFrame logging at key pipeline stages
- Enhanced error handling in prediction pipeline with diagnostic logging
- Improved date handling in prediction module with more robust fallbacks

### Fixed
- Bug in Predictor class where date column might be missing
- Error handling in feature column identification

## [0.1.0] - 2024-07-01

### Added
- Initial version of GFAnalytics framework
- Stock data loading functionality
- Bazi data generation
- Feature transformations (Bazi and ChengShen)
- Random Forest model implementation
- Prediction pipeline
- Basic visualization tools
- BigQuery storage integration
- Google Drive model storage

## Version Numbering

GFAnalytics uses [Semantic Versioning](https://semver.org/):

- MAJOR version when making incompatible API changes
- MINOR version when adding functionality in a backwards compatible manner
- PATCH version when making backwards compatible bug fixes

## Changelog Format

This changelog is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). 