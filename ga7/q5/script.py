import pandas as pd
import numpy as np

df=pd.read_csv('data.csv')

print(df.groupby('category')['session_duration_min'].median().sort_values(ascending=False).head(10).round(2))


# category
# Books       14.04
# Beauty      13.46
# Health      13.29
# Toys        11.82
# Garden      10.43
# Outdoors     9.87
# Office       9.41
# Travel       9.31
# Gaming       9.22
# Apparel      9.14
# Name: session_duration_min, dtype: float64