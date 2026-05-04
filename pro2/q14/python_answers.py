# import json
# from datetime import datetime
# from collections import defaultdict

# def parse_date(s):
#     return datetime.fromisoformat(s.replace('Z','').split('+')[0])

# CUTOFF = datetime(2026, 4, 25, 23, 59, 59)

# with open('data/python-kb.json', 'r') as f:
#     data = json.load(f)

# print(f"Total topics: {len(data)}")

# # Filter to truly solved topics (accepted answer post before cutoff)
# truly_solved = []
# for topic in data:
#     accepted_posts = [p for p in topic['posts'] if p['accepted_answer']]
#     if not accepted_posts:
#         continue
#     accepted_date = parse_date(accepted_posts[0]['created_at'])
#     if accepted_date <= CUTOFF:
#         truly_solved.append(topic)

# print(f"Truly solved (accepted before cutoff): {len(truly_solved)}")

# # ================================================================
# # TASK 14: unique creators — solved topics created Jul-Dec 2025
# # ================================================================
# t14_start = datetime(2025, 7, 1)
# t14_end = datetime(2025, 12, 31, 23, 59, 59)

# unique_creators = set()
# for topic in truly_solved:
#     topic_date = parse_date(topic['created_at'])
#     if t14_start <= topic_date <= t14_end:
#         # Original poster = post_number 1
#         op = [p for p in topic['posts'] if p['post_number'] == 1]
#         if op:
#             unique_creators.add(op[0]['username'].lower())

# print(f"\nTask 14 - Unique creators (Jul-Dec 2025): {len(unique_creators)}")

# # ================================================================
# # TASK 16: top liked user — posts between Jul-Dec 2025
# # ================================================================
# t16_start = datetime(2025, 7, 1)
# t16_end = datetime(2025, 12, 31, 23, 59, 59)

# user_likes = defaultdict(int)
# for topic in truly_solved:
#     for post in topic['posts']:
#         d = parse_date(post['created_at'])
#         if t16_start <= d <= t16_end:
#             user_likes[post['username']] += post['likes']

# if user_likes:
#     top_user = max(user_likes, key=user_likes.get)
#     print(f"\nTask 16 - Top liked user (Jul-Dec 2025): {top_user} ({user_likes[top_user]} likes)")
# else:
#     print("\nTask 16 - No posts found!")

# print("\n--- ANSWERS ---")
# print(f"task14: {len(unique_creators)}")
# print(f"task16: {top_user}")

# # task 14 ans : is actually 105 but this script gives 104

import json
from datetime import datetime

def parse_date(s):
    return datetime.fromisoformat(s.replace('Z','').split('+')[0])

CUTOFF = datetime(2026, 4, 25, 23, 59, 59)

with open('data/python-kb.json', 'r') as f:
    data = json.load(f)

t14_start = datetime(2025, 7, 1)
t14_end = datetime(2025, 12, 31, 23, 59, 59)

# Check ALL topics in Jul-Dec 2025 range regardless of solved status
all_in_range = []
for topic in data:
    d = parse_date(topic['created_at'])
    if t14_start <= d <= t14_end:
        all_in_range.append(topic)

print(f"ALL topics in Jul-Dec 2025: {len(all_in_range)}")

# Now check which ones we excluded
truly_solved_ids = set()
excluded = []
for topic in data:
    accepted_posts = [p for p in topic['posts'] if p['accepted_answer']]
    if not accepted_posts:
        excluded.append(topic)
        continue
    if parse_date(accepted_posts[0]['created_at']) <= CUTOFF:
        truly_solved_ids.add(topic['id'])
    else:
        excluded.append(topic)

print(f"Excluded topics total: {len(excluded)}")

# Find excluded topics that are in Jul-Dec 2025 range
excluded_in_range = []
for topic in excluded:
    d = parse_date(topic['created_at'])
    if t14_start <= d <= t14_end:
        excluded_in_range.append(topic)

print(f"Excluded topics in Jul-Dec 2025: {len(excluded_in_range)}")
for t in excluded_in_range:
    accepted = [p for p in t['posts'] if p['accepted_answer']]
    op = min(t['posts'], key=lambda p: p['post_number']) if t['posts'] else None
    print(f"  id={t['id']} title={t['title'][:40]}")
    print(f"  creator={op['username'] if op else 'NONE'}")
    print(f"  accepted_post={'NONE' if not accepted else accepted[0]['created_at']}")
    print(f"  posts_in_our_data={len(t['posts'])}")

# Try counting with ALL topics in range (no solved filter)
unique_all = set()
for topic in all_in_range:
    op = min(topic['posts'], key=lambda p: p['post_number']) if topic['posts'] else None
    if op:
        unique_all.add(op['username'].lower())

print(f"\nUnique creators (ALL topics in range): {len(unique_all)}")