# 1. get stock birthday with finance.get_listing_date_timestamp
# 2. get stock 8w with bazi.get_heavenly_branch_ymdh_pillars_base to base_8w
# 3. Define a time range star date today minus 725 days, end date today
# 4. create a blank data frame, create a "time" column where each element are incremented by 2hours with the time range and add future 12 months
# 5. use adding_8w_pillars to add pillars in and put base_8w into the dataset
# 6. reusing the timerange - get stock history data with finance.get_historical_data_UTC(hong_kong_stocks[0], start_date=(current day minus 725 days), end_date=(current day), interval='1h')
# 7. merge the history data with the dataset where time is the key. 
# 7. get stock chengseng with create_chengseng_for_dataset
# 8. feature engineering
# 9. split data sets for random forest training
# 10. train random forest
# 11. predict with random forest model with the future 12 months

import pandas as pd
from datetime import datetime, timedelta
from app  import  finance  # Assume you have finance module with functions like get_listing_date_timestamp and get_historical_data_UTC
from app  import bazi # Assume you have bazi module with functions like get_heavenly_branch_ymdh_pillars_base, adding_8w_pillars, create_chengseng_for_dataset
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from app.chengseng import adding_8w_pillars, create_chengseng_for_dataset

# Step 1: Get stock birthday
symbol = '00001'  # Replace with your stock symbol
stock_birthday_timestamp = finance.get_listing_date_timestamp(symbol)

# Step 2: Get stock 8w
base_8w = bazi.get_heavenly_branch_ymdh_pillars_base(stock_birthday_timestamp.year, 
                                                            stock_birthday_timestamp.month, 
                                                            stock_birthday_timestamp.day, 
                                                            stock_birthday_timestamp.hour)

# Step 3: Define time range
today = datetime.now()
start_date = today - timedelta(days=725)
end_date = today

# Step 4: Create a blank data frame with time column
time_range = pd.date_range(start=start_date, end=end_date, freq='2H').union(pd.date_range(end_date, end_date + pd.DateOffset(months=12), freq='D'))
dataset = pd.DataFrame({'time': time_range})

# Step 5: Adding 8w pillars to the dataset
dataset = adding_8w_pillars(dataset)

symbol_code = "0001.hk"
# Step 6: Get stock history data
historical_data = finance.get_historical_data_UTC(symbol_code, start_date=start_date, end_date=end_date, interval='1h')

# Step 7: Merge history data with the dataset
dataset = pd.merge(dataset, historical_data, left_on='time', right_index=True, how='left')

# Step 7 (cont.): Get stock chengseng and merge with the dataset
chengseng_data = create_chengseng_for_dataset(dataset, symbol)
dataset = pd.merge(dataset, chengseng_data, on='time', how='left')

# Step 8: Feature engineering (assuming you have additional features to engineer)

# Step 9: Split datasets for random forest training
features = dataset.drop(['time', 'label'], axis=1)  # Adjust based on your actual features
labels = dataset['label']  # Adjust based on your actual labels

X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Step 10: Train random forest
rf_model = RandomForestClassifier()
rf_model.fit(X_train, y_train)

# Step 11: Predict with the future 12 months
future_features = pd.DataFrame({'time': pd.date_range(end_date, end_date + pd.DateOffset(months=12), freq='D')})
future_features = bazi.adding_8w_pillars(future_features, base_8w)  # Assuming this function works for future features

# Add any additional feature engineering steps if needed

# Make predictions
future_predictions = rf_model.predict(future_features.drop('time', axis=1))

# Combine predictions with the future_features dataframe
future_features['prediction'] = future_predictions

# Display the predictions for the future 12 months
print("Predictions for the Future 12 Months:")
print(future_features[['time', 'prediction']])
