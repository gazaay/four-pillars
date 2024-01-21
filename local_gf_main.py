from datetime import datetime, timedelta
from app  import bazi
import json
import pandas as pd
from app.chengseng import adding_8w_pillars, create_chengseng_for_dataset
import pytz




base_8w = bazi.get_heavenly_branch_ymdh_pillars_base(1969, 11, 24, 9)
print(base_8w)

base_8w = bazi.get_heavenly_branch_ymdh_pillars_current(1969, 11, 24, 9)
print(base_8w)

start_time = datetime.now(pytz.timezone('Asia/Shanghai'))

print(start_time)

sorted_df_with_new_features = pd.DataFrame()

end_time = start_time + timedelta(hours=8)

time_format = "%Y-%m-%dT%H:%M:%S"
time_elements = []

current_time = start_time
while current_time < end_time:
    time_elements.append(current_time.strftime(time_format))
    current_time += timedelta(hours=2)

print(time_elements)

time_string = time_elements[0]
time_format = "%Y-%m-%dT%H:%M:%S"
parsed_time = datetime.strptime(time_string, time_format)
# datetime.strptime(time_string, time_format)

# Extract the components
year = parsed_time.year
month = parsed_time.month
day = parsed_time.day
hour = parsed_time.hour

print(f" {year} - {month} - {day} - {hour} - {datetime.now()} - {sorted_df_with_new_features} Started processing")



sorted_df_with_new_features["time"] = time_elements

data_for_analytics = adding_8w_pillars(sorted_df_with_new_features)

end_time =  datetime.now(pytz.timezone('Asia/Shanghai'))
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time.total_seconds()} seconds")


data_for_analytics['本時'] = base_8w["時"]
data_for_analytics['本日'] = base_8w["日"]
data_for_analytics['-本時'] = base_8w["-時"]
data_for_analytics['本月'] = base_8w["月"]
data_for_analytics['本年'] = base_8w["年"]
data_for_analytics['-本月'] = base_8w["-月"]

print (data_for_analytics)

dataset_with_cs = create_chengseng_for_dataset(data_for_analytics)
print(dataset_with_cs.columns.tolist())
# # Example usage
# stem_branch = "甲亥"
# cheung_sheng = get_cheung_sheng(stem_branch)
# print(f"The Cheung Sheng for {stem_branch} is {cheung_sheng}")



# Assuming your DataFrame is named df
# Replace df with your actual DataFrame name if it's different

column_mapping = {
    '流時': 'current_hour',
    '流日': 'current_day',
    '-流時': 'negative_current_hour',
    '流月': 'current_month',
    '流年': 'current_year',
    '-流月': 'negative_current_month',
    '本時': 'base_hour',
    '本日': 'base_day',
    '-本時': 'negative_base_hour',
    '本月': 'base_month',
    '本年': 'base_year',
    '-本月': 'negative_base_month',
    '長_本時_流時': 'chengseng_base_hour_current_hour',
    '長_本時_流日': 'chengseng_base_hour_current_day',
    '長_本時_-流時': 'chengseng_base_hour_negative_current_hour',
    '長_本時_流月': 'chengseng_base_hour_current_month',
    '長_本時_流年': 'chengseng_base_hour_current_year',
    '長_本時_-流月': 'chengseng_base_hour_negative_current_month',
    '長_本日_流時': 'chengseng_base_day_current_hour',
    '長_本日_流日': 'chengseng_base_day_current_day',
    '長_本日_-流時': 'chengseng_base_day_negative_current_hour',
    '長_本日_流月': 'chengseng_base_day_current_month',
    '長_本日_流年': 'chengseng_base_day_current_year',
    '長_本日_-流月': 'chengseng_base_day_negative_current_month',
    '長_-本時_流時': 'chengseng_negative_base_hour_current_hour',
    '長_-本時_流日': 'chengseng_negative_base_hour_current_day',
    '長_-本時_-流時': 'chengseng_negative_base_hour_negative_current_hour',
    '長_-本時_流月': 'chengseng_negative_base_hour_current_month',
    '長_-本時_流年': 'chengseng_negative_base_hour_current_year',
    '長_-本時_-流月': 'chengseng_negative_base_hour_negative_current_month',
    '長_本月_流時': 'chengseng_base_month_current_hour',
    '長_本月_流日': 'chengseng_base_month_current_day',
    '長_本月_-流時': 'chengseng_base_month_negative_current_hour',
    '長_本月_流月': 'chengseng_base_month_current_month',
    '長_本月_流年': 'chengseng_base_month_current_year',
    '長_本月_-流月': 'chengseng_base_month_negative_current_month',
    '長_本年_流時': 'chengseng_base_year_current_hour',
    '長_本年_流日': 'chengseng_base_year_current_day',
    '長_本年_-流時': 'chengseng_base_year_negative_current_hour',
    '長_本年_流月': 'chengseng_base_year_current_month',
    '長_本年_流年': 'chengseng_base_year_current_year',
    '長_本年_-流月': 'chengseng_base_year_negative_current_month',
    '長_-本月_流時': 'chengseng_negative_base_month_current_hour',
    '長_-本月_流日': 'chengseng_negative_base_month_current_day',
    '長_-本月_-流時': 'chengseng_negative_base_month_negative_current_hour',
    '長_-本月_流月': 'chengseng_negative_base_month_current_month',
    '長_-本月_流年': 'chengseng_negative_base_month_current_year',
    '長_-本月_-流月': 'chengseng_negative_base_month_negative_current_month',
}

dataset_with_cs.rename(columns=column_mapping, inplace=True)

# Now, your DataFrame df has columns with the specified meanings incorporated into their names
print(dataset_with_cs)