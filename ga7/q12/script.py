import pandas as pd
import re

# Load file — use read_excel if still .xlsx
df = pd.read_csv('q-flaw-priority-ranking.csv')

# Trim whitespace from column names and all text cells
df.columns = [c.strip() for c in df.columns]
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].str.strip()

# Parse numeric columns
df['Impact Score']    = pd.to_numeric(df['Impact Score'],    errors='coerce')
df['Frequency Score'] = pd.to_numeric(df['Frequency Score'], errors='coerce')
df['Is Real']         = pd.to_numeric(df['Is Real'],         errors='coerce')

# Keep only real flaws
real = df[df['Is Real'] == 1].copy()

# Apply severity rules — S1 checked first to avoid misclassification
def classify(row):
    impact = row['Impact Score']
    freq   = row['Frequency Score']
    if impact >= 80 or (impact >= 70 and freq >= 70):
        return 'S1'
    elif 50 <= impact <= 79:
        return 'S2'
    else:
        return 'S3'

real['severity'] = real.apply(classify, axis=1)

# Extract numeric Issue ID
def extract_id(issue_id):
    match = re.search(r'\d+', str(issue_id))
    return int(match.group()) if match else None

real['issue_num'] = real['Issue ID'].apply(extract_id)

# Sort: S1 → S2 → S3, then Impact desc, then Frequency desc
severity_order = {'S1': 0, 'S2': 1, 'S3': 2}
real['sev_rank'] = real['severity'].map(severity_order)

real = real.sort_values(
    by=['sev_rank', 'Impact Score', 'Frequency Score'],
    ascending=[True, False, False]
)

# Print result
result = [(row['issue_num'], row['severity']) for _, row in real.iterrows()]
print(result)