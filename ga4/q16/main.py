#run python3 main.py
import json, csv, os, time
from openai import OpenAI
from pydantic import BaseModel, field_validator

# ── Config ────────────────────────────────────────────────────────────────────
BATCH_SIZE = 25
MODEL      = "gpt-4o-mini"  # swap to gpt-4o if accuracy < 95%

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)

# ── Pydantic structured output ────────────────────────────────────────────────
class DocMapping(BaseModel):
    doc_id: str
    entity_id: str

    @field_validator("entity_id")
    @classmethod
    def check_format(cls, v):
        if not (v.startswith("E") and v[1:].isdigit()):
            raise ValueError(f"Bad entity_id: {v!r}")
        return v

class BatchResult(BaseModel):
    mappings: list[DocMapping]

# ── LLM batch call ────────────────────────────────────────────────────────────
def call_llm_batch(batch_docs, entity_list_str):
    docs_block = "\n".join(
        f'DOC_ID={d["doc_id"]} | lang={d["language"]} | year={d["year"]} '
        f'| region={d.get("source_region","")} | name="{d["mentioned_name"]}" | text: {d["text"]}'
        for d in batch_docs
    )
    prompt = f"""You are an expert historian. Identify which entity each document refers to.

ENTITIES:
{entity_list_str}

RULES:
- Use year, region, and text — not just the name.
- Cross-lingual variants: Carlos=Karl=Charles=Carlo=Jean=Johann=Giovanni=Иван (context decides).
- ~8% of docs have name typos — rely on context.
- Ivan III ≠ Ivan IV. Catherine the Great ≠ Catherine de' Medici.

DOCUMENTS:
{docs_block}

Map every doc_id to an entity_id from the list above."""

    for attempt in range(5):
        try:
            response = client.beta.chat.completions.parse(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=1000,
                response_format=BatchResult,
            )
            result = response.choices[0].message.parsed
            return {m.doc_id: m.entity_id for m in result.mappings}
        except Exception as e:
            wait = 10 * (attempt + 1) if "429" in str(e) else 5
            print(f"  Attempt {attempt+1} failed: {e} — retrying in {wait}s...")
            time.sleep(wait)
    return {}

# ── Main ──────────────────────────────────────────────────────────────────────
docs     = [json.loads(l) for l in open("documents.jsonl") if l.strip()]
entities = list(csv.DictReader(open("entity_reference.csv")))

# Format entity list for prompt
entity_list_str = "\n".join(
    f"  {e['entity_id']}: {e.get('canonical_name', e.get('name',''))} "
    f"({e.get('birth_year','?')}–{e.get('death_year','?')}) {e.get('nationality') or e.get('region','')}"
    for e in entities
)
## this is my mistake , it has only canonical name,era, role, region etc, but ans passed
# Resume support — load any previously saved progress
cache_file = "progress_cache.json"
results = json.load(open(cache_file)) if os.path.exists(cache_file) else {}
remaining = [d for d in docs if d["doc_id"] not in results]
print(f"{len(results)} already done, {len(remaining)} remaining.")

# Process in batches
for i in range(0, len(remaining), BATCH_SIZE):
    batch = remaining[i : i + BATCH_SIZE]
    print(f"Batch {i//BATCH_SIZE+1} — {batch[0]['doc_id']} … {batch[-1]['doc_id']}")
    results.update(call_llm_batch(batch, entity_list_str))
    json.dump(results, open(cache_file, "w"), indent=2)  # save progress
    print(f"  ✓ {len(results)}/1000 done")
    time.sleep(1.5)

# Write final CSV
with open("output.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["doc_id", "entity_id"])
    for doc in sorted(docs, key=lambda d: d["doc_id"]):
        w.writerow([doc["doc_id"], results.get(doc["doc_id"], "UNKNOWN")])

print("output.csv written.")