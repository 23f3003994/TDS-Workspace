#q-ranked-anomaly-detection
import pandas as pd
import re

# Load the CSV
df = pd.read_csv('q-ranked-anomaly-detection.csv')

# Step 1: Trim whitespace from all string columns
df.columns = [c.strip() for c in df.columns]
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].str.strip()

# Step 2: Extract numeric part from Observed Value, Range Min, Range Max
def extract_number(val):
    val = str(val).strip()
    match = re.match(r'[-+]?\d*\.?\d+', val)
    return float(match.group()) if match else None

df['value'] = df['Observed Value'].apply(extract_number)
df['rmin']  = df['Range Min'].apply(extract_number)
df['rmax']  = df['Range Max'].apply(extract_number)

# Step 3: Compute deviation fraction
def compute_deviation(row):
    v, mn, mx = row['value'], row['rmin'], row['rmax']
    if v is None or mn is None or mx is None:
        return 0.0
    if mn <= v <= mx:
        return 0.0  # normal
    span = mx - mn
    if span == 0:
        return 0.0
    nearest = mn if v < mn else mx
    return abs(v - nearest) / span

df['deviation'] = df.apply(compute_deviation, axis=1)

# Step 4: Classify severity
def classify(dev):
    if dev > 0.50:
        return 'S1'
    elif dev > 0.20:
        return 'S2'
    elif dev > 0:
        return 'S3'
    else:
        return 'Normal'

df['severity'] = df['deviation'].apply(classify)

print(df.head())

# Step 5: Filter out Normal rows
anomalies = df[df['severity'] != 'Normal'].copy()

# Step 6: Extract numeric Event ID
def extract_id(eid):
    match = re.search(r'\d+', str(eid))
    return int(match.group()) if match else None

anomalies['event_num'] = anomalies['Event ID'].apply(extract_id)


# Step 7: Sort — S1 first, then S2, then S3, within same severity by deviation descending
severity_order = {'S1': 0, 'S2': 1, 'S3': 2}
anomalies['sev_rank'] = anomalies['severity'].map(severity_order)
anomalies = anomalies.sort_values(
    by=['sev_rank', 'deviation'],
    ascending=[True, False]
)

print(anomalies.head())

# Step 8: Build and print the tuple list
result = [(row['event_num'], row['severity']) for _, row in anomalies.iterrows()]
print(result)