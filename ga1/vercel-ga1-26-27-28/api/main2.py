#redis implementation--- LOCAL TESTING NOT DONE YET
### FOR THIS TO RUN ON VERCEL MUST CHANGE HOST
# redis.Redis(
#     host="YOUR_UPSTASH_HOST",
#     port=6379,
#     password="YOUR_PASSWORD",
#     ssl=True
# )
#pip install fastapi uvicorn openai numpy redis
#redis serve  must be run in another terminal
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import time
import numpy as np
import openai
# import redis
import json
import os
from upstash_redis import Redis


# ---------------------------
# CONFIG
# ---------------------------
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")#.environ.get("ENV_VARIABLE_NAME", "default_value")

CACHE_MAX_SIZE = 1000
CACHE_TTL = 24 * 60 * 60
SEMANTIC_THRESHOLD = 0.95
MODEL_COST_PER_1M = 1.20
AVG_TOKENS_PER_REQUEST = 2000

# ---------------------------
# CONNECT TO REDIS
# ---------------------------
# r = redis.Redis(
#     host='localhost',  # Redis server host (hostname or IP). 'localhost' for local dev.
#     port=6379,         # Redis TCP port (default 6379).
#     db=0,              # Redis logical database index (0-15 by default). Use different
#                        # DB numbers to separate namespaces if needed.
#     decode_responses=True  # Return strings instead of bytes (auto-decodes UTF-8).
# )


r = Redis(
    url=os.environ["UPSTASH_REDIS_REST_URL"],
    token=os.environ["UPSTASH_REDIS_REST_TOKEN"]
)

# ---------------------------
# ANALYTICS
# ---------------------------
analytics = {
    "hitRate":0.0,
    "totalRequests": 0,
    "cacheHits": 0,
    "cacheMisses": 0,
    "cacheSize": 0,
    "costSavings": 0.0,
    'savingsPercent':0.0,
    "strategies": ["exact match", "semantic similarity", "LRU eviction", "TTL expiration"]
}

# ---------------------------
# REQUEST MODEL
# ---------------------------
class QueryRequest(BaseModel):
    query: str
    application: str

# ---------------------------
# UTILITIES
# ---------------------------
def normalize(text):
    """
    Normalize input text by stripping whitespace and converting to lowercase.

    Args:
        text (str): Input text to normalize.

    Returns:
        str: Normalized string.
    """
    return text.strip().lower()

def md5_hash(text):
    """
    Generate an MD5 hexadecimal hash for the provided text.

    This is used to create compact, fixed-size cache keys for exact-match lookups.

    Args:
        text (str): Input text to hash.

    Returns:
        str: 32-character hexadecimal MD5 digest.
    """
    return hashlib.md5(text.encode()).hexdigest()

def cosine_similarity(a, b):
    """
    Compute cosine similarity between two vectors.

    Args:
        a (array-like): First vector or embedding.
        b (array-like): Second vector or embedding.

    Returns:
        float: Cosine similarity score in range [-1, 1].
    """
    a = np.array(a)
    b = np.array(b)
    # guard against zero vectors to avoid division by zero
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return np.dot(a, b) / denom

def call_openai(query):
    """
    Call the OpenAI API to generate a response for the given query.
    Uses gpt-4o-mini model with deterministic output (temperature=0).
    
    Args:
        query (str): The user query to send to the OpenAI API.
        
    Returns:
        str: The generated response content from the API.
        
    Raises:
        Exception: If the API call fails or returns an error.
    """
    # Call OpenAI API with temperature=0 for deterministic responses
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
        temperature=0
    )

    # Extract and return the text content from the response
    return response.choices[0].message.content
    

def compute_embedding(text):
    """
    Compute an embedding vector for the given text using OpenAI embeddings API.

    Args:
        text (str): Text to compute embedding for.

    Returns:
        list: Embedding vector (list of floats).
    """
    response = openai.embeddings.create(
        model="text-embedding-3-small",  # Model supported by AI Pipe
        input=text
    )
    return response.data[0].embedding


# Redis-backed caching notes:
#no evict_cache(cache) (remove old keys (ie LRU keys) if cache length exceeds size) 
# or cleanup_ttl(cache) (remove keys whose ttl expired)

# This implementation uses Redis as the central cache store instead of in-process
# Python dictionaries (as in main.py). Because Redis provides native TTL support
# and server-side eviction policies, the client does not need to call
# `evict_cache(...)` or `cleanup_ttl(...)` here. Details:

# - Exact keys use the prefix `exact:{md5}` and store the raw answer string.

# - Semantic keys use the prefix `semantic:{md5}` and store a JSON string with
#   the format: {"answer": <str>, "embedding": <list_of_floats>}.

#here timestamp storing is not needed in the exact and semantic caches, coz they atre needed only to
#handle cleanup_ttl and evict_cache

# - When storing keys we pass `ex=CACHE_TTL` to `r.set(...)` so Redis expires
#   the keys automatically after `CACHE_TTL` seconds (TTL-based expiration).
# - Redis eviction (LRU / LFU / volatile-* settings) is configured on the Redis
#   server. If the server is configured to evict keys when memory limits are
#   reached, it will remove old keys according to that policy. Therefore, client
#   side eviction (like `evict_cache`) is unnecessary and could interfere with
#   Redis' persistence and clustering behavior.
#
# Comparison with main.py:
# - main.py uses in-process dicts (`exact_cache`, `semantic_cache`) and therefore
#   implements `evict_cache` and `cleanup_ttl` to manage memory and TTL locally.
# - main2.py relies on Redis to handle TTL and eviction, making the cache
#   persistent across multiple app instances and avoiding in-memory duplication.


# ---------------------------
# FASTAPI APP
# ---------------------------
app = FastAPI(title="Persistent Code Review Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all websites
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
    expose_headers=["*"] # expose all headers ie allow client side JS to access them
)
@app.post("/")
async def main_query(request: QueryRequest):
    """
    Main query endpoint using Redis-backed caches.

    Strategy:
    1. Normalize and compute MD5 key for exact-match lookup (prefix `exact:`).
    2. If no exact hit, compute embedding and scan Redis semantic keys
       (prefix `semantic:`) to find a semantically similar cached result.
    3. On cache miss, call OpenAI, store results in Redis with TTL, and return.

    Args:
        request (QueryRequest): Request containing `query` and `application`.

    Returns:
        dict: Response with `answer`, `cached`, `latency`, and `cacheKey`.
    """
    start_time = time.time()
    query = normalize(request.query)
    analytics["totalRequests"] += 1

    # Create deterministic, compact key for exact-match cache
    key = md5_hash(query)

    # -------- Exact match cache (Redis) --------
    # We use a Redis key with `exact:{md5}` that stores the answer string.
    # `r.get` returns the value as a decoded string because `decode_responses=True`.
    cached_answer = r.get(f"exact:{key}")
    if cached_answer:
        analytics["cacheHits"] += 1
        latency = (time.time() - start_time) * 1000
        return {"answer": cached_answer, "cached": True, "latency": latency, "cacheKey": key}

    # -------- Semantic cache --------
    query_emb = compute_embedding(query)
    # -------- Semantic cache (Redis) --------
    # Semantic entries are stored with keys like `semantic:{md5}` and the value
    # is a JSON string containing `answer` and `embedding` fields. We iterate
    # through matching keys using `scan_iter` to avoid blocking Redis on large
    # keyspaces (unlike `keys`, which is blocking). Each value is JSON-decoded
    # and the embedding is converted to a numpy array for similarity comparison.
    # for emb_key in r.scan_iter("semantic:*"):
    for emb_key in r.keys("semantic:*"):
        # json.loads() converts JSON string → Python dict 
         # Semantic entry format:
    # {
    #   "answer": <str>,
    #   "embedding": <list_of_floats>
    # }
        val = json.loads(r.get(emb_key))
        cached_emb = np.array(val["embedding"])
        if cosine_similarity(query_emb, cached_emb) > SEMANTIC_THRESHOLD:
            analytics["cacheHits"] += 1
            latency = (time.time() - start_time) * 1000
            return {"answer": val["answer"], "cached": True, "latency": latency, "cacheKey": emb_key}

    # -------- Cache miss: call OpenAI --------
    try:
        answer = call_openai(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # -------- Store new response in Redis with TTL --------
    # Exact match: store the raw answer string under `exact:{md5}`.
    # The `ex` parameter sets the key TTL (seconds) so Redis will auto-expire it.
    r.set(f"exact:{key}", answer, ex=CACHE_TTL)

    # Semantic entry format:
    # {
    #   "answer": <str>,
    #   "embedding": <list_of_floats>
    # }
    # We store the JSON string representation under `semantic:{md5}` so that
    # other processes can read the embedding and answer.
    #query_emb.tolist() was there it wont work i guess coz query_emb is already a list
    #and because Python list has no .tolist() method.
    semantic_val = {"answer": answer, "embedding": query_emb}
    r.set(f"semantic:{key}", json.dumps(semantic_val), ex=CACHE_TTL)

    analytics["cacheMisses"] += 1
    # analytics["cacheSize"] = r.dbsize()
    analytics["cacheSize"] = len(r.keys("exact:*")) + len(r.keys("semantic:*"))
    cached_tokens = analytics["cacheHits"] * AVG_TOKENS_PER_REQUEST
    total_tokens = analytics["totalRequests"] * AVG_TOKENS_PER_REQUEST
    analytics["costSavings"] = (total_tokens - cached_tokens) * MODEL_COST_PER_1M / 1_000_000
    analytics["hitRate"] = (analytics["cacheHits"] / analytics["totalRequests"]) if analytics["totalRequests"] > 0 else 0
    analytics["savingsPercent"]= int(analytics["hitRate"] * 100)

    latency = (time.time() - start_time) * 1000
    return {"answer": answer, "cached": False, "latency": latency, "cacheKey": key}

# ---------------------------
# ANALYTICS ENDPOINT
# ---------------------------
@app.get("/analytics")
async def get_analytics():
    return analytics



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app,port=8003)
