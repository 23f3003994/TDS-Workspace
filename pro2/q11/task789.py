# import requests
# from bs4 import BeautifulSoup

# proxies = {
#     'http': 'socks5h://127.0.0.1:9050',
#     'https': 'socks5h://127.0.0.1:9050'
# }

# BASE = "http://tds26vu3ptapxx6igo6n26kuwfpn2l5omkmagc4hc7g7yn2o3xb25syd.onion/90"

# def get_page(url):
#     response = requests.get(url, proxies=proxies, timeout=60)
#     return BeautifulSoup(response.text, 'lxml')

# # ---- Step 1: Go through all 20 feed pages ----
# verified_handles = set()
# all_handles = set()
# python_likes = 0

# for page_num in range(1, 21):
#     if page_num == 1:
#         url = f"{BASE}/index.html"
#     else:
#         url = f"{BASE}/feed_page_{page_num}.html"
    
#     print(f"Scanning feed page {page_num}...")
#     soup = get_page(url)
    
    
#     posts = soup.find_all('article', class_='post-card')
    
#     for post in posts:
#         post_header = post.find('div', class_='post-header')
        
#         # Get handle
#         handle_tag = post_header.find('a', class_='handle')
#         handle = handle_tag.text.strip().replace('@', '')
#         all_handles.add(handle)
        
#         # Check if verified (SVG present in header)
#         verified_svg = post_header.find('svg', class_='verified')
#         if verified_svg:
#             verified_handles.add(handle)
        
#         # Check for #python hashtag
#         post_text = post.find('div', class_='post-text')
#         hashtags = [h.text.strip() for h in post_text.find_all('span', class_='hashtag')]
        
#         if '#python' in hashtags:
#             # Get likes from aria-label="Likes" NOT from .trap
#             likes_div = post.find('div', {'aria-label': 'Likes'})
#             likes = int(likes_div.find('span').text.strip())
#             python_likes += likes
#             print(f"  #python post found! Likes: {likes}")

# print(f"\nTotal unique users found: {len(all_handles)}")
# print(f"Verified users: {len(verified_handles)} → {verified_handles}")
# print(f"\nTASK 9 ANSWER: {python_likes}")

# # ---- Step 2: Visit each user profile ----
# user_data = {}

# for handle in all_handles:
#     url = f"{BASE}/u/{handle}/index.html"
#     print(f"Fetching profile: {handle}...")
#     soup = get_page(url)
    
    
#     # Get followers - second stat-val is followers
#     stats = soup.find('div', class_='profile-stats')
#     stat_vals = stats.find_all('span', class_='stat-val')
#     followers = int(stat_vals[1].text.strip())
    
#     # Get location
#     location_span = soup.find('span', string=lambda s: s and '📍' in s)
#     location = location_span.text.replace('📍', '').strip() if location_span else ''
    
#     user_data[handle] = {
#         'followers': followers,
#         'location': location,
#         'verified': handle in verified_handles
#     }
#     print(f"  {handle} | Followers: {followers} | Location: {location} | Verified: {handle in verified_handles}")

# # ---- Task 7: Total followers of all verified users ----
# verified_followers_total = sum(
#     u['followers'] for h, u in user_data.items() if u['verified']
# )
# print(f"\n{'='*50}")
# print(f"TASK 7 ANSWER: {verified_followers_total}")

# # ---- Task 8: Handle with most followers in West Kimberly ----
# west_kimberly_users = {h: u for h, u in user_data.items() if u['location'] == 'West Kimberly'}
# print(f"\nWest Kimberly users found: {len(west_kimberly_users)}")
# for h, u in west_kimberly_users.items():
#     print(f"  {h} | Followers: {u['followers']}")

# if west_kimberly_users:
#     top_user = max(west_kimberly_users, key=lambda h: west_kimberly_users[h]['followers'])
#     print(f"TASK 8 ANSWER: {top_user}")
# else:
#     print("No West Kimberly users found!")

# print(f"\nTASK 9 ANSWER: {python_likes}")


import requests
from bs4 import BeautifulSoup
import time

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

BASE = "http://tds26vu3ptapxx6igo6n26kuwfpn2l5omkmagc4hc7g7yn2o3xb25syd.onion/90"

def get_page(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, proxies=proxies, timeout=60)
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
            time.sleep(5)
    return None

# ---- Step 1: Go through all 20 feed pages ----
verified_handles = set()
all_handles = set()
python_likes = 0

for page_num in range(1, 21):
    if page_num == 1:
        url = f"{BASE}/index.html"
    else:
        url = f"{BASE}/feed_page_{page_num}.html"
    
    print(f"Scanning feed page {page_num}...")
    soup = get_page(url)
    if not soup:
        print(f"  Failed to load page {page_num}, skipping...")
        continue
    
    posts = soup.find_all('article', class_='post-card')
    
    for post in posts:
        post_header = post.find('div', class_='post-header')
        
        # Get handle
        handle_tag = post_header.find('a', class_='handle')
        handle = handle_tag.text.strip().replace('@', '')
        all_handles.add(handle)
        
        # Check if verified
        verified_svg = post_header.find('svg', class_='verified')
        if verified_svg:
            verified_handles.add(handle)
        
        # Check for #python hashtag
        post_text = post.find('div', class_='post-text')
        hashtags = [h.text.strip() for h in post_text.find_all('span', class_='hashtag')]
        
        if '#python' in hashtags:
            likes_div = post.find('div', {'aria-label': 'Likes'})
            likes = int(likes_div.find('span').text.strip())
            python_likes += likes
            print(f"  #python post found! Likes: {likes}")

print(f"\nTotal unique users found: {len(all_handles)}")
print(f"Verified users: {len(verified_handles)}")
print(f"TASK 9 ANSWER: {python_likes}")

# ---- Step 2: Visit each user profile ----
user_data = {}

for handle in all_handles:
    url = f"{BASE}/u/{handle}/index.html"
    print(f"Fetching profile: {handle}...")
    soup = get_page(url)
    
    if not soup:
        print(f"  Skipping {handle} due to error")
        continue
    
    # DEBUG - print raw location div for first user
    if not user_data:
        profile_header = soup.find('div', class_='profile-header')
        location_div = profile_header.find('div', style=lambda s: s and 'color' in s if s else False)
        print(f"  DEBUG location div: {location_div}")
    
    # Get followers
    stats = soup.find('div', class_='profile-stats')
    stat_vals = stats.find_all('span', class_='stat-val')
    followers = int(stat_vals[1].text.strip())
    
    # Get location - find the div with margin-top and muted color style
    profile_header = soup.find('div', class_='profile-header')
    location = ''
    
    # Find all divs in profile header
    all_divs = profile_header.find_all('div')
    for div in all_divs:
        style = div.get('style', '')
        if 'margin-top: 1rem' in style and 'color' in style:
            # First span is location, second is join date
            spans = div.find_all('span')
            if spans:
                location = spans[0].get_text(strip=True)
                # Remove the pin emoji and any leading/trailing spaces
                location = location.encode('ascii', 'ignore').decode('ascii').strip()
            break
    
    user_data[handle] = {
        'followers': followers,
        'location': location,
        'verified': handle in verified_handles
    }
    print(f"  {handle} | Followers: {followers} | Location: '{location}' | Verified: {handle in verified_handles}")

# ---- Task 7 ----
verified_followers_total = sum(
    u['followers'] for h, u in user_data.items() if u['verified']
)
print(f"\n{'='*50}")
print(f"TASK 7 ANSWER: {verified_followers_total}")

# ---- Task 8 ----
west_kimberly_users = {h: u for h, u in user_data.items() if u['location'] == 'West Kimberly'}
print(f"\nWest Kimberly users found: {len(west_kimberly_users)}")
for h, u in west_kimberly_users.items():
    print(f"  {h} | Followers: {u['followers']}")

if west_kimberly_users:
    top_user = max(west_kimberly_users, key=lambda h: west_kimberly_users[h]['followers'])
    print(f"TASK 8 ANSWER: {top_user}")
else:
    print("No West Kimberly users found!")

print(f"\nTASK 9 ANSWER: {python_likes}")