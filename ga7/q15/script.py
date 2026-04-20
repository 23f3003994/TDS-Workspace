import csv
import math

rows_data = []

with open('q-latency-spike-detection.csv', 'r') as f:
    reader = csv.DictReader(f)
    # Strip whitespace from column headers
    reader.fieldnames = [h.strip() for h in reader.fieldnames]
    for row in reader:
        row_num    = int(row['Row'].strip())
        latency    = float(row['Latency (ms)'].strip())
        cpu_util   = float(row['CPU Util (%)'].strip())
        ram_util   = float(row['RAM Util (%)'].strip())
        rows_data.append((row_num, latency, cpu_util, ram_util))

# Step 1 — Compute mean and population std over all 60 latency values
latencies = [r[1] for r in rows_data]
n         = len(latencies)
mean      = sum(latencies) / n
variance  = sum((v - mean) ** 2 for v in latencies) / n  # divide by N
std       = math.sqrt(variance)
threshold = mean + 2 * std

print(f"N        : {n}")
print(f"Mean     : {mean:.4f} ms")
print(f"Std (pop): {std:.4f} ms")
print(f"Threshold: {threshold:.4f} ms")
print()

# Step 2 — Detect spikes and apply scaling decision
results = []
for row_num, latency, cpu_util, ram_util in rows_data:
    if latency > threshold:
        action = 'SCALE_UP' if max(cpu_util, ram_util) >= 80 else 'MONITOR'
        results.append((row_num, action))
        print(f"  Row {row_num:2d}: latency={latency}ms  "
              f"CPU={cpu_util}%  RAM={ram_util}%  "
              f"max_util={max(cpu_util,ram_util)}%  → {action}")

# Step 3 — Sort by Row number ascending
results.sort(key=lambda x: x[0])

print()
print("Answer:", results)