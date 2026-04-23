
#has task 1 and task 2
import requests
from bs4 import BeautifulSoup
import json

# ---- Tor proxy setup (same as always) ----
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

BASE = "http://tds26vu3ptapxx6igo6n26kuwfpn2l5omkmagc4hc7g7yn2o3xb25syd.onion/33"

# The 3 pages of the home category
PAGES = [
    f"{BASE}/cat/home/index.html",
    f"{BASE}/cat/home/offset-24.html",
    f"{BASE}/cat/home/offset-48.html",
]

def get_page(url):
    """Fetch any page through Tor and return a BeautifulSoup object"""
    response = requests.get(url, proxies=proxies, timeout=60)
    return BeautifulSoup(response.text, 'lxml')

def get_inventory(sku):
    """Visit individual product page and extract inventory_level"""
    url = f"{BASE}/p/{sku}.html"
    soup = get_page(url)
    
    # Find the script tag with id="__SERVER_DATA"
    script_tag = soup.find('script', {'id': '__SERVER_DATA'})
    
    if script_tag:
        data = json.loads(script_tag.string)
        return data['inventory_level']
    
    return 0  # if not found, assume 0

# ---- Main scraping logic ----
total_inventory_value = 0.0
all_products = []

for page_url in PAGES:
    print(f"\nScraping: {page_url}")
    soup = get_page(page_url)
    
    # Find all product cards on this page
    cards = soup.find_all('div', class_='card')
    print(f"Found {len(cards)} products on this page")
    
    for card in cards:
        # Get SKU
        sku_div = card.find('div', class_='card-sku')
        sku = sku_div.text.replace('SKU:', '').strip()
        
        # Get price from data-raw-price attribute
        price_div = card.find('div', class_='current-price')
        price = float(price_div['data-raw-price'])
        
        # Get stock status
        badge = card.find('div', class_='stock-badge')
        status = badge.text.strip()
        
        # Get rating from aria-label
        rating_div = card.find('div', class_='rating-strip')
        aria = rating_div['aria-label']  # "Rated 4 out of 5 stars"
        rating = float(aria.split('Rated ')[1].split(' out')[0])
        
        # Get review count - the (10) number
        review_span = card.find('span', style=lambda s: s and 'color:#64748b' in s)
        review_count = int(review_span.text.strip().strip('()'))
        
        # Get inventory from product page
        print(f"  Getting inventory for {sku}...")
        inventory = get_inventory(sku)
        
        # Calculate this product's inventory value
        value = price * inventory
        total_inventory_value += value
        
        all_products.append({
            'sku': sku,
            'price': price,
            'status': status,
            'rating': rating,
            'reviews': review_count,
            'inventory': inventory,
            'value': value
        })
        
        print(f"  {sku} | ${price} x {inventory} = ${value:.2f} | {status}")

print(f"\n{'='*50}")
print(f"Total products scraped: {len(all_products)}")
#all three urls and tasks are related to home category
#----------------TASK1: Total inventory value across all products in home category ----
print(f"\nTASK 1 ANSWER: {total_inventory_value:.2f}")

# ---- TASK 2: SKU with highest number of reviews ----
max_reviews_product = max(all_products, key=lambda p: p['reviews'])
print(f"\nTASK 2 ANSWER: {max_reviews_product['sku']}")
print(f"  (had {max_reviews_product['reviews']} reviews)")

