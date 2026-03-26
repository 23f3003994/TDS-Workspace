import pandas as pd
import numpy as np
from datetime import datetime

# Load data
day1 = pd.read_csv('day1.csv')
day2 = pd.read_csv('day2.csv')

bad_rows = set()  # Store anomalous row indices

# Analyze each column
for col in day1.columns:
    print(f"\nColumn: {col}")
    
    # RULE 1: Null check
    if day1[col].isnull().sum() == 0:  # No nulls in Day 1
        null_rows = day2[day2[col].isnull()].index
        if len(null_rows) > 0:
            print(f"  ✗ Rule 1: {len(null_rows)} rows with null values")
            bad_rows.update(null_rows)
    #here dont put continue    
    
    # RULE 2: Numeric check (>95%)
    day1_numeric = pd.to_numeric(day1[col], errors='coerce')
    # print(day1_numeric)
#     Column: account_balance
# 0      7414.89
# 1      9744.53
# 2       349.23
# 3      8024.19
# 4      7372.04

    numeric_pct = day1_numeric.notna().sum() / len(day1)
    
    if numeric_pct > 0.95:
        day1_min = day1_numeric.min()
        day1_max = day1_numeric.max()
        day2_numeric = pd.to_numeric(day2[col], errors='coerce')
        
        out_of_range = day2[
            (day2_numeric < day1_min) | (day2_numeric > day1_max)
        ].index
        
        if len(out_of_range) > 0:
            print(f"  ✗ Rule 2: {len(out_of_range)} rows outside range [{day1_min}, {day1_max}]")
            bad_rows.update(out_of_range)
        continue # Don't check as date or categorical 
    
    # RULE 3: Date check (>90%)
    day1_dates = pd.to_datetime(day1[col],format='%Y-%m-%d', errors='coerce')
    date_pct = day1_dates.notna().sum() / len(day1)
    
    if date_pct > 0.90:
        day2_dates = pd.to_datetime(day2[col], errors='coerce')
        today = pd.Timestamp.now()
        future_rows = day2[day2_dates > today].index
        
        if len(future_rows) > 0:
            print(f"  ✗ Rule 3: {len(future_rows)} rows with future dates")
            bad_rows.update(future_rows)
        continue # Don't check categorical
    
    # RULE 4: Categorical check (≤20 distinct)
    unique_count = day1[col].nunique()
    
    if unique_count <= 20:
        allowed = set(day1[col].dropna().unique())
        day2_values = set(day2[col].dropna().unique())
        new_vals = day2_values - allowed
        
        if len(new_vals) > 0:
            print(f"  ✗ Rule 4: New categorical values: {new_vals}")
            new_val_rows = day2[day2[col].isin(new_vals)].index
            bad_rows.update(new_val_rows)

# ANSWER
print(f"\n{'='*50}")
print(f"TOTAL ANOMALOUS ROWS: {len(bad_rows)}")
print(f"{'='*50}")
print(len(bad_rows))

