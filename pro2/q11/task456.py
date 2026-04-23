import requests
from bs4 import BeautifulSoup

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

BASE = "http://tds26vu3ptapxx6igo6n26kuwfpn2l5omkmagc4hc7g7yn2o3xb25syd.onion/72"

def get_page(url):
    response = requests.get(url, proxies=proxies, timeout=60)
    return BeautifulSoup(response.text, 'lxml')

def get_category_articles(category):
    """Get all article links from all pages of a category"""
    article_links = []
    page = 1
    
    while True:
        if page == 1:
            url = f"{BASE}/c/{category}/index.html"
        else:
            url = f"{BASE}/c/{category}/page-{page}.html"
        
        print(f"  Scanning: {url}")
        soup = get_page(url)
        
        # Find all article cards
        articles = soup.find_all('article', class_='article-card')
        
        if not articles:
            break
        
        for article in articles:
            # Get article link - from the real title only (not honeypot)
            title_h2 = article.find('h2', class_='article-title')
            link = title_h2.find('a')['href']
            # link looks like "article/202604-0101.html"
            full_url = f"{BASE}/{link}"
            article_links.append(full_url)
        
        # Check if there's a next page
        pager = soup.find('div', class_='pager')
        next_page = pager.find('a', string=str(page + 1))
        if next_page:
            page += 1
        else:
            break
    
    return article_links

def get_article_data(url):
    """Visit article page and extract author and internal views"""
    soup = get_page(url)
    
    # Get author name
    author_div = soup.find('div', class_='detail-author-name')
    author = author_div.get_text().replace('By', '').strip()
    
    # Get data-internal-views from the hidden span
    hidden_span = soup.find('span', class_='visually-hidden', 
                           attrs={'data-internal-views': True})
    internal_views = int(hidden_span['data-internal-views'])
    
    return author, internal_views

# ---- Main Logic ----
categories = ['tech', 'politics', 'sports']
data = {}  # stores all article data per category

for category in categories:
    print(f"\nScraping category: {category.upper()}")
    links = get_category_articles(category)
    print(f"  Found {len(links)} articles")
    
    articles = []
    for link in links:
        print(f"  Fetching: {link}")
        author, views = get_article_data(link)
        articles.append({'author': author, 'views': views})
        print(f"    Author: {author} | Views: {views}")
    
    data[category] = articles

# ---- Task 4: Total internal views for tech ----
tech_total = sum(a['views'] for a in data['tech'])
print(f"\n{'='*50}")
print(f"TASK 4 ANSWER: {tech_total}")

# ---- Task 5: Count Sarah Baker articles in politics ----
sarah_count = sum(1 for a in data['politics'] if a['author'] == 'Sarah Baker')
print(f"TASK 5 ANSWER: {sarah_count}")

# ---- Task 6: Average internal views for sports ----
sports_views = [a['views'] for a in data['sports']]
sports_avg = round(sum(sports_views) / len(sports_views))
print(f"TASK 6 ANSWER: {sports_avg}")