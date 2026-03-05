# """
# Cross-Lingual Entity Disambiguation Pipeline
# =============================================
# Strategy: Batch 25 docs per LLM call → ~40 total calls instead of 1000.
# Progress is saved after each batch so you can resume if interrupted.
# """

# import json
# import csv
# import os
# import time
# from openai import OpenAI
# from pydantic import BaseModel, field_validator

# # ── Config ────────────────────────────────────────────────────────────────────
# DOCUMENTS_FILE   = "documents.jsonl"
# ENTITIES_FILE    = "entity_reference.csv"
# OUTPUT_FILE      = "output.csv"
# PROGRESS_FILE    = "progress_cache.json"   # resume support
# BATCH_SIZE       = 25                      # docs per LLM call (~40 calls total)
# MODEL            = "gpt-4o-mini"           # fast + cheap; swap to gpt-4o for max accuracy
# RETRY_LIMIT      = 5
# RETRY_DELAY      = 10                      # seconds between retries on rate limit

# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY", ""),
#     base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
# )

# # ── Load Data ─────────────────────────────────────────────────────────────────
# def load_documents(path):
#     docs = []
#     with open(path, "r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if line:
#                 docs.append(json.loads(line))
#     print(f"Loaded {len(docs)} documents.")
#     return docs

# def load_entities(path):
#     with open(path, "r", encoding="utf-8") as f:
#         entities = list(csv.DictReader(f))
#     print(f"Loaded {len(entities)} entities.")
#     return entities

# def format_entity_list(entities):
#     """Format entity reference as a compact string for the prompt."""
#     lines = []
#     for e in entities:
#         # Include all fields that help with disambiguation
#         parts = [f"  {e['entity_id']}: {e.get('canonical_name', e.get('name', ''))}"]
#         if e.get('birth_year') or e.get('death_year'):
#             parts.append(f"({e.get('birth_year','?')}–{e.get('death_year','?')})")
#         if e.get('nationality') or e.get('region'):
#             parts.append(e.get('nationality') or e.get('region',''))
#         if e.get('description') or e.get('role'):
#             parts.append(e.get('description') or e.get('role',''))
#         lines.append(" ".join(parts))
#     return "\n".join(lines)

# # ── Pydantic Models ───────────────────────────────────────────────────────────
# class DocMapping(BaseModel):
#     doc_id: str
#     entity_id: str

#     @field_validator("entity_id")
#     @classmethod
#     def entity_id_format(cls, v):
#         """Ensure entity_id looks like E001–E099."""
#         if not v.startswith("E") or not v[1:].isdigit():
#             raise ValueError(f"Invalid entity_id format: {v!r}")
#         return v

# class BatchResult(BaseModel):
#     mappings: list[DocMapping]

# # ── LLM Call ──────────────────────────────────────────────────────────────────
# def call_llm_batch(batch_docs, entity_list_str):
#     """
#     Send a batch of documents to the LLM using Pydantic structured output.
#     Returns a dict: {doc_id: entity_id}
#     """
#     doc_lines = []
#     for doc in batch_docs:
#         doc_lines.append(
#             f'DOC_ID={doc["doc_id"]} | lang={doc["language"]} | year={doc["year"]} '
#             f'| region={doc.get("source_region","")} | name_mentioned="{doc["mentioned_name"]}" '
#             f'| text: {doc["text"]}'
#         )
#     docs_block = "\n".join(doc_lines)

#     prompt = f"""You are an expert historian and polyglot. Your job is to identify which historical entity each document refers to.

# ENTITY REFERENCE LIST (19 entities):
# {entity_list_str}

# IMPORTANT DISAMBIGUATION RULES:
# - Use the year, region, and document text as context clues — not just the name.
# - Names vary across languages: Carlos/Karl/Charles/Carlo/Jean/Johann/Giovanni/Иван all refer to different people depending on context.
# - Watch for typos (~8% of docs have character swaps in names — rely on context instead).
# - "Ivan III" and "Ivan IV" are DIFFERENT people. "Catherine the Great" ≠ "Catherine de' Medici".
# - Match the entity whose era AND region best fit the document.

# DOCUMENTS TO CLASSIFY:
# {docs_block}

# Return a mapping for every doc_id above. Entity IDs must exactly match the reference list (e.g. E001, E017).
# """

#     for attempt in range(RETRY_LIMIT):
#         try:
#             # response_format=BatchResult tells the API to return structured JSON
#             # that is guaranteed to parse into our Pydantic model — no regex needed.
#             response = client.beta.chat.completions.parse(
#                 model=MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0,
#                 max_tokens=1000,
#                 response_format=BatchResult,
#             )
#             # .parsed gives us a fully validated BatchResult instance
#             batch_result: BatchResult = response.choices[0].message.parsed
#             return {m.doc_id: m.entity_id for m in batch_result.mappings}

#         except Exception as e:
#             err_str = str(e).lower()
#             if "rate limit" in err_str or "429" in err_str:
#                 wait = RETRY_DELAY * (attempt + 1)
#                 print(f"  Rate limit hit. Waiting {wait}s before retry {attempt+1}/{RETRY_LIMIT}...")
#                 time.sleep(wait)
#             else:
#                 print(f"  LLM error on attempt {attempt+1}: {e}")
#                 if attempt < RETRY_LIMIT - 1:
#                     time.sleep(5)

#     print(f"  Failed after {RETRY_LIMIT} attempts. Returning empty for this batch.")
#     return {}

# # ── Progress Cache ────────────────────────────────────────────────────────────
# def load_progress():
#     if os.path.exists(PROGRESS_FILE):
#         with open(PROGRESS_FILE, "r") as f:
#             data = json.load(f)
#         print(f"Resuming from cache: {len(data)} docs already processed.")
#         return data
#     return {}

# def save_progress(results_dict):
#     with open(PROGRESS_FILE, "w") as f:
#         json.dump(results_dict, f, indent=2)

# # ── Main Pipeline ─────────────────────────────────────────────────────────────
# def run_pipeline():
#     docs     = load_documents(DOCUMENTS_FILE)
#     entities = load_entities(ENTITIES_FILE)
#     entity_list_str = format_entity_list(entities)

#     # Load any previously saved progress (resume support)
#     results = load_progress()

#     # Filter out already-processed docs
#     remaining = [d for d in docs if d["doc_id"] not in results]
#     print(f"Docs remaining: {len(remaining)}")

#     # Process in batches
#     total_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE
#     for batch_num, i in enumerate(range(0, len(remaining), BATCH_SIZE), 1):
#         batch = remaining[i : i + BATCH_SIZE]
#         print(f"Batch {batch_num}/{total_batches} — processing {len(batch)} docs "
#               f"({batch[0]['doc_id']} … {batch[-1]['doc_id']})...")

#         batch_result = call_llm_batch(batch, entity_list_str)

#         # Merge into results
#         for doc_id, entity_id in batch_result.items():
#             results[doc_id] = entity_id.strip()

#         # Save progress after every batch
#         save_progress(results)
#         print(f"  ✓ Got {len(batch_result)} mappings. Total so far: {len(results)}/1000")

#         # Small polite delay between batches to avoid rate limits
#         if batch_num < total_batches:
#             time.sleep(1.5)

#     # ── Validation ────────────────────────────────────────────────────────────
#     valid_ids  = {e["entity_id"] for e in entities}
#     all_doc_ids = {d["doc_id"] for d in docs}
#     missing     = all_doc_ids - results.keys()
#     bad_ids     = {did: eid for did, eid in results.items() if eid not in valid_ids}

#     if missing:
#         print(f"\n⚠️  Missing {len(missing)} doc_ids: {sorted(missing)[:10]}...")
#     if bad_ids:
#         print(f"\n⚠️  {len(bad_ids)} invalid entity_ids: {list(bad_ids.items())[:5]}...")

#     # ── Write Output CSV ──────────────────────────────────────────────────────
#     # Sort by doc_id to keep output tidy
#     ordered_docs = sorted(docs, key=lambda d: d["doc_id"])

#     with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=["doc_id", "entity_id"])
#         writer.writeheader()
#         for doc in ordered_docs:
#             doc_id = doc["doc_id"]
#             entity_id = results.get(doc_id, "UNKNOWN")
#             writer.writerow({"doc_id": doc_id, "entity_id": entity_id})

#     print(f"\n✅ Output written to {OUTPUT_FILE} ({len(ordered_docs)} rows)")
#     print(f"   Valid mappings: {len(ordered_docs) - len(missing) - len(bad_ids)}/1000")

# if __name__ == "__main__":
#     run_pipeline()


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