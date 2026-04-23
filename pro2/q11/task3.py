import requests
from bs4 import BeautifulSoup
import json

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

BASE = "http://tds26vu3ptapxx6igo6n26kuwfpn2l5omkmagc4hc7g7yn2o3xb25syd.onion/33"

PAGES = [
    f"{BASE}/cat/home/index.html",
    f"{BASE}/cat/home/offset-24.html",
    f"{BASE}/cat/home/offset-48.html",
]

def get_page(url):
    response = requests.get(url, proxies=proxies, timeout=60)
    return BeautifulSoup(response.text, 'lxml')

def get_exact_rating(sku):
    """Visit product page and calculate exact average from all individual reviews"""
    url = f"{BASE}/p/{sku}.html"
    soup = get_page(url)
    
    # Find the reviews section
    reviews_section = soup.find('div', class_='reviews-section')
    
    if not reviews_section:
        return None
    
    # Find all review items
    review_items = reviews_section.find_all('div', class_='review-item')
    
    if not review_items:
        return None
    
    ratings = []
    for review in review_items:
        # Each review has its own aria-label with the rating
        rating_div = review.find('div', class_='rating-strip')
        if rating_div:
            aria = rating_div['aria-label']  # "Rated 4 out of 5 stars"
            rating = float(aria.split('Rated ')[1].split(' out')[0])
            ratings.append(rating)
    
    if ratings:
        return sum(ratings) / len(ratings)
    return None

# ---- Main logic ----
out_of_stock_skus = []

# Step 1: Collect all Out of Stock SKUs from listing pages
for page_url in PAGES:
    print(f"Scanning: {page_url}")
    soup = get_page(page_url)
    cards = soup.find_all('div', class_='card')
    
    for card in cards:
        badge = card.find('div', class_='stock-badge')
        status = badge.text.strip()
        
        if status == 'Out of Stock':
            sku_div = card.find('div', class_='card-sku')
            sku = sku_div.text.replace('SKU:', '').strip()
            out_of_stock_skus.append(sku)

print(f"\nFound {len(out_of_stock_skus)} Out of Stock products")
print("SKUs:", out_of_stock_skus)

# Step 2: Visit each product page and get exact rating
all_ratings = []

for sku in out_of_stock_skus:
    print(f"  Getting exact rating for {sku}...")
    rating = get_exact_rating(sku)
    if rating is not None:
        all_ratings.append(rating)
        print(f"  {sku} exact avg rating: {rating:.4f}")

# Step 3: Calculate overall average
overall_avg = sum(all_ratings) / len(all_ratings)
print(f"\n{'='*50}")
print(f"Out of Stock products with ratings: {len(all_ratings)}")
print(f"TASK 3 ANSWER: {overall_avg:.2f}")