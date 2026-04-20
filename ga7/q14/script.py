import csv
import math

# Instance catalogue
instances = [
    ('A', 2,  4,  0.05),
    ('B', 4,  8,  0.10),
    ('C', 8,  16, 0.20),
]

BASE_LATENCY = 50

# Load and parse the CSV
requests = []
with open('q-deployment-cost-analysis.csv', 'r') as f:
    reader = csv.DictReader(f)
    # Strip whitespace from headers
    reader.fieldnames = [h.strip() for h in reader.fieldnames]
    for row in reader:
        cpu       = float(row['CPU Required (cores)'].strip())
        ram       = float(row['RAM Required (GB)'].strip())
        threshold = float(row['Latency Threshold (ms)'].strip())
        requests.append((cpu, ram, threshold))

print(f"Loaded {len(requests)} requests")

# Check each instance type
viable = []
for name, vcpu, inst_ram, cost in instances:
    passes_all = True
    for i, (cpu, ram, threshold) in enumerate(requests):
        combined = cpu / vcpu + ram / inst_ram
        latency  = BASE_LATENCY * max(1, combined)
        if latency > threshold + 0.0001:  # tiny tolerance for float errors
            print(f"  Instance {name} FAILS request {i+1}: "
                  f"latency={latency:.4f}ms threshold={threshold}ms")
            passes_all = False
            break
    if passes_all:
        print(f"Instance {name} PASSES all requests — cost ${cost}/hr")
        viable.append((name, cost))

# Pick cheapest viable
if viable:
    viable.sort(key=lambda x: x[1])
    cheapest = viable[0]
    print(f"\nAnswer: {cheapest}")
else:
    print("No viable instance found.")