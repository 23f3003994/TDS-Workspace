
## there is no local testing folders for these 26,27,28 qstns
## its just this vercel folder
## so can do local testing by following the below steps

## MAIN2.PY WILL HAVE Q26-Q27-Q28 ENDPOINTS

## Prerequisites Setup

### Step 1: Install Dependencies 
```bash
# Install required packages globally or via uv
pip install fastapi uvicorn requests openai pydantic numpy 
# OR
uv pip install fastapi uvicorn requests openai pydantic numpy 

# Using uv (if uv is installed)
uv init project_nam
uv add fastapi uvicorn requests openai pydantic numpy 

# Add a requirements.txt file for deployment to vercel or railway
pip freeze > requirements.txt
```
### What I did
Created vercel-ga1-26-27-28 folder
	|-----------api
		        |------------main.py(not working with vercel-caching isuue-just locally run+cloufared)
            |------------main2.py(redis implementation-working with vercel)
	|-----------vercel.json
	|-----------requirements.txt

Change vercel.json
{
    "builds": [
        {
            "src": "api/main2.py",
            "use": "@vercel/python"
           
        }
    ],
    "routes": [
        { "src": "/(.*)", 
        "dest": "api/main2.py" }
    ]
}

for local testing either set this folder as a uv folder and use the above prerequisites step 
or 
since everything is actually installed globally..no need of them
 just add the below code in main.py (make sure to comment it before deploying)
  
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,port=8003)
```
and run 

```bash
python3 api/main.py

or

uvicorn api.main:app --reload --host 127.0.0.1 --port 8003
```


### Step 2: Set Environment Variables
Before running, you MUST set these environment variables:

```bash
# On PowerShell (Windows)
$env:OPENAI_API_KEY="***REMOVED***"
$env:OPENAI_BASE_URL="https://aipipe.org/openai/v1"

# On Linux/Mac (bash/zsh)
export OPENAI_API_KEY="***REMOVED***"
export OPENAI_BASE_URL="https://aipipe.org/openai/v1"

export UPSTASH_REDIS_REST_URL="***REMOVED***"
export UPSTASH_REDIS_REST_TOKEN="***REMOVED***"
```

---

## Running Locally

### Option A: Using Python directly (Fast - if dependencies installed globally but must have option c __name__ code)
```bash
# Terminal 1: Run the FastAPI server
python3 api/main.py
# Server runs on http://127.0.0.1:8003
```

### Option B: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn api.main:app --reload --host 127.0.0.1 --port 8003

# If uvicorn is not installed globally, use uv:
uv run uvicorn api.main:app --reload --host 127.0.0.1 --port 8003
```

### Option C: Using main.py with uvicorn programmatically
```python
# Add this to the end of main.py:  #DONT FORGET TO COMMENT BEFORE DEPLOMENT
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,port=8003)

# Then run:
python3 api/main.py
# OR
uv run api/main.py
```
---

## Final Deployment Structure for Vercel

## IN VERCEL WEBSITE DONT FORRGET TO GO TO
settings->environment variables->edit them and link to project ->MUST PRESS ENTER
## step- 1
main.py
requirements.txt
vercel.json
main.py:
app = FastAPI()


## step- 2
#dont put
```python
if __name__==__main__:
 uvicorn.run(..)

#use

@app.on_event("startup")
async def startup_event():
    load_documents()
    global document_embeddings
    ...
```

## step-3
```bash
#run from the project folder
vercel    #for preview deployment
vercel --prod #for prod deployment
```
OR

go to vercel site-> create new projet->import from github or paste this project folder's github url-> set env vars -> deploy


## builds section
``` json
{
  "src": "api/main.py",
  "use": "@vercel/python"
}
```

Meaning:
-	Entry file = api/main.py
-	Runtime = Python (managed by Vercel)
-	Vercel will turn this file into a serverless function


## routes section
```json
{
  "src": "/(.*)",
  "dest": "api/main.py"
}
```
This is a wildcard route.
It means:
-	/
-	/users
-	/items/123
-	/anything

 ** All requests go to main.py, and FastAPI decides which endpoint handles them.
Without this → your API won’t respond properly. **

## Project Architecture: main.py vs main2.py

Below are concise architecture notes for the two entrypoints included in this folder and the related Redis-backed variant. These are appended for developer reference and do not modify any of the instructions above.

- **`main.py` (in-process caching)**
  - Framework: FastAPI application that runs in-process.
  - Cache strategy: Two in-memory Python dictionaries:
    - `exact_cache`: keys are MD5 hashes of normalized queries, values are tuples `(answer, timestamp)`.
    - `semantic_cache`: keys are embedding tuples, values are tuples `(answer, timestamp)`.
  - Eviction & expiration: Client-side functions `evict_cache(...)` (LRU by timestamp) and `cleanup_ttl(...)` (TTL-based removal) are used to keep memory bounded.
  - Pros: Simple, no external dependencies, fast lookups within a single process.
  - Cons: Not shared across multiple instances, not persistent across restarts, memory limited to the process.

- **`main2.py` (Redis-backed caching)**
  - Framework: FastAPI with Redis used as the cache store.
  - Cache strategy: Redis keys with prefixes to separate semantics:
    - `exact:{md5}` → stores the raw answer string. `r.set(..., ex=CACHE_TTL)` is used so Redis auto-expires the key.
    - `semantic:{md5}` → stores a JSON string with the format `{ "answer": <str>, "embedding": <list_of_floats> }`.
  - Eviction & expiration: Relies on Redis server for TTL (`ex` argument) and server-side eviction policies (LRU/LFU) — thus `evict_cache(...)` and `cleanup_ttl(...)` are intentionally not used in `main2.py`.
  - Semantic lookup: Iterates keys via `r.scan_iter("semantic:*")`, decodes JSON, converts embedding to a numeric array and computes cosine similarity to decide semantic cache hits.
  - Pros: Shared cache across processes, persistent (depending on Redis config), scalable for multiple app instances.
  - Cons: Requires running Redis, network latency for cache access, requires careful key and memory management on Redis server.

Notes / Why both exist:
- Use `main.py` for quick local testing or single-process deployments without external infrastructure.
- Use `main2.py` when you need a persistent or distributed cache (multiple instances, horizontal scaling) and are able to provision a Redis instance.

See also the README in the related folder for similar notes: [ga1/vercel-ga1-q-19/README.md](ga1/vercel-ga1-q-19/README.md)

---

### Flowchart Architecture (visual)

Below are flowchart-style diagrams (Mermaid) that show request flows for both `main.py` and `main2.py`.

```mermaid
flowchart LR
  Client[Client / Caller]
  subgraph MainInProc [main.py - In-process cache]
    direction TB
    FastAPI_main[FastAPI (main.py)]
    InProcCache[In-memory caches\n- exact_cache\n- semantic_cache]
    AnalyticsA[analytics dict]
  end

  subgraph MainRedis [main2.py - Redis-backed cache]
    direction TB
    FastAPI_main2[FastAPI (main2.py)]
    RedisSrv[Redis server]\n- exact:{md5}\n- semantic:{md5}
    AnalyticsB[analytics (uses Redis dbsize etc.)]
  end

  Client --> FastAPI_main
  FastAPI_main --> InProcCache
  InProcCache --> OpenAI[OpenAI API (LLM / embeddings)]
  FastAPI_main --> AnalyticsA

  Client --> FastAPI_main2
  FastAPI_main2 --> RedisSrv
  RedisSrv --> OpenAI
  FastAPI_main2 --> AnalyticsB
```

Notes:
- `main.py` uses in-memory Python dicts for `exact_cache` and `semantic_cache`, with client-side `evict_cache()` and `cleanup_ttl()` for eviction and TTL handling.
- `main2.py` delegates caching to Redis using key prefixes `exact:{md5}` and `semantic:{md5}` and sets `ex=CACHE_TTL` so Redis auto-expires keys.
- Semantic caching stores embeddings and answers; semantic lookup computes cosine similarity between query embedding and cached embeddings.

This visual gives a quick overview of where caching and API calls occur for both variants.



## API Models Documentation (for `main.py` and `main2.py`)

This project contains two API variants. Both expose a single POST query endpoint (root `/`) and an analytics GET endpoint (`/analytics`). The request and response models are small and consistent between `main.py` and `main2.py`.

### QueryRequest (Request Body)

Both `main.py` and `main2.py` define the same request model used by the POST `/` endpoint:

```python
class QueryRequest(BaseModel):
    query: str        # The user's query text (required)
    application: str  # Application identifier or caller name (optional string used for analytics)
```

Parameters explained:
- `query` (required): The text to search/answer. It will be normalized (trimmed and lowercased) before processing.
- `application` (optional): A free-form string to help identify the caller or application in analytics.

Example curl request (POST `/`):
```bash
curl -X POST http://127.0.0.1:8003/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the difference between caching strategies", "application": "test-client"}'
```

Example curl request (GET `/analytics`):
```bash
curl -X GET http://127.0.0.1:8003/analytics
```


### QueryResponse (Response Body)

Both implementations return a JSON object with the following fields:

```json
{
  "answer": "...",     // Generated or cached answer string
  "cached": true|false, // Whether the response came from cache
  "latency": 123.45,    // Round-trip time in milliseconds
  "cacheKey": "..."    // Identifier for cache hit or stored key
}
```

Field details:
- `answer` (string): The generated text from OpenAI or the cached answer.
- `cached` (boolean): `true` if returned from cache (exact or semantic match), `false` if generated by the LLM.
- `latency` (float): Time elapsed for request processing in milliseconds.
- `cacheKey` (string): For `main.py` this is the MD5 hash key; for `main2.py` this is the Redis key used (e.g. `semantic:<md5>` or `exact:<md5>`).

### Analytics Response (`GET /analytics`)

Both files expose a simple analytics object with these keys:

```json
{
  "totalRequests": 0,
  "cacheHits": 0,
  "cacheMisses": 0,
  "cacheSize": 0,
  "costSavings": 0.0,
  "strategies": ["exact match","semantic similarity","LRU eviction","TTL expiration"]
}
```


Notes about differences between `main.py` and `main2.py` (important for model consumers and maintainers):

- `main.py` (in-process caches):
  - Uses two Python dicts: `exact_cache` and `semantic_cache`.
  - `exact_cache` keys: MD5 hash of normalized query; values: `(answer, timestamp)`.
  - `semantic_cache` keys: tuple(embedding); values: `(answer, timestamp)`.
  - Eviction and TTL are handled in-process via `evict_cache(...)` (LRU) and `cleanup_ttl(...)` (TTL) functions.

- `main2.py` (Redis-backed cache):
  - Uses Redis as the cache. Keys are prefixed to indicate type:
    - `exact:{md5}` → raw answer string
    - `semantic:{md5}` → JSON string `{ "answer": <str>, "embedding": <list_of_floats> }`
  - When storing values `main2.py` sets `ex=CACHE_TTL`, so Redis handles TTL and optional server-side eviction. There is no in-process `evict_cache(...)` or `cleanup_ttl(...)` used.
  - Semantic embeddings are stored as lists in JSON so they can be reloaded and compared by other processes.

These model definitions should help you construct requests and parse responses for either variant. The behavior you observe (cache hit vs miss) depends on which implementation you deploy.

---

## Processing Pipeline

When you make a search request, here's what happens:

1. **Query Reception** → API receives SearchRequest
2. **Query Embedding** → Query converted to vector using OpenAI (latency: ~50-100ms)
3. **Vector Search** → Find top k most similar documents using cosine similarity (latency: ~50-200ms)
4. **LLM Re-ranking** (if enabled) → Use GPT-4o-mini to score relevance of candidates (latency: ~100-200ms)
5. **Result Sorting** → Sort by final scores (highest first)
6. **Response Return** → Return top rerankK results as SearchResponse

---

## How It Works - Step by Step

1. **Query Reception**: API receives search query
2. **Embedding Generation**: Query converted to embeddings using OpenAI API
3. **Cosine Similarity**: Compares query embedding to all document embeddings, returns top 12
4. **LLM Re-ranking**: Batched processing using GPT-4o-mini to re-rank and filter
5. **Result Return**: Returns top 7 most semantically relevant results

---
