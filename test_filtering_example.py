#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script to demonstrate column filtering functionality.
Run this script to see how the filtering works with different settings.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the GFAnalytics package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'GFAnalytics'))

from GFAnalytics.utils.data_utils import apply_column_filtering, prepare_feature_data

def create_sample_data():
    """Create sample data with various column types for testing."""
    np.random.seed(42)
    
    data = pd.DataFrame({
        # Time columns
        'time': pd.date_range('2023-01-01', periods=100, freq='D'),
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        
        # Stock data
        'Close': np.random.random(100) * 100 + 20000,
        'Open': np.random.random(100) * 100 + 20000,
        'Volume': np.random.randint(1000, 10000, 100),
        
        # Base pillars (stock listing date Bazi)
        'base_year_stem': np.random.choice(['甲', '乙', '丙', '丁', '戊'], 100),
        'base_year_branch': np.random.choice(['子', '丑', '寅', '卯', '辰'], 100),
        'base_month_stem': np.random.choice(['甲', '乙', '丙', '丁', '戊'], 100),
        'base_month_branch': np.random.choice(['子', '丑', '寅', '卯', '辰'], 100),
        'base_day_stem': np.random.choice(['甲', '乙', '丙', '丁', '戊'], 100),
        'base_day_branch': np.random.choice(['子', '丑', '寅', '卯', '辰'], 100),
        
        # Current pillars (time-specific Bazi)
        'current_year_stem': np.random.choice(['甲', '乙', '丙', '丁', '戊'], 100),
        'current_year_branch': np.random.choice(['子', '丑', '寅', '卯', '辰'], 100),
        'current_month_stem': np.random.choice(['甲', '乙', '丙', '丁', '戊'], 100),
        'current_month_branch': np.random.choice(['子', '丑', '寅', '卯', '辰'], 100),
        'current_day_stem': np.random.choice(['甲', '乙', '丙', '丁', '戊'], 100),
        'current_day_branch': np.random.choice(['子', '丑', '寅', '卯', '辰'], 100),
        'current_hour_stem': np.random.choice(['甲', '乙', '丙', '丁', '戊'], 100),
        'current_hour_branch': np.random.choice(['子', '丑', '寅', '卯', '辰'], 100),
        
        # ChengShen attributes
        'chengshen_year_生': np.random.randint(0, 2, 100),
        'chengshen_year_克': np.random.randint(0, 2, 100),
        'chengshen_month_生': np.random.randint(0, 2, 100),
        'chengshen_month_克': np.random.randint(0, 2, 100),
        'year_木生': np.random.randint(0, 2, 100),
        'month_火克': np.random.randint(0, 2, 100),
        
        # Other features
        'some_other_feature': np.random.random(100),
        
        # Target
        'target': np.random.random(100) * 1000 + 20000
    })
    
    return data

def test_no_filtering():
    """Test with filtering disabled."""
    print("=" * 60)
    print("TEST 1: No filtering (disabled)")
    print("=" * 60)
    
    config = {
        'model': {
            'features': {
                'filtering': {
                    'enabled': False
                }
            }
        }
    }
    
    data = create_sample_data()
    print(f"Original columns ({len(data.columns)}): {sorted(data.columns.tolist())}")
    
    filtered_data = apply_column_filtering(data, config)
    print(f"After filtering ({len(filtered_data.columns)}): {sorted(filtered_data.columns.tolist())}")
    
    return filtered_data

def test_base_pillars_filtering():
    """Test filtering base pillars only."""
    print("\n" + "=" * 60)
    print("TEST 2: Filter base pillars - keep only year and month")
    print("=" * 60)
    
    config = {
        'model': {
            'features': {
                'filtering': {
                    'enabled': True,
                    'base_pillars': {
                        'include_patterns': ['year', 'month'],  # Only keep year and month
                        'exclude_patterns': []
                    },
                    'current_pillars': {
                        'include_patterns': [],
                        'exclude_patterns': []
                    },
                    'chengshen': {
                        'include_patterns': [],
                        'exclude_patterns': []
                    },
                    'custom': {
                        'include_patterns': [],
                        'exclude_patterns': []
                    }
                }
            }
        }
    }
    
    data = create_sample_data()
    base_cols_before = [col for col in data.columns if col.startswith('base_')]
    print(f"Base pillar columns before: {base_cols_before}")
    
    filtered_data = apply_column_filtering(data, config)
    base_cols_after = [col for col in filtered_data.columns if col.startswith('base_')]
    print(f"Base pillar columns after: {base_cols_after}")
    
    return filtered_data

def test_chengshen_filtering():
    """Test filtering ChengShen attributes."""
    print("\n" + "=" * 60)
    print("TEST 3: Filter ChengShen - exclude all 克 relations")
    print("=" * 60)
    
    config = {
        'model': {
            'features': {
                'filtering': {
                    'enabled': True,
                    'base_pillars': {
                        'include_patterns': [],
                        'exclude_patterns': []
                    },
                    'current_pillars': {
                        'include_patterns': [],
                        'exclude_patterns': []
                    },
                    'chengshen': {
                        'include_patterns': [],
                        'exclude_patterns': ['克']  # Exclude all 克 relations
                    },
                    'custom': {
                        'include_patterns': [],
                        'exclude_patterns': []
                    }
                }
            }
        }
    }
    
    data = create_sample_data()
    cs_cols_before = [col for col in data.columns if any(keyword in col for keyword in ['chengshen', '生', '克'])]
    print(f"ChengShen columns before: {cs_cols_before}")
    
    filtered_data = apply_column_filtering(data, config)
    cs_cols_after = [col for col in filtered_data.columns if any(keyword in col for keyword in ['chengshen', '生', '克'])]
    print(f"ChengShen columns after: {cs_cols_after}")
    
    return filtered_data

def test_combined_filtering():
    """Test combined filtering with multiple rules."""
    print("\n" + "=" * 60)
    print("TEST 4: Combined filtering")
    print("=" * 60)
    
    config = {
        'model': {
            'features': {
                'filtering': {
                    'enabled': True,
                    'base_pillars': {
                        'include_patterns': ['day'],  # Only keep day pillars
                        'exclude_patterns': []
                    },
                    'current_pillars': {
                        'include_patterns': ['hour'],  # Only keep hour pillars
                        'exclude_patterns': []
                    },
                    'chengshen': {
                        'include_patterns': ['生'],  # Only keep 生 relations
                        'exclude_patterns': []
                    },
                    'custom': {
                        'include_patterns': [],
                        'exclude_patterns': ['some_other']  # Remove some_other_feature
                    }
                }
            }
        }
    }
    
    data = create_sample_data()
    
    print("Before filtering:")
    print(f"  Base pillars: {[col for col in data.columns if col.startswith('base_')]}")
    print(f"  Current pillars: {[col for col in data.columns if col.startswith('current_')]}")
    print(f"  ChengShen: {[col for col in data.columns if any(keyword in col for keyword in ['chengshen', '生', '克'])]}")
    print(f"  Other: {[col for col in data.columns if 'some_other' in col]}")
    
    filtered_data = apply_column_filtering(data, config)
    
    print("After filtering:")
    print(f"  Base pillars: {[col for col in filtered_data.columns if col.startswith('base_')]}")
    print(f"  Current pillars: {[col for col in filtered_data.columns if col.startswith('current_')]}")
    print(f"  ChengShen: {[col for col in filtered_data.columns if any(keyword in col for keyword in ['chengshen', '生', '克'])]}")
    print(f"  Other: {[col for col in filtered_data.columns if 'some_other' in col]}")
    
    return filtered_data

def test_with_prepare_feature_data():
    """Test the complete pipeline with prepare_feature_data."""
    print("\n" + "=" * 60)
    print("TEST 5: Complete pipeline with prepare_feature_data")
    print("=" * 60)
    
    config = {
        'model': {
            'features': {
                'filtering': {
                    'enabled': True,
                    'base_pillars': {
                        'include_patterns': ['day'],  # Only keep day pillars
                        'exclude_patterns': []
                    },
                    'current_pillars': {
                        'include_patterns': ['hour'],  # Only keep hour pillars  
                        'exclude_patterns': []
                    },
                    'chengshen': {
                        'include_patterns': ['生'],  # Only keep 生 relations
                        'exclude_patterns': []
                    },
                    'custom': {
                        'include_patterns': [],
                        'exclude_patterns': []
                    }
                }
            }
        }
    }
    
    data = create_sample_data()
    print(f"Original data shape: {data.shape}")
    print(f"Original columns: {sorted(data.columns.tolist())}")
    
    # Test training mode
    X_train, y_train = prepare_feature_data(data, is_training=True, config=config)
    print(f"Training features shape: {X_train.shape}")
    print(f"Training target shape: {y_train.shape}")
    print(f"Remaining columns: {sorted(X_train.columns.tolist())}")
    
    # Test prediction mode
    data_no_target = data.drop('target', axis=1)
    X_pred, y_pred = prepare_feature_data(data_no_target, is_training=False, config=config)
    print(f"Prediction features shape: {X_pred.shape}")
    print(f"Prediction target: {y_pred}")
    
    return X_train, y_train

if __name__ == "__main__":
    print("Column Filtering Demonstration")
    print("=" * 60)
    
    # Run all tests
    test_no_filtering()
    test_base_pillars_filtering()
    test_chengshen_filtering()
    test_combined_filtering()
    test_with_prepare_feature_data()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60) 