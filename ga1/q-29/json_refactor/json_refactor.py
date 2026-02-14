import pandas as pd
import json

# Read JSON
with open('data.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)
# print(df.head())
# print(df.columns)
# print(type(df.columns)) #index type

# print(df.values)
# print(type(df.values)) #numpy array

# Create columnar format
result = {
    'columns': df.columns.tolist(),
    'rows': df.values.tolist()
}
# print(result)

# Save
with open('refactored.json', 'w') as f:
    json.dump(result, f, indent=2)