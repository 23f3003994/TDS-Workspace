import math

coverage_data = {
  "executed_lines": [4,5,6,8,9,10,11,12,13,14,17,39,42,43,44,45,48,49,50,53,54,55,56,57,58,60,62,63,64,66,67,70,71,72,73,74,82,84,85,86,87,89,90,91,94,96,97,101,102,104,107,108,112,113,114,115,118,119,120,121,124,125,126,128,130,131,134,135,137,138,139,140,142,143,145,146],
  "missing_lines": [1,7,16,18,21,22,24,25,26,27,30,31,32,33,34,37,38,40,41,46,47,65,69,77,78,79,83,88,92,93,95,98,99,100,103,109,127,129,132,133,136,144,147,148],
  "branches": {"[30, 34]": True,"[144, 147]": True,"[107, 112]": True,"[77, 82]": True,"[138, 143]": True,"[57, 62]": True,"[53, 58]": True,"[107, 109]": True,"[64, 65]": True,"[128, 133]": True,"[113, 117]": False,"[40, 41]": False,"[10, 11]": False,"[69, 73]": False,"[92, 94]": False,"[120, 124]": False,"[25, 29]": False,"[86, 90]": False,"[115, 117]": False,"[85, 88]": False},
  "total_statements": 120,
  "total_branches": 20
}

# ── 1. Line Coverage ──────────────────────────────────────────────
line_coverage_pct = len(coverage_data["executed_lines"]) / coverage_data["total_statements"] * 100

# ── 2. Branch Coverage ───────────────────────────────────────────
executed_branches = sum(1 for v in coverage_data["branches"].values() if v)
branch_coverage_pct = executed_branches / coverage_data["total_branches"] * 100

# ── 3 & 4. Group consecutive missing lines ───────────────────────
missing = sorted(coverage_data["missing_lines"])

groups = []
current_group = [missing[0]]

for line in missing[1:]:
    if line == current_group[-1] + 1:   # consecutive → extend group
        current_group.append(line)
    else:                                # gap found → start new group
        groups.append(current_group)
        current_group = [line]
groups.append(current_group)            # don't forget the last group

# Each group needs ceil(size / 5) test cases
missing_line_runs = sum(math.ceil(len(g) / 5) for g in groups)

# Largest group = critical missing
critical_missing = max(len(g) for g in groups)

# ── Print results ─────────────────────────────────────────────────
print(f"line_coverage_pct  : {line_coverage_pct:.2f}%")
print(f"branch_coverage_pct: {branch_coverage_pct:.2f}%")
print(f"missing_line_runs  : {missing_line_runs}")
print(f"critical_missing   : {critical_missing}")
print()
print("Answer:", f"{line_coverage_pct:.2f}, {branch_coverage_pct:.2f}, {missing_line_runs}, {critical_missing}")

# ── Show the groups (for understanding) ──────────────────────────
print("\nConsecutive missing-line groups:")
for i, g in enumerate(groups, 1):
    size = len(g)
    runs = math.ceil(size / 5)
    print(f"  Group {i:2d}: lines {g[0]:3d}–{g[-1]:3d}  size={size}  needs {runs} test run(s)")
