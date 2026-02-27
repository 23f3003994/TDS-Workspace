import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
import os

visited = set()

def crawl(url):
    if url in visited:
        return
    
    print("Visiting:", url)
    visited.add(url)
    
    try:
        response = requests.get(url) # fetch the page content
        soup = BeautifulSoup(response.text, "html.parser") # parse the HTML
        
        for link in soup.find_all("a"):
            href = link.get("href")
            full_url = urljoin(url, href)
            crawl(full_url)
    except:
        pass

start_url = "https://sanand0.github.io/tdsdata/crawl_html/"
crawl(start_url)


# -------- NEW PART --------
count = 0

for page in visited:
    path = urlparse(page).path          # get path
    filename = os.path.basename(path)   # get file name
    
    if filename.endswith(".html") and filename:
        first_char = filename[0].upper()
        if 'M' <= first_char <= 'Z':
            count += 1

print("\nTotal HTML files starting with M to Z:", count)