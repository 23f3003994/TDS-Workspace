# import requests
# import json
# import time
# from datetime import datetime

# BASE = "https://discourse.onlinedegree.iitm.ac.in"
# CUTOFF = datetime(2026, 4, 25, 23, 59, 59)

# COOKIE = "_fbp=fb.2.1695895939030.610410321; _ga_YRLBGM14X9=GS1.1.1745127161.1.1.1745127433.15.0.0; _ga_3GCYV6BMDX=GS2.1.s1747369438$o3$g1$t1747369488$j0$l0$h0; _ga_S234BK01XY=GS2.3.s1747369513$o1$g1$t1747369529$j44$l0$h0; _ga_LTJPTW3NR9=GS2.1.s1747369513$o1$g1$t1747369799$j0$l0$h0; _ga=GA1.1.1451270738.1695895939; _gcl_au=1.1.1223384585.1775624988; _ga_5HTJMW67XK=GS2.1.s1777356635$o729$g0$t1777356727$j60$l0$h0; _ga_08NPRH5L4M=GS2.1.s1777356635$o1483$g1$t1777358361$j60$l0$h0; _forum_session=yB%2FLB71KpWe5UBmy2SNaT%2B7RMUQtj%2B6Kzd2dt%2BQ0dfEa4fegefQMxaPAR%2FOr8VzWORmhb8gJYiiH5OXULwXSSvj9Go9Jvw%2F3sy8sKMMDzHIV538gCFzv9hl7YcTD%2Ft3pQYikaEegejut%2Fz8%2FL4xPW6BK6nHHb9Bxx12ZDXeTvHH0zFXd1y6EXpOJgKQ99y5sj9KkkeJNJBYe9kxmk626D7UPaKMpthHx9NVRRC26VaV5SpjR5w6FaJmt6yTW99wlVeaoFQA94os6zl3N5318%2BXoU%2FuxWH7eKKjfooQZfoLYdMxrSOY9A1p0dE29TrSOA%2BGg%2F%2FWjdetNeTdj2itXWitA0IKd6zJdSfZhECKaPisnq6qndwvgT4WlK1wkuHzW%2BQtj1SAbbCxzkDeVlubjRz0x%2Fm26p%2B9WKv%2Fs5KfS6qejBMWo4cLRovuvO06nR%2BQ%3D%3D--h5D2BEKSAOHMsQcF--Sgo0JOViJ4TEu5BulhAPPw%3D%3D; _t=fvBCKLCPx3jookzvp2VNyoxr4mQxBcekS9%2B%2Ba03%2FIGxy6afUy7vrEKPgk4rcnbNQbGjtSjJn016tseUs5W1CY2ZRAWBPi7gjW7C0EN4C2Eos2HIfnxhP2LQ5RpYVSttvnELnKQA5LuIv6RFsE%2Fe27bLVgbvt%2FL%2BDivPNFGrj4Vc8voNLFTFje66g1GozU%2FuSnkWjOQtIEgVWtPIlSHX85UsWMTpolNw8hv4Q%2B%2FjdoxEFx2QE5JGxIBXvPTbSbgHtYSrfluD9IIOGuFm%2FzhX2X0CxeM6GOaFUgD17ZPpBXXY%3D--m0ppA4E2QFrA24Lp--EzPHv9iwEah9Jcve6jmQlA%3D%3D"
# HEADERS = {
#     "cookie": COOKIE,
#     "user-agent": "Mozilla/5.0"
# }

# def fetch_json(url):
#     try:
#         r = requests.get(url, headers=HEADERS, timeout=30)
#         if r.status_code == 200:
#             return r.json()
#         print(f"  Error {r.status_code}")
#         return None
#     except Exception as e:
#         print(f"  Exception: {e}")
#         return None

# def parse_date(s):
#     return datetime.fromisoformat(s.replace('Z','').split('+')[0])

# def search_topic(title, category):
#     """Search for a specific topic by title"""
#     url = f"{BASE}/search.json?q={requests.utils.quote(title)}+category:{category}"
#     data = fetch_json(url)
#     time.sleep(1)
#     if not data:
#         return None
#     topics = data.get('topics', [])
#     # Find exact title match
#     for t in topics:
#         if t['title'].strip().lower() == title.strip().lower():
#             return t
#     # If no exact match return first result
#     if topics:
#         print(f"  No exact match, using closest: {topics[0]['title']}")
#         return topics[0]
#     return None

# def get_topic_posts(topic_id):
#     """Get all posts for a topic"""
#     all_posts = []
#     url = f"{BASE}/t/{topic_id}.json"
#     data = fetch_json(url)
#     time.sleep(1)
#     if not data:
#         return all_posts

#     post_stream = data.get('post_stream', {})
#     all_post_ids = post_stream.get('stream', [])
#     first_posts = post_stream.get('posts', [])

#     for post in first_posts:
#         all_posts.append(post)

#     loaded_ids = {p['id'] for p in first_posts}
#     remaining = [pid for pid in all_post_ids if pid not in loaded_ids]

#     for i in range(0, len(remaining), 20):
#         chunk = remaining[i:i+20]
#         ids_param = "&post_ids[]=".join(str(pid) for pid in chunk)
#         url2 = f"{BASE}/t/{topic_id}/posts.json?post_ids[]={ids_param}"
#         data2 = fetch_json(url2)
#         time.sleep(1)
#         if data2:
#             posts = data2.get('post_stream', {}).get('posts', [])
#             all_posts.extend(posts)

#     return all_posts

# def get_accepted_post_id(topic_id):
#     """Find the accepted answer post ID"""
#     posts = get_topic_posts(topic_id)
#     for post in posts:
#         if post.get('accepted_answer', False):
#             return post['id']
#     return None

# def get_reply_count_compound(topic_id):
#     """Get reply count and latest reply post ID"""
#     posts = get_topic_posts(topic_id)
#     # Filter by cutoff
#     valid_posts = []
#     for post in posts:
#         created = post.get('created_at', '')
#         if created and parse_date(created) <= CUTOFF:
#             valid_posts.append(post)

#     # Replies = all posts except post_number 1 (original post)
#     replies = [p for p in valid_posts if p.get('post_number', 1) > 1]

#     if not replies:
#         return 0, None

#     reply_count = len(replies)
#     # Latest reply = highest post ID among replies
#     latest = max(replies, key=lambda p: p['id'])
#     return reply_count, latest['id']

# # ================================================================
# # TARGETED TASKS — Each needs only ONE specific topic
# # ================================================================

# print("Solving targeted tasks (Group A)...\n")

# # Task 1: accepted post id
# # "About OPPE VM query" posted by shubh45 on 2025-12-04
# print("Task 1: About OPPE VM query")
# t = search_topic("About OPPE VM query", "sc-kb")
# if t:
#     print(f"  Found topic ID: {t['id']}")
#     ans = get_accepted_post_id(t['id'])
#     print(f"  TASK 1 ANSWER: {ans}")

# # Task 2: reply count compound
# # "Ga-4 q3" posted by 22f2000223 on 2025-02-10
# print("\nTask 2: Ga-4 q3")
# t = search_topic("Ga-4 q3", "sc-kb")
# if t:
#     print(f"  Found topic ID: {t['id']}")
#     count, latest_id = get_reply_count_compound(t['id'])
#     print(f"  TASK 2 ANSWER: {count}-{latest_id}")

# # Task 3: reply count compound
# # "Query regarding BPT" posted by 24dp3000019 on 2025-05-30
# print("\nTask 3: Query regarding BPT")
# t = search_topic("Query regarding BPT", "sc-kb")
# if t:
#     print(f"  Found topic ID: {t['id']}")
#     count, latest_id = get_reply_count_compound(t['id'])
#     print(f"  TASK 3 ANSWER: {count}-{latest_id}")

# # Task 6: reply count compound
# # "Unable to connect to remote VM" posted by 23f2000628 on 2025-09-22
# print("\nTask 6: Unable to connect to remote VM")
# t = search_topic("Unable to connect to remote VM", "sc-kb")
# if t:
#     print(f"  Found topic ID: {t['id']}")
#     count, latest_id = get_reply_count_compound(t['id'])
#     print(f"  TASK 6 ANSWER: {count}-{latest_id}")

# # Task 7: reply count compound
# # "Clarification Regarding Final Score Calculation" posted by 23f2004941 on 2025-08-29
# print("\nTask 7: Clarification Regarding Final Score Calculation")
# t = search_topic("Clarification Regarding Final Score Calculation", "sc-kb")
# if t:
#     print(f"  Found topic ID: {t['id']}")
#     count, latest_id = get_reply_count_compound(t['id'])
#     print(f"  TASK 7 ANSWER: {count}-{latest_id}")

# # Task 8: reply count compound
# # "Mega Thread - OPPE FAQs and PYQs" posted by 21f3000759 on 2026-04-17
# print("\nTask 8: Mega Thread - OPPE FAQs and PYQs")
# t = search_topic("Mega Thread - OPPE FAQs and PYQs", "sc-kb")
# if t:
#     print(f"  Found topic ID: {t['id']}")
#     count, latest_id = get_reply_count_compound(t['id'])
#     print(f"  TASK 8 ANSWER: {count}-{latest_id}")

# # Task 9: accepted post id
# # "BPT permission denied(permission not granted)" posted by 23dp2000032 on 2025-01-25
# print("\nTask 9: BPT permission denied")
# t = search_topic("BPT permission denied(permission not granted)", "sc-kb")
# if t:
#     print(f"  Found topic ID: {t['id']}")
#     ans = get_accepted_post_id(t['id'])
#     print(f"  TASK 9 ANSWER: {ans}")

# print("\n✅ Group A tasks done!")
# print("Tasks 4, 5, 10 need full download - run download.py for those")

##############################
import requests
import time
from datetime import datetime

BASE = "https://discourse.onlinedegree.iitm.ac.in"

COOKIE = "_fbp=fb.2.1695895939030.610410321; _ga_YRLBGM14X9=GS1.1.1745127161.1.1.1745127433.15.0.0; _ga_3GCYV6BMDX=GS2.1.s1747369438$o3$g1$t1747369488$j0$l0$h0; _ga_S234BK01XY=GS2.3.s1747369513$o1$g1$t1747369529$j44$l0$h0; _ga_LTJPTW3NR9=GS2.1.s1747369513$o1$g1$t1747369799$j0$l0$h0; _ga=GA1.1.1451270738.1695895939; _gcl_au=1.1.1223384585.1775624988; _ga_5HTJMW67XK=GS2.1.s1777443149$o730$g0$t1777443165$j44$l0$h0; _t=eEAMiL7d6bzJYmkRIH6uuuvVxrq2xRW0sVrBk84VW7nLb%2BmS1%2F5SwL9Va4vJPf3gRKLUuZQjZPyuxMpJmHONjQTzvt%2BasYZ5gKcIVrm3fb0XhJ1Jl8yt%2Fom9TZS0lrQ3HhvH1unT2%2Bh58kd5Ac0YekofB7eIxb3V528Qf8hWz%2BO4EUZ0W%2BfMH9fWocDLIbiyn2tEdMqY8ECFleKxbfO3NjUyNVqmkb4aP9ThZ1RfXA1J41%2Bn%2FZ1r2OcOoPznw06JUhsV7W3pdothwwpPDLVe73rRVquIQPCEFc1EcnLkS1w%3D--O55VZgY1SdwagH%2B0--UlT5CgiWvkPTo%2B3LhSoEbg%3D%3D; _ga_08NPRH5L4M=GS2.1.s1777454636$o1485$g0$t1777454645$j51$l0$h0; _forum_session=EXqke6uPIMZlScs64l78e3xamyB7nfAKayLL7fggtgpBdEotrQ9p4VhsW1ljXxFQ6ZWVbN947pEiOCD6yUOZ1fhQMHBcdJLg2JJHPsBws9%2FZEXLSb5lRvFGEx5BTd3FJjXpKkQKa4yyvyYu0lWt8CDz2VyhpXVyRYVN0X0dJaQW80zU3uYEP7xhG1u%2B1IiTRMnL5lrrTTyJBe20YDiBtXsEPVlGdDd%2BsHd%2FBCUl96WD1MFsnjrhiALCNnJ456t%2FldRBsZf2m07MvJ53WpTRmdkOYEg%2F%2FsgRQE6fWCFDWI3pOOm0KW7aKuJfsK9PNYhL%2BacNVup2QLkGqbUd1aHuNyhRMf6zIWIwGwOcrL6QcbnQ5TPSKUGtcD49Zl8H5yfwW4T4tF%2BD%2FduZklFKuEbaNnWidaSXU3PNyvTsGVI8czAmgE0ya7d5SKpf9z%2BC56A%3D%3D--eYsXJe%2BC%2BKYLOEGg--eoX%2BLpK2bFU6SRilfwUnHA%3D%3D"
HEADERS = {"cookie": COOKIE, "user-agent": "Mozilla/5.0"}
CUTOFF = datetime(2026, 4, 25, 23, 59, 59)



def fetch_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

def parse_date(s):
    return datetime.fromisoformat(s.replace('Z','').split('+')[0])

# Get all posts for Mega Thread

topic_id = 201785
url = f"{BASE}/t/{topic_id}.json"
data = fetch_json(url)
post_stream = data.get('post_stream', {})
all_post_ids = post_stream.get('stream', [])
first_posts = post_stream.get('posts', [])
#169-761158
#168-761112
#167-761111
all_posts = list(first_posts)
loaded_ids = {p['id'] for p in first_posts}
remaining = [pid for pid in all_post_ids if pid not in loaded_ids]

for i in range(0, len(remaining), 20):
    chunk = remaining[i:i+20]
    ids_param = "&post_ids[]=".join(str(pid) for pid in chunk)
    url2 = f"{BASE}/t/{topic_id}/posts.json?post_ids[]={ids_param}"
    data2 = fetch_json(url2)
    time.sleep(1)
    if data2:
        posts = data2.get('post_stream', {}).get('posts', [])
        all_posts.extend(posts)

print(f"Total posts: {len(all_posts)}")

# Show ALL posts from April 24 onwards with their dates
# print("\nPosts from April 24 onwards:")
for p in sorted(all_posts, key=lambda x: x['created_at']):
    d = parse_date(p['created_at'])
    # if d >= datetime(2026, 4, 24):
    if p['deleted_at'] is not None :
        print(f"  post_num={p['post_number']} id={p['id']} created={p['created_at']} deleted={p['deleted_at']}")


