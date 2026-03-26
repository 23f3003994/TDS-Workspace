import pandas as pd

# ── 1. Load data ───────────────────────────────────────────────────────────────
train = pd.read_csv("train.csv")
test  = pd.read_csv("test.csv")

# ── 2. Define feature columns used for matching ────────────────────────────────
feature_cols = ["age", "income", "education", "hours_per_week"]

# ── 3. Find leaked rows via left merge with indicator ──────────────────────────
merged = test.merge(
    train[feature_cols].drop_duplicates(),   # unique train feature combos
    on=feature_cols,
    how="left",
    indicator=True                           # adds "_merge" column
)

# ── 4. Split into leaked vs clean ──────────────────────────────────────────────
leaked = merged[merged["_merge"] == "both"]
clean  = merged[merged["_merge"] == "left_only"]

# ── 5. Compute metrics ─────────────────────────────────────────────────────────
leaked_count    = len(leaked)
leaked_accuracy = leaked["is_correct"].mean() * 100
clean_accuracy  = clean["is_correct"].mean()  * 100
reported        = 75.67
inflation_pp    = reported - clean_accuracy

# ── 6. Print detailed report ───────────────────────────────────────────────────
print("=" * 50)
print("   TRAIN-TEST CONTAMINATION REPORT")
print("=" * 50)
print(f"  Total test rows       : {len(test)}")
print(f"  Leaked rows           : {leaked_count}")
print(f"  Clean rows            : {len(clean)}")
print("-" * 50)
print(f"  Leaked accuracy       : {leaked_accuracy:.2f}%")
print(f"  Clean accuracy        : {clean_accuracy:.2f}%")
print(f"  Reported accuracy     : {reported:.2f}%")
print(f"  Inflation             : {inflation_pp:.2f} pp")
print("=" * 50)

# ── 7. Final answer ────────────────────────────────────────────────────────────
print("\n✅ FINAL ANSWER:")
print(f"{leaked_count}, {leaked_accuracy:.2f}, {clean_accuracy:.2f}, {inflation_pp:.2f}")