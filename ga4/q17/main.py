#NOTE: The zip file must be extracted and paste the contents of the extracted folder
#(ie scripts folder and README.md to q-17 folder and then delete the empty extracted folder )

#run python3 main.py

# note in the cache.json file all scripts were done using gpt-4o-mini (could use gpt-4o for better accuracy)
#it was giveing many false positives with gpt-4o-mini  but what i did was , for every file it returnded has_hallucination as false..i tried all of them in the portal, and finally
#script_409.py is the one with no hallucination (so the batch processing stopped at 450th script ie script_449.py)
import os, json, time
from openai import OpenAI
from pydantic import BaseModel

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPTS_DIR = "scripts"
CACHE_FILE  = "hallucination_cache.json"
BATCH_SIZE  = 50   # ~20 lines each → ~20 LLM calls total
MODEL       = "gpt-4o-mini" # swap to gpt-4o if accuracy < 95%

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)

# ── Pydantic structured output ────────────────────────────────────────────────
class FileResult(BaseModel):
    filename: str
    has_hallucination: bool  # True = bad, False = clean ✅

class BatchResult(BaseModel):
    results: list[FileResult]

# ── LLM batch call ────────────────────────────────────────────────────────────
def check_batch(batch: dict[str, str]) -> dict[str, bool]:
    files_block = "\n\n".join(f"### {fname} ###\n{code}" for fname, code in batch.items())

    prompt = f"""You are a strict Python expert auditor. For each script, detect ANY hallucinated method calls, 
function calls, or attribute accesses — things that sound plausible but do NOT exist in real Python libraries.

HALLUCINATIONS include both method calls AND attribute access. Be very strict.

Common examples (but not limited to these):
METHODS/FUNCTIONS:
- json.parse()             → FAKE (real: json.loads())
- df.drop_nulls()          → FAKE (real: df.dropna())
- requests.fetch()         → FAKE (real: requests.get())
- os.path.make_dirs()      → FAKE (real: os.makedirs())
- list.flatten()           → FAKE (doesn't exist)
- str.remove_punctuation() → FAKE (doesn't exist)
- dict.merge()             → FAKE (real: dict.update() or {{**a, **b}})

ATTRIBUTES:
- response.http_status     → FAKE (real: response.status_code)
- response.text_content    → FAKE (real: response.text)
- response.json_data       → FAKE (real: response.json())
- df.column_names          → FAKE (real: df.columns)
- exception.error_message  → FAKE (real: str(exception))

Set has_hallucination=false ONLY if you are 100% certain every single method, function, 
and attribute in the script is real and valid.

{files_block}"""


    for attempt in range(5):
        try:
            response = client.beta.chat.completions.parse(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=2000,
                response_format=BatchResult,
            )
            result = response.choices[0].message.parsed
            return {r.filename: r.has_hallucination for r in result.results}
        except Exception as e:
            wait = 10 * (attempt + 1) if "429" in str(e) else 5
            print(f"  Retry {attempt+1}: {e} — waiting {wait}s...")
            time.sleep(wait)
    return {}

# ── Main ──────────────────────────────────────────────────────────────────────
all_files = sorted(f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".py"))
print(f"Found {len(all_files)} scripts. Batch size: {BATCH_SIZE} → ~{-(-len(all_files)//BATCH_SIZE)} LLM calls.")

# Resume support
cache = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}
remaining = [f for f in all_files if f not in cache]
print(f"{len(cache)} already checked, {len(remaining)} remaining.")

# Process in batches — break as soon as we find the clean one
answer = next((f for f, bad in cache.items() if not bad), None)

for i in range(0, len(remaining), BATCH_SIZE):
    batch_files = remaining[i : i + BATCH_SIZE]
    batch = {f: open(os.path.join(SCRIPTS_DIR, f)).read() for f in batch_files}

    print(f"Batch {i//BATCH_SIZE+1} — checking {batch_files[0]} … {batch_files[-1]}")
    results = check_batch(batch)
    cache.update(results)
    json.dump(cache, open(CACHE_FILE, "w"), indent=2)

    clean_in_batch = [f for f, bad in results.items() if not bad]
    if clean_in_batch:
        answer = clean_in_batch[0]
        print(f"\n✅ Found it — breaking early! Answer: {answer}")
        break

    print(f"  ✓ {len(cache)}/{len(all_files)} checked, no clean script yet...")
    time.sleep(1)

if answer:
    print(f"\n✅ Answer: {answer}")
else:
    print("\n⚠️  No clean script found — try reducing BATCH_SIZE for more careful checking.")