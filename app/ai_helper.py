import pandas as pd
from sklearn.preprocessing import LabelEncoder
import datetime

label_encoders ={}

# Define your custom encoding mapping
custom_encoding_mapping = {
    "甲子": 1, "乙丑": 2, "丙寅": 3, "丁卯": 4, "戊辰": 5, "己巳": 6, "庚午": 7, "辛未": 8,
    "壬申": 9, "癸酉": 10, "甲戌": 11, "乙亥": 12, "丙子": 13, "丁丑": 14, "戊寅": 15, "己卯": 16,
    "庚辰": 17, "辛巳": 18, "壬午": 19, "癸未": 20, "甲申": 21, "乙酉": 22, "丙戌": 23, "丁亥": 24,
    "戊子": 25, "己丑": 26, "庚寅": 27, "辛卯": 28, "壬辰": 29, "癸巳": 30, "甲午": 31, "乙未": 32,
    "丙申": 33, "丁酉": 34, "戊戌": 35, "己亥": 36, "庚子": 37, "辛丑": 38, "壬寅": 39, "癸卯": 40,
    "甲辰": 41, "乙巳": 42, "丙午": 43, "丁未": 44, "戊申": 45, "己酉": 46, "庚戌": 47, "辛亥": 48,
    "壬子": 49, "癸丑": 50, "甲寅": 51, "乙卯": 52, "丙辰": 53, "丁巳": 54, "戊午": 55, "己未": 56,
    "庚申": 57, "辛酉": 58, "壬戌": 59, "癸亥": 60,
    "甲": 201, "乙": 202, "丙": 203, "丁": 204, "戊": 205,
    "己": 206, "庚": 207, "辛": 208, "壬": 209, "癸": 210,
    "傷官": -310, "七殺": -308, "劫財": -306, "比肩": -304,
    "食神": -302, "偏印": 302, "偏財": 304, "正財": 306,
    "正官": 308, "正印": 310,
    "長生": 402, "沐浴": -402, "冠帶": 406, "臨官": 408,
    "帝旺": 410, "衰": -404, "病": -406, "死": -410,
    "墓庫": -404, "絕": -408, "胎": 400, "養": 400,
    "子": 111, "丑": 112, "寅": 101, "卯": 102,
    "辰": 103, "巳": 104, "午": 105, "未": 106,
    "申": 107, "酉": 108, "戌": 109, "亥": 110
}


def process_encode_data(data_, categorical_features):
    data = data_.copy()
    for feature in categorical_features:
          try: 
            # Initialize the LabelEncoder with your custom mapping
            label_encoder = LabelEncoder()
            label_encoder.fit(list(custom_encoding_mapping.values()))
            encoded_values = None

            try:
              # Try to map the values using custom_encoding_mapping
              encoded_values = data[feature].map(custom_encoding_mapping)
            except Exception as e:
              print("An error occurred:", e)
            # Assuming 'data' is your DataFrame and 'feature' is the column containing the large numbers
            formatted_values = []

            # If value in feature could be int or float. We will add it there. if it is not, we will
            # add the raw value instead.
            for value in data[feature]:
              if isinstance(value, (int, float)):
                  formatted_values.append(f'{value:.0f}')
              else:
                  formatted_values.append(value)


            data[feature] = formatted_values


            # Convert the column to numeric with errors='coerce' to convert non-numeric to NaN
            numeric_data = pd.to_numeric(data[feature], errors='coerce')

            if numeric_data.isnull().any():
              # Check if any value is not found in the custom_encoding_mapping
              if encoded_values.isnull().any() :
                  # Fallback to using fit_transform
                  print(feature + " will fall back to use fit_transform")
                  data[feature] = label_encoder.fit_transform(data[feature])
              else:
                  # Use transform with your custom mapping to encode the data
                  data[feature] = label_encoder.transform(data[feature].map(custom_encoding_mapping))

              label_encoders[feature] = label_encoder
            else:
              print(f"Column {feature} doesn't need to encode")
              data[feature] = data[feature].astype(float)


            print(f"Unique values for {feature}: {data[feature].unique()}")
            #print(f"decode the value {label_encoders[feature].inverse_transform(data[feature])}")
          except Exception as e:
            print("An error occurred:", e)
            continue
    return data