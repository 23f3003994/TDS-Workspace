import pandas as pd

df = pd.read_csv('q-poisoned-document-detection.csv')

# Trim whitespace from column names and text columns
df.columns = [c.strip() for c in df.columns]
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].str.strip()

# Parse the two columns you need as integers
df['Relevance Score'] = pd.to_numeric(df['Relevance Score'], errors='coerce')
df['Error Flag'] = pd.to_numeric(df['Error Flag'], errors='coerce')

# Apply selection rule
def classify(row):
    if row['Relevance Score'] >= 50 and row['Error Flag'] == 0:
        return 'I'
    else:
        return 'E'

df['label'] = df.apply(classify, axis=1)

# Extract numeric Doc ID
import re
def extract_id(doc_id):
    match = re.search(r'\d+', str(doc_id))
    return int(match.group()) if match else None

df['doc_num'] = df['Doc ID'].apply(extract_id)

# Sort: I before E, then by Relevance Score descending
df['label_rank'] = df['label'].map({'I': 0, 'E': 1})
df = df.sort_values(
    by=['label_rank', 'Relevance Score'],
    ascending=[True, False]
)

# Print result
result = [(row['doc_num'], row['label']) for _, row in df.iterrows()]
print(result)