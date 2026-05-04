import requests
import json
import time
import os
from datetime import datetime

BASE = "https://discourse.onlinedegree.iitm.ac.in"
CUTOFF = datetime(2026, 4, 25, 23, 59, 59)

os.makedirs("data", exist_ok=True)

# Change this to download one category at a time
CATEGORY_TO_DOWNLOAD = ("english2-kb", "English II")
#("sc-kb", "System Commands")

COOKIE = "_fbp=fb.2.1695895939030.610410321; _ga_YRLBGM14X9=GS1.1.1745127161.1.1.1745127433.15.0.0; _ga_3GCYV6BMDX=GS2.1.s1747369438$o3$g1$t1747369488$j0$l0$h0; _ga_S234BK01XY=GS2.3.s1747369513$o1$g1$t1747369529$j44$l0$h0; _ga_LTJPTW3NR9=GS2.1.s1747369513$o1$g1$t1747369799$j0$l0$h0; _ga=GA1.1.1451270738.1695895939; _gcl_au=1.1.1223384585.1775624988; _ga_5HTJMW67XK=GS2.1.s1777531472$o732$g0$t1777531493$j39$l0$h0; _ga_08NPRH5L4M=GS2.1.s1777531472$o1487$g1$t1777531501$j31$l0$h0; _forum_session=P9re7nC2vBilF1vGknMdugo%2FTUvTMsABF%2F4T%2B6NBIbZye%2FREEIn1ewZGCor0VywMkGu6E%2BH7u2e4bNqmuEbK4JC%2FCrwfqGjNlaPFHWE4uMw3knZH9sLLFS3sMf2fiEQ7CJ0YzoZrJQD10Z6tt0th1OewRUU4F3%2FwOvVzXXzotHyBGZ%2FkrB0JhjxbaHHUOx9GlV6yhb%2BxxcK3RWfXwzOznCUF8wZsssK3dFd3j7EgwcTP5HMaPWlRsZ5p429W0y%2F0E5vaS5l7flFCPTW0%2BpA%3D--of4fHQxyRdrbQ7wb--yFWny%2Bnk9qfrMlCtPUsqkA%3D%3D; _t=42ukL6fWe7H1X%2FQr0iwUnquEX1XUHrTh7r8gv%2BlLwI8uFUzVa2ILtQq8wdtEHMUHduA2%2FvdbOi301oCgFQtyRhBnDtgh0H1xzVupaDvXUTjBK%2B8tiif6blAPUYgIAZGrDdQzVZ8eBjIoG%2BuNPOKh5jnk67Q%2Bptg78iTzxvuLl9pf3PSUaZxWryG4FGt%2BJboDP%2B5uNcAT2Dl59mTfPChip6pGTOndYgd%2B0BJ5T7f72Hu40%2BPACCsHAK%2BVksQCGWmCdSYW7eAYZDbxDtm534jm%2BYj15mrJ%2F4HPPxpRzYRdfHI%3D--zsovVkalptTC2rmn--eonyKlma5yL5zgNMc%2BLmng%3D%3D"

HEADERS = {
    "cookie": COOKIE,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.json()
        print(f"  Error {r.status_code} for {url}")
        return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None

def parse_date(s):
    return datetime.fromisoformat(s.replace('Z', '').split('+')[0])

def fetch_all_topics(category_slug):
    all_topics = []
    page = 0

    while True:
        url = f"{BASE}/filter.json?q=category:{category_slug}+status:solved&page={page}"
        print(f"  Fetching topics page {page}...")
        data = fetch_json(url)
        time.sleep(1)

        if not data:
            break

        topics = data.get('topic_list', {}).get('topics', [])
        if not topics:
            print(f"  No more topics at page {page}")
            break

        all_topics.extend(topics)
        print(f"  Got {len(topics)} topics (total: {len(all_topics)})")
        page += 1

    # Deduplicate by topic ID
    unique = list({t["id"]: t for t in all_topics}.values())

    # Filter to only topics on or before cutoff
    filtered = [t for t in unique if parse_date(t['created_at']) <= CUTOFF]
    print(f"  After dedup + date filter: {len(filtered)} topics")
    return filtered

def process_post(post):
    created_at = post.get('created_at', '')
    if not created_at:
        return None
    if parse_date(created_at) > CUTOFF:
        return None

    likes = 0
    for action in post.get('actions_summary', []):
        if action.get('id') == 2:
            likes = action.get('count', 0)

    return {
        'id': post.get('id'),
        'post_number': post.get('post_number'),
        'username': post.get('username'),
        'created_at': created_at,
        'likes': likes,
        'accepted_answer': post.get('accepted_answer', False)
    }

def fetch_topic_posts(topic_id):
    all_posts = []

    url = f"{BASE}/t/{topic_id}.json"
    data = fetch_json(url)
    time.sleep(1)

    if not data:
        return all_posts

    post_stream = data.get('post_stream', {})
    all_post_ids = post_stream.get('stream', [])
    first_posts = post_stream.get('posts', [])

    for post in first_posts:
        processed = process_post(post)
        if processed:
            all_posts.append(processed)

    loaded_ids = {p['id'] for p in first_posts}
    remaining = [pid for pid in all_post_ids if pid not in loaded_ids]

    for i in range(0, len(remaining), 20):
        chunk = remaining[i:i+20]
        ids_param = "&post_ids[]=".join(str(pid) for pid in chunk)
        url2 = f"{BASE}/t/{topic_id}/posts.json?post_ids[]={ids_param}"
        data2 = fetch_json(url2)
        time.sleep(1)

        if not data2:
            continue

        posts = data2.get('post_stream', {}).get('posts', [])
        for post in posts:
            processed = process_post(post)
            if processed:
                all_posts.append(processed)

    # Deduplicate posts by ID
    seen = set()
    unique_posts = []
    for post in all_posts:
        if post['id'] not in seen:
            seen.add(post['id'])
            unique_posts.append(post)

    return unique_posts

def download_category(slug, name):
    output_file = f"data/{slug}.json"
    progress_file = f"data/{slug}_progress.json"

    # Load existing progress if any
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            result = json.load(f)
        done_ids = {t['id'] for t in result}
        print(f"\n✅ Resuming {name} — {len(result)} topics already done")
    else:
        result = []
        done_ids = set()

    if os.path.exists(output_file):
        print(f"\n✅ {name} already fully downloaded, skipping...")
        return

    print(f"\n{'='*50}")
    print(f"Downloading: {name} ({slug})")
    print(f"{'='*50}")

    topics = fetch_all_topics(slug)

    # Skip already downloaded topics
    remaining_topics = [t for t in topics if t['id'] not in done_ids]
    print(f"  {len(done_ids)} already done, {len(remaining_topics)} remaining")

    for i, topic in enumerate(remaining_topics):
        topic_id = topic['id']
        print(f"  [{len(done_ids)+i+1}/{len(topics)}] Topic {topic_id}: {topic.get('title','')[:50]}")
        
        posts = fetch_topic_posts(topic_id)
        
        result.append({
            'id': topic_id,
            'title': topic.get('title', ''),
            'created_at': topic.get('created_at', ''),
            'tags': [t['name'] if isinstance(t, dict) else t for t in topic.get('tags', [])],
            'has_accepted_answer': topic.get('has_accepted_answer', False),
            'posts': posts
        })

        # Save progress after every topic
        with open(progress_file, 'w') as f:
            json.dump(result, f)

    # All done — save final file and remove progress file
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    os.remove(progress_file)
    print(f"\n✅ Saved {len(result)} topics to {output_file}")

# ---- Main ----
slug, name = CATEGORY_TO_DOWNLOAD
print(f"Starting download for: {name}\n")
download_category(slug, name)
print(f"\n✅ Done!")
