import pandas as pd
import numpy as np

# ── Load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv("records.csv")

def preprocess(df, monotone_col):
    result = df.copy()
    for col in result.select_dtypes(include="number").columns:
        result[col] = result[col].rank(method="average", na_option="keep")
        n = result[col].count()
        if n > 0:
            result[col] = result[col] / n
    return result

# ── Run function once and twice ────────────────────────────────────────────────
result1 = preprocess(df, "score")
result2 = preprocess(result1, "score")

numeric_cols = result1.select_dtypes(include="number").columns

# ── 1. IDEMPOTENCY ─────────────────────────────────────────────────────────────
idempotency_violations = 0
for i in result1.index:
    for col in numeric_cols:
        a = result1.loc[i, col]
        b = result2.loc[i, col]
        if pd.isna(a) and pd.isna(b):
            continue
        elif pd.isna(a) or pd.isna(b):
            idempotency_violations += 1
            break                        # count row once
        elif abs(a - b) > 1e-9:
            idempotency_violations += 1
            break

# ── 2. MONOTONICITY ────────────────────────────────────────────────────────────
monotonicity_violations = 0
orig  = df["score"].reset_index(drop=True)
proc  = result1["score"].reset_index(drop=True)
n     = len(df)

for i in range(n):
    for j in range(n):
        oi, oj = orig.iloc[i], orig.iloc[j]
        if pd.isna(oi) or pd.isna(oj):
            continue
        if oi > oj:                      # strictly greater in original
            pi, pj = proc.iloc[i], proc.iloc[j]
            if not (pi > pj):            # must still be greater after
                monotonicity_violations += 1

# ── 3. NULL STABILITY ──────────────────────────────────────────────────────────
null_stability_violations = 0
for i in df.index:
    if df.loc[i].isna().sum() == 0:          # no nulls going in
        if result1.loc[i].isna().sum() > 0:  # nulls appeared going out
            null_stability_violations += 1

# ── Results ────────────────────────────────────────────────────────────────────
print("=" * 45)
print("   IDEMPOTENCY PROBER RESULTS")
print("=" * 45)
print(f"  Idempotency violations  : {idempotency_violations}")
print(f"  Monotonicity violations : {monotonicity_violations}")
print(f"  Null stability violations: {null_stability_violations}")
print("=" * 45)
print(f"\n✅ ANSWER: {idempotency_violations}, {monotonicity_violations}, {null_stability_violations}")