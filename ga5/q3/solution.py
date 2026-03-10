# /// script
# requires-python = ">=3.11"
# dependencies = ["openai", "pandas"]
# ///
import os, json, time
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

BATCH_SIZE = 20
CACHE_FILE = "topic_cache.json"

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)

# ── Pydantic structured output ────────────────────────────────────────────────
class HeadlineLabel(BaseModel):
    headline: str
    topic: Literal["Politics", "Sports", "Technology", "Business", "Entertainment"]

class BatchResult(BaseModel):
    results: list[HeadlineLabel]

# ── LLM batch call ────────────────────────────────────────────────────────────
def classify_batch(headlines: list[str]) -> dict[str, str]:
    numbered = "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
    prompt = f"""Classify each headline into exactly one of: Politics, Sports, Technology, Business, Entertainment.

Definitions (be strict about boundaries):
- Politics: government, legislation, elections, diplomacy, policy, military, international relations
- Sports: games, tournaments, athletes, records, sports teams, coaches
- Technology: software, hardware, AI, cybersecurity, scientific research, space, gadgets
- Business: earnings, markets, stocks, corporate news, economics, companies, mergers, CEO, trade
- Entertainment: movies, music, TV shows, celebrity, awards, streaming, video games, culture

IMPORTANT BOUNDARY RULES:
- A tech COMPANY's financial news (earnings, stock, layoffs) → Business, NOT Technology
- A politician using social media → Politics, NOT Technology
- A sports team being sold → Business, NOT Sports
- AI/software product launches or research → Technology
- Only classify as Technology if the headline is primarily about a technical topic

Headlines:
{numbered}"""

    for attempt in range(5):
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o",#gpt-4o-mini is faster but less accurate, so we use gpt-4o for better accuracy in this classification task.
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=2000,
                response_format=BatchResult,
            )
            result = response.choices[0].message.parsed
            return {r.headline: r.topic for r in result.results}
        except Exception as e:
            wait = 10 * (attempt + 1) if "429" in str(e) else 5
            print(f"  Retry {attempt+1}: {e} — waiting {wait}s...")
            time.sleep(wait)
    return {}

# ── Main ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("q-topic-modeling-llm.csv")
df = df.dropna(subset=["headline"])           # drop blank lines
df["headline"] = df["headline"].str.strip()   # strip whitespace
df = df[df["headline"] != ""]                 # drop empty strings
print(f"Loaded {len(df)} valid headlines.")

# Resume support
cache = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}
headlines = df["headline"].tolist()
remaining = [h for h in headlines if h not in cache]# ie h not in cache dict's keys
print(f"{len(cache)} already classified, {len(remaining)} remaining.")

for i in range(0, len(remaining), BATCH_SIZE):
    batch = remaining[i : i + BATCH_SIZE]
    print(f"Batch {i//BATCH_SIZE+1} — headlines {i+1}…{i+len(batch)}")
    cache.update(classify_batch(batch))
    json.dump(cache, open(CACHE_FILE, "w"), indent=2)  # save progress(rewrite file)
    print(f"  ✓ {len(cache)}/{len(headlines)} done")
    time.sleep(0.5)

df["topic"] = df["headline"].map(cache) #add a new column "topic" to the DataFrame by mapping each headline to its classified topic using the cache dictionary.
print("\nTopic counts:")
print(df["topic"].value_counts().to_string())
print(f"\n✅ Technology count: {(df['topic'] == 'Technology').sum()}")

## though 41 it gave,..42 is the right answer, but it is possible that the LLM made a mistake on one headline, classifying it as Technology when it should be Business or vice versa. 
# The LLM's classification is based on its understanding of the headlines and the definitions provided, but it may not be perfect.