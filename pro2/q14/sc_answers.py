# import json
# from datetime import datetime

# CUTOFF = datetime(2026, 4, 25, 23, 59, 59)

# def parse_date(s):
#     return datetime.fromisoformat(s.replace('Z','').split('+')[0])

# with open('data/sc-kb.json', 'r') as f:
#     data = json.load(f)

# print(f"Total topics: {len(data)}")

# # Check for still-failed topics
# failed = [t for t in data if len(t['posts']) == 0]
# print(f"Still empty (failed): {len(failed)}")

# # ================================================================
# # TASK 4: top liked user — posts between 2025-04-01 and 2025-06-30
# # ================================================================
# from collections import defaultdict

# t4_start = datetime(2025, 4, 1)
# t4_end = datetime(2025, 6, 30, 23, 59, 59)

# user_likes = defaultdict(int)
# for topic in data:
#     for post in topic['posts']:
#         d = parse_date(post['created_at'])
#         if t4_start <= d <= t4_end:
#             user_likes[post['username']] += post['likes']

# if user_likes:
#     top_user = max(user_likes, key=user_likes.get)
#     print(f"\nTask 4 - Top liked user (Apr-Jun 2025): {top_user} ({user_likes[top_user]} likes)")
# else:
#     print("\nTask 4 - No posts found in range!")

# # ================================================================
# # TASK 5: total posts — between 2025-07-01 and 2025-09-30
# # ================================================================
# t5_start = datetime(2025, 7, 1)
# t5_end = datetime(2025, 9, 30, 23, 59, 59)

# total_posts = 0
# for topic in data:
#     for post in topic['posts']:
#         d = parse_date(post['created_at'])
#         if t5_start <= d <= t5_end:
#             total_posts += 1

# print(f"\nTask 5 - Total posts (Jul-Sep 2025): {total_posts}")

# # ================================================================
# # TASK 10: aggregate likes — between 2026-01-01 and 2026-04-30
# # ================================================================
# t10_start = datetime(2026, 1, 1)
# t10_end = datetime(2026, 4, 25, 23, 59, 59)  # capped at cutoff

# total_likes = 0
# for topic in data:
#     for post in topic['posts']:
#         d = parse_date(post['created_at'])
#         if t10_start <= d <= t10_end:
#             total_likes += post['likes']

# print(f"\nTask 10 - Total likes (Jan-Apr 2026): {total_likes}")

# print("\n--- ANSWERS ---")
# print(f"task4:  {top_user}")
# print(f"task5:  {total_posts}")
# print(f"task10: {total_likes}")
import json
from datetime import datetime

def parse_date(s):
    return datetime.fromisoformat(s.replace('Z','').split('+')[0])

CUTOFF = datetime(2026, 4, 25, 23, 59, 59)

with open('data/sc-kb.json', 'r') as f:
    data = json.load(f)

problem_ids = [202358, 202383, 167312]

t10_start = datetime(2026, 1, 1)
t10_end = datetime(2026, 4, 25, 23, 59, 59)
t5_start = datetime(2025, 7, 1)
t5_end = datetime(2025, 9, 30, 23, 59, 59)

for topic in data:
    if topic['id'] in problem_ids:
        print(f"\nTopic {topic['id']}: {topic['title'][:50]}")
        print(f"  Total posts in our data: {len(topic['posts'])}")
        
        t10_likes = sum(p['likes'] for p in topic['posts']
                       if t10_start <= parse_date(p['created_at']) <= t10_end)
        t5_posts = sum(1 for p in topic['posts']
                      if t5_start <= parse_date(p['created_at']) <= t5_end)
        
        print(f"  Likes in Jan-Apr 2026: {t10_likes}")
        print(f"  Posts in Jul-Sep 2025: {t5_posts}")
        
        for p in topic['posts']:
            d = parse_date(p['created_at'])
            if t10_start <= d <= t10_end:
                print(f"  Post {p['id']}: likes={p['likes']} created={p['created_at']}")