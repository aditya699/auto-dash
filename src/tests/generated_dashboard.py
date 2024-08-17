import numpy as np
import pandas as pd

data=pd.read_csv("C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv")

data_dtypes = data.dtypes
column_descriptions = "\n".join([f"- {col}: {dtype}" for col, dtype in data_dtypes.items()])

print(column_descriptions)