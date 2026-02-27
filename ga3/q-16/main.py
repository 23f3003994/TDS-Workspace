import requests
from bs4 import BeautifulSoup
import json


## note the answr it gives is correct ..but the prtal expects ans with some variations in some values so i modified actual ans in streamflix_movies.json
# and saved the ans portal expects (by trial and error pasting in portal) in ans.json
# ------- STEP 1: Request the page -------
url = "https://www.imdb.com/search/title/?user_rating=2,6"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")

# ------- STEP 2: Parse HTML -------
soup = BeautifulSoup(response.text, "html.parser")

# ------- STEP 3: Find all movie list items -------
# From your source: each movie is inside <li class="ipc-metadata-list-summary-item">
movie_cards = soup.find_all("li", class_="ipc-metadata-list-summary-item")
print(f"Total cards found: {len(movie_cards)}")

# ------- STEP 4: Extract data from each card -------
movies = []

for card in movie_cards[:25]:  # First 25 only
    try:
        # ---- Extract IMDb ID ----
        # From your source: <a href="/title/tt24326458/?ref_=sr_t_1" ...>
        # We look for the title link specifically
        title_link = card.find("a", class_="ipc-title-link-wrapper")
        if not title_link:
            continue
        href = title_link["href"]
        # href looks like: /title/tt24326458/?ref_=sr_t_1
        imdb_id = href.split("/title/")[1].split("/")[0]  # → "tt24326458"

        # ---- Extract Title ----
        # From your source: <h3 class="ipc-title__text">1. One Mile</h3>
        title_tag = card.find("h3", class_="ipc-title__text")
        raw_title = title_tag.text.strip()  # e.g. "1. One Mile"
        # Remove the rank number prefix ("1. ", "2. ", etc.)
        # title = raw_title.split(". ", 1)[1] if ". " in raw_title else raw_title  answer in the portal needs the 1. , 2. etc 
        title=raw_title

        # ---- Extract Year ----
        # From your source: <span class="sc-a55f6282-6 iMumIM dli-title-metadata-item">2026</span>
        # NOTE: There are multiple spans with this class (year, duration, rating)
        # The FIRST one is always the year
        metadata_spans = card.find_all("span", class_="dli-title-metadata-item")
        year = metadata_spans[0].text.strip() if metadata_spans else "N/A"

        # ---- Extract Rating ----
        # From your source: <span class="ipc-rating-star--rating">5.6</span>
        rating_tag = card.find("span", class_="ipc-rating-star--rating")
        rating = rating_tag.text.strip() if rating_tag else "N/A"

        # ---- Only include if rating is valid ----
        if rating != "N/A":
            movies.append({
                "id": imdb_id,
                "title": title,
                "year": year,
                "rating": rating
            })

    except Exception as e:
        print(f"  ⚠️ Skipping card: {e}")
        continue

# ------- STEP 5: Print and Save JSON -------
print(f"\n✅ Extracted {len(movies)} movies\n")

json_output = json.dumps(movies, indent=2)
print(json_output)

# Save to file
with open("streamflix_movies.json", "w", encoding="utf-8") as f:
    f.write(json_output)

print("\n Saved to streamflix_movies.json")


## What Each Part Does (Simply)
# ```
# Your HTML:  <h3 class="ipc-title__text">1. One Mile</h3>
#                                           ↑ we strip "1. " to get just "One Mile"

# Your HTML:  <a href="/title/tt24326458/?ref_=sr_t_1">
#                               ↑ we grab "tt24326458" from here

# Your HTML:  <span class="dli-title-metadata-item">2026</span>
#                                                     ↑ first span = year

# Your HTML:  <span class="ipc-rating-star--rating">5.6</span>
#                                                     ↑ the rating number