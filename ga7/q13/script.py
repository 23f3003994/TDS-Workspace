import pandas as pd
import re

# Load file
#df = pd.read_excel('your_file.xlsx')
df = pd.read_csv('q-chart-error-detection.csv')

# Trim column names
df.columns = [c.strip() for c in df.columns]

# Trim all text cells
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].str.strip()

# Parse numeric columns
df['Error Score']      = pd.to_numeric(df['Error Score'],      errors='coerce')
df['Visibility Score'] = pd.to_numeric(df['Visibility Score'], errors='coerce')
df['Is Error']         = pd.to_numeric(df['Is Error'],         errors='coerce')

# Filter: keep only genuine errors
real = df[df['Is Error'] == 1].copy()

# Classify severity
def classify(row):
    score = row['Error Score']
    if score >= 80:
        return 'S1'
    elif score >= 50:
        return 'S2'
    else:
        return 'S3'

real['severity'] = real.apply(classify, axis=1)

# Extract numeric Issue ID
def extract_id(issue_id):
    match = re.search(r'\d+', str(issue_id))
    return int(match.group()) if match else None

real['issue_num'] = real['Issue ID'].apply(extract_id)

# Sort
severity_order = {'S1': 0, 'S2': 1, 'S3': 2}
real['sev_rank'] = real['severity'].map(severity_order)

real = real.sort_values(
    by=['sev_rank', 'Error Score', 'Visibility Score'],
    ascending=[True, False, False]
)

# Print result
result = [(row['issue_num'], row['severity']) for _, row in real.iterrows()]
print(result)