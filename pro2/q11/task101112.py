import requests
from bs4 import BeautifulSoup
import time
import re

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

BASE = "http://tds26vu3ptapxx6igo6n26kuwfpn2l5omkmagc4hc7g7yn2o3xb25syd.onion/8"

def get_page(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, proxies=proxies, timeout=60)
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
            time.sleep(5)
    return None

# ---- TASK 10: Sum reputation of users who joined July 2025 ----
print("=== TASK 10 ===")
members_url = f"{BASE}/users/index.html"
soup = get_page(members_url)

# Get all usernames from members table
rows = soup.find('table', class_='board-list').find_all('tr')[1:]  # skip header
usernames = []
for row in rows:
    cells = row.find_all('td')
    if cells:
        username = cells[0].find('a').text.strip()
        usernames.append(username)

print(f"Total users: {len(usernames)}")

july_reputation_sum = 0
july_users = []

for username in usernames:
    url = f"{BASE}/u/{username}.html"
    print(f"  Checking {username}...")
    soup = get_page(url)
    if not soup:
        continue
    
    # Get joined date and reputation
    text = soup.get_text()
    
    # Find joined date
    joined_match = re.search(r'Joined:\s*(\d{4}-\d{2}-\d{2})', text)
    rep_match = re.search(r'Reputation:\s*(\d+)', text)
    
    if joined_match and rep_match:
        joined = joined_match.group(1)
        reputation = int(rep_match.group(1))
        
        if joined.startswith('2025-07'):
            july_reputation_sum += reputation
            july_users.append((username, joined, reputation))
            print(f"    ✅ JULY 2025! {username} | Joined: {joined} | Rep: {reputation}")

print(f"\nJuly 2025 users: {july_users}")
print(f"TASK 10 ANSWER: {july_reputation_sum}")

# ---- TASK 11: Thread ID with most views in market board ----
print("\n=== TASK 11 ===")
max_views = 0
max_thread_id = None

for page_num in range(1, 5):
    if page_num == 1:
        url = f"{BASE}/b/market/index.html"
    else:
        url = f"{BASE}/b/market/page-{page_num}.html"
    
    print(f"Scanning market page {page_num}...")
    soup = get_page(url)
    if not soup:
        continue
    
    rows = soup.find('table', class_='thread-list').find_all('tr')[1:]
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            # Get replies/views - format is "13 / 215"
            replies_views = cells[2].text.strip()
            views = int(replies_views.split('/')[1].strip())
            
            # Get thread link
            thread_link = cells[0].find('a')['href']
            # Link looks like "t/1001.html"
            thread_id = thread_link.split('/')[-1].replace('.html', '')
            
            print(f"  Thread ID: {thread_id} | Views: {views}")
            
            if views > max_views:
                max_views = views
                max_thread_id = thread_id

print(f"\nTASK 11 ANSWER: {max_thread_id} (with {max_views} views)")

# ---- TASK 12: Count threads with 0 replies in general board ----
print("\n=== TASK 12 ===")
zero_reply_count = 0

for page_num in range(1, 5):
    if page_num == 1:
        url = f"{BASE}/b/general/index.html"
    else:
        url = f"{BASE}/b/general/page-{page_num}.html"
    
    print(f"Scanning general page {page_num}...")
    soup = get_page(url)
    if not soup:
        continue
    
    rows = soup.find('table', class_='thread-list').find_all('tr')[1:]
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            replies_views = cells[2].text.strip()
            replies = int(replies_views.split('/')[0].strip())
            
            if replies == 0:
                zero_reply_count += 1
                title = cells[0].text.strip()
                print(f"  Zero replies: {title}")

print(f"\nTASK 12 ANSWER: {zero_reply_count}")