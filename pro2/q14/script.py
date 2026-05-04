#21 25 45 50
import json
from datetime import datetime

def parse_date(s):
    return datetime.fromisoformat(s.replace('Z','').split('+')[0])

CUTOFF = datetime(2026, 4, 25, 23, 59, 59)

def get_truly_solved(data):
    truly_solved = []
    for topic in data:
        accepted = [p for p in topic['posts'] if p['accepted_answer']]
        if accepted and parse_date(accepted[0]['created_at']) <= CUTOFF:
            truly_solved.append(topic)
    return truly_solved

def count_posts_in_range(truly_solved, start, end):
    count = 0
    for topic in truly_solved:
        for post in topic['posts']:
            d = parse_date(post['created_at'])
            if start <= d <= end:
                count += 1
    return count

# ================================================================
# TASK 21: mlp-kb total posts between 2025-01-01 and 2025-03-31
# ================================================================
with open('data/mlp-kb.json', 'r') as f:
    mlp_data = json.load(f)

mlp_solved = get_truly_solved(mlp_data)
print(f"mlp-kb total topics: {len(mlp_data)}")
print(f"mlp-kb truly solved: {len(mlp_solved)}")

task21 = count_posts_in_range(
    mlp_solved,
    datetime(2025, 1, 1),
    datetime(2025, 3, 31, 23, 59, 59)
)
print(f"\nTask 21 (mlp-kb posts Jan-Mar 2025): {task21}")

# ================================================================
# TASK 25: stats2-kb total posts between 2025-01-01 and 2025-06-30
# ================================================================
with open('data/stats2-kb.json', 'r') as f:
    stats2_data = json.load(f)

stats2_solved = get_truly_solved(stats2_data)
print(f"\nstats2-kb total topics: {len(stats2_data)}")
print(f"stats2-kb truly solved: {len(stats2_solved)}")

task25 = count_posts_in_range(
    stats2_solved,
    datetime(2025, 1, 1),
    datetime(2025, 6, 30, 23, 59, 59)
)
print(f"\nTask 25 (stats2-kb posts Jan-Jun 2025): {task25}")

# ================================================================
# TASK 45: mlf-kb total posts between 2025-01-01 and 2025-06-30
# ================================================================
with open('data/mlf-kb.json', 'r') as f:
    mlf_data = json.load(f)

mlf_solved = get_truly_solved(mlf_data)
print(f"\nmlf-kb total topics: {len(mlf_data)}")
print(f"mlf-kb truly solved: {len(mlf_solved)}")

task45 = count_posts_in_range(
    mlf_solved,
    datetime(2025, 1, 1),
    datetime(2025, 6, 30, 23, 59, 59)
)
print(f"\nTask 45 (mlf-kb posts Jan-Jun 2025): {task45}")

# ================================================================
# TASK 50: english2-kb total posts between 2025-01-01 and 2025-09-30
# ================================================================
with open('data/english2-kb.json', 'r') as f:
    eng_data = json.load(f)

eng_solved = get_truly_solved(eng_data)
print(f"\nenglish2-kb total topics: {len(eng_data)}")
print(f"english2-kb truly solved: {len(eng_solved)}")

task50 = count_posts_in_range(
    eng_solved,
    datetime(2025, 1, 1),
    datetime(2025, 9, 30, 23, 59, 59)
)
print(f"\nTask 50 (english2-kb posts Jan-Sep 2025): {task50}")

print("\n--- ALL ANSWERS ---")
print(f"task21: {task21}")
print(f"task25: {task25}")
print(f"task45: {task45}")
print(f"task50: {task50}")