
#task answers for qstns that dont require full fetch of all posts or topics
import requests
import json
import time
from datetime import datetime

BASE = "https://discourse.onlinedegree.iitm.ac.in"
CUTOFF = datetime(2026, 4, 25, 23, 59, 59)
REPLY_CUTOFF = CUTOFF  

COOKIE = "_fbp=fb.2.1695895939030.610410321; _ga_YRLBGM14X9=GS1.1.1745127161.1.1.1745127433.15.0.0; _ga_3GCYV6BMDX=GS2.1.s1747369438$o3$g1$t1747369488$j0$l0$h0; _ga_S234BK01XY=GS2.3.s1747369513$o1$g1$t1747369529$j44$l0$h0; _ga_LTJPTW3NR9=GS2.1.s1747369513$o1$g1$t1747369799$j0$l0$h0; _ga=GA1.1.1451270738.1695895939; _gcl_au=1.1.1223384585.1775624988; _ga_5HTJMW67XK=GS2.1.s1777443149$o730$g0$t1777443165$j44$l0$h0; _ga_08NPRH5L4M=GS2.1.s1777454636$o1485$g0$t1777454645$j51$l0$h0; _bypass_cache=true; _forum_session=6m42xZsanYd%2B4i5jUMLxYYGC6DA3ivbwzQKBqETyiPZ2cqCrhkoHPYnTPjPypGI4xORkuZgftVEvwmitF7PY4fRr7AJ5Td290%2BIouYt8%2BreIolItaRbbe6kC3dsuNIbmvquB1v06kkqT1crmMdMAGs%2F5IlFOOYTz4%2FGiZcQ%2FhdedmsridmzkAQfC6uKxNjc7VeKxnfiD25BB4EE8Ze0narfgPaP5Crl%2FZA6Z7TuhQW09oJ1%2Fh7nWjN0xlfzzUvIt%2BrSknB7FbQ%2BC3KtaYLSerNn0HKA1iAWdrfLF%2BsI9XLBqAaGPfPSD48qGea22oL9LMBKhzJiKXW7wsCZGGyG6kHWQNCERSS5QRATfo7JCB8Ug8rSsymM%3D--t5MkWtH3ztiD%2BPI9--7xZLqrji4DyAKnSFnykkEQ%3D%3D; _t=y3sZG5ICAQ%2Fp7LefH4r7eXOcbYN4FUf5iAQESW9FqXGIwDC%2BmFgtTw2t3o6IGK5ixNfdE4SMbYcg9UFTH3oW5iRnGL%2BUA6EQxa%2Fl651MLL%2FVDbxMFJkphwPnihDCl7xPEj4a51LLgHlehYpNd%2F8h11QHD3ppfUgLwISu3u%2BMYzD%2FEsCHySJkJ4H%2BpJGGdqcXCNY6cKS7uoogwyIM%2FxfY0Jx5D5LZB2yqWFQJDqmzrBfE3LXCR8aMu4250cMMpts%2BuCFud9shPlYmbG%2BeRXdkRvwJ34pg%2Bd3mC76ubcsPHFY%3D--QIy%2FH5cj4BpyM2OP--CVizP3mTJ%2FMw9dGvQ9VOvg%3D%3D"
HEADERS = {
    "cookie": COOKIE,
    "user-agent": "Mozilla/5.0"
}

def fetch_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.json()
        print(f"  Error {r.status_code}")
        return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None

def parse_date(s):
    return datetime.fromisoformat(s.replace('Z','').split('+')[0])

def search_topic(title, category):
    url = f"{BASE}/search.json?q={requests.utils.quote(title)}+category:{category}"
    data = fetch_json(url)
    time.sleep(1)
    if not data:
        return None
    topics = data.get('topics', [])
    for t in topics:
        if t['title'].strip().lower() == title.strip().lower():
            return t
    if topics:
        print(f"  No exact match, using: {topics[0]['title']}")
        return topics[0]
    return None

def get_all_posts(topic_id):
    all_posts = []
    url = f"{BASE}/t/{topic_id}.json"
    data = fetch_json(url)
    time.sleep(1)
    if not data:
        return all_posts

    post_stream = data.get('post_stream', {})
    all_post_ids = post_stream.get('stream', [])
    first_posts = post_stream.get('posts', [])
    all_posts.extend(first_posts)

    loaded_ids = {p['id'] for p in first_posts}
    remaining = [pid for pid in all_post_ids if pid not in loaded_ids]

    for i in range(0, len(remaining), 20):
        chunk = remaining[i:i+20]
        ids_param = "&post_ids[]=".join(str(pid) for pid in chunk)
        url2 = f"{BASE}/t/{topic_id}/posts.json?post_ids[]={ids_param}"
        data2 = fetch_json(url2)
        time.sleep(1)
        if data2:
            all_posts.extend(data2.get('post_stream', {}).get('posts', []))

    # Deduplicate
    seen = set()
    unique = []
    for p in all_posts:
        if p['id'] not in seen:
            seen.add(p['id'])
            unique.append(p)
    return unique

def get_accepted_post_id(topic_id):
    posts = get_all_posts(topic_id)
    for post in posts:
        if post.get('accepted_answer', False):
            return post['id']
    return None

def get_reply_count_compound(topic_id):
    posts = get_all_posts(topic_id)
    replies = [p for p in posts
               if p.get('post_number', 1) > 1
               and parse_date(p['created_at']) <= REPLY_CUTOFF]
    if not replies:
        return 0, None
    latest = max(replies, key=lambda p: p['id'])
    return len(replies), latest['id']

# ================================================================
answers = {}

# ---- SC-KB ----
tasks = [
    ("task1", "accepted", "About OPPE VM query", "sc-kb"),
    ("task2", "reply", "Ga-4 q3", "sc-kb"),
    ("task3", "reply", "Query regarding BPT", "sc-kb"),
    ("task6", "reply", "Unable to connect to remote VM", "sc-kb"),
    ("task7", "reply", "Clarification Regarding Final Score Calculation", "sc-kb"),
    ("task8", "reply", "Mega Thread - OPPE FAQs and PYQs", "sc-kb"),
    ("task9", "accepted", "BPT permission denied(permission not granted)", "sc-kb"),
    # ---- PYTHON-KB ----
    ("task11", "reply", "Query Regarding Grade for Graded Assignment Week 2 q.25", "python-kb"),
    ("task12", "reply", "Query regarding Non Proctored Programming Exam (NPPE) in python", "python-kb"),
    ("task13", "reply", "New OPPE Score calculation?", "python-kb"),
    ("task15", "accepted", "Doubt regarding PPA's - Week 9", "python-kb"),
    ("task17", "accepted", "Missing Lecture Videos - Course Structure Query", "python-kb"),
    # ---- MLP-KB ----
    ("task20", "reply", "Mlp oppe score", "mlp-kb"),
    # ---- STATS2-KB ----
    ("task23", "reply", "Some trolls are rating the activities with bad marks", "stats2-kb"),
    ("task24", "accepted", "Aq2.1-2", "stats2-kb"),
    # ---- MLT-KB ----
    ("task29", "accepted", "Week 9 Programming Assignment due date passed before GA", "mlt-kb"),
    ("task30", "reply", "Lecture 9.3 Error", "mlt-kb"),
    # ---- DBMS-KB ----
    ("task31", "accepted", "Which version to use", "dbms-kb"),
    ("task32", "reply", "Quiz 1 - 265, 268", "dbms-kb"),
    ("task33", "reply", "UNIQUE constraint allows NULL values in tuples?", "dbms-kb"),
    # ---- TDS-KB ----
    ("task34", "reply", "End term TDS", "tds-kb"),
    # ---- MAD1-KB ----
    ("task37", "reply", "Mad1 project data", "mad1-kb"),
    # ---- MATHS2-KB ----
    ("task40", "accepted", "Week 6 AQ 6.2, Qno.10", "maths2-kb"),
    # ---- JAVA-KB ----
    ("task43", "accepted", "How to prepare for OPPE?", "java-kb"),
    # ---- MLF-KB ----
    ("task46", "reply", "MLF-Week4-L4.1", "mlf-kb"),
    # ---- PDSA-KB ----
    ("task47", "reply", "About additional activity in PDSA", "pdsa-kb"),
    ("task48", "reply", "Week 2 live coding", "pdsa-kb"),
    # ---- MAD2-KB ----
    ("task49", "accepted", "Clarification regarding Mock Test and week-wise weightage for End Term exam", "mad2-kb"),
]

print(f"Solving {len(tasks)} targeted tasks...\n")

for task_id, task_type, title, category in tasks:
    print(f"{task_id}: {title[:50]}")
    t = search_topic(title, category)
    if not t:
        print(f"  ❌ Topic not found!")
        continue

    print(f"  Found topic ID: {t['id']}")

    if task_type == "accepted":
        ans = get_accepted_post_id(t['id'])
        answers[task_id] = str(ans) if ans else "NOT_FOUND"
        print(f"  ANSWER: {answers[task_id]}")

    elif task_type == "reply":
        count, latest_id = get_reply_count_compound(t['id'])
        answers[task_id] = f"{count}-{latest_id}"
        print(f"  ANSWER: {answers[task_id]}")

print("\n" + "="*50)
print("ALL ANSWERS:")
for k, v in sorted(answers.items()):
    print(f"  {k}: {v}")

print("\nJSON to submit:")
print(json.dumps(answers, indent=2))