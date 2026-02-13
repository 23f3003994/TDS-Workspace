# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import time
import numpy as np
import openai
import os

# ---------------------------
# CONFIG
# ---------------------------
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")#.environ.get("ENV_VARIABLE_NAME", "default_value")

CACHE_MAX_SIZE = 1000  # max entries
CACHE_TTL = 24 * 60 * 60  # 24 hours in seconds
SEMANTIC_THRESHOLD = 0.95  # cosine similarity threshold

# ---------------------------
# DATA STRUCTURES
# ---------------------------
exact_cache = {}       # key: md5 hash, value: (answer, timestamp)
semantic_cache = {}    # key: embedding vector tuple, value: (answer, timestamp)

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

MODEL_COST_PER_1M = 1.20
AVG_TOKENS_PER_REQUEST = 2000

# ---------------------------
# REQUEST MODELS
# ---------------------------
class QueryRequest(BaseModel):
    query: str
    application: str

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
def normalize(text):
    """
    Normalize input text by removing leading/trailing whitespace and converting to lowercase.
    
    Args:
        text (str): The input text to normalize.
        
    Returns:
        str: The normalized text (lowercase and stripped).
    """
    return text.strip().lower()

def md5_hash(text):
    """
    Generate MD5 hash of the input text for exact match cache key generation.
    
    Args:
        text (str): The input text to hash.
        
    Returns:
        str: The MD5 hash hexadecimal representation.
    """
    # text.encode() - Converts the string into bytes using UTF-8 encoding
    # hashlib.md5() - Creates an MD5 hash object from the encoded bytes
    # .hexdigest() - Converts the hash object into a hexadecimal string representation
    return hashlib.md5(text.encode()).hexdigest()

def cosine_similarity(a, b):
    """
    Calculate cosine similarity between two embedding vectors.
    Used for semantic cache matching to find similar queries.
    
    Args:
        a (list or np.ndarray): First embedding vector.
        b (list or np.ndarray): Second embedding vector.
        
    Returns:
        float: Cosine similarity score between 0 and 1.
               Returns 0.0 if either vector has zero norm.
    """
    a = np.array(a)
    b = np.array(b)

    # Calculate the norm (magnitude) of each vector
    norm1 = np.linalg.norm(a)
    norm2 = np.linalg.norm(b)
    # Avoid division by zero
    if norm1 == 0 or norm2 == 0:
        return 0.0

    # Cosine similarity = dot product / (norm1 * norm2)
    return np.dot(a, b) / (norm1 * norm2)


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
    '''
    ===== RESPONSE STRUCTURE =====
        The response is a ChatCompletion object that looks like:
        {
          "id": "chatcmpl-123abc",
          "object": "chat.completion",
          "created": 1677649420,
          "model": "gpt-4o-mini",
          "choices": [
            {
              "index": 0,
              "message": {
                "role": "assistant",
                "content": "This text expresses optimistic emotions. The writing shows optimism and enthusiasm."
              },
              "finish_reason": "stop"
            }
          ],
          "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
          }
        }
        '''

    # Extract and return the text content from the response
    return response.choices[0].message.content

def compute_embedding(text):
    """
    Compute the embedding vector for semantic caching using OpenAI's embedding model.
    Used to represent queries as vectors for semantic similarity matching.
    
    Args:
        text (str): The text to compute embedding for.
        
    Returns:
        list: The embedding vector representing the input text.
    """
    # Call OpenAI embeddings API with text-embedding-3-small model
    response = openai.embeddings.create(
        model="text-embedding-3-small",  # Model supported by AI Pipe
        input=text
    )
    """
    -------------------------
    What the response looks like:
    -------------------------

    response is an OpenAI object similar to:

    {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": [0.0123, -0.0045, 0.9912, ...]
            },
            {
                "object": "embedding",
                "index": 1,
                "embedding": [-0.2211, 0.7712, -0.1123, ...]
            },
            ...
        ],
        "model": "text-embedding-3-small",
        "usage": {
            "prompt_tokens": 123,
            "total_tokens": 123
        }
    }

    Important parts:
    - response.data → list of embedding objects
    - Each item.embedding → list of floats (vector)
    - Length of embedding depends on model (e.g., 1536 dimensions)
    """

    # Extract and return the embedding vector from the response
    return response.data[0].embedding

def evict_cache(cache):
    """
    Evict the oldest entry from the cache when it exceeds CACHE_MAX_SIZE.
    Implements Least Recently Used (LRU) eviction policy based on timestamp.
    
    Args:
        cache (dict): The cache dictionary with entries in format {key: (value, timestamp)}.
    """
    # Check if cache size exceeds the maximum allowed
    if len(cache) > CACHE_MAX_SIZE:
        # Find the oldest key by timestamp (second element of the tuple)
        #cache[k][1] is the timestamp value
        oldest_key = min(cache, key=lambda k: cache[k][1])
        # Remove the oldest entry from the cache
        del cache[oldest_key]

def cleanup_ttl(cache):
    """
    Remove expired entries from the cache based on Time-To-Live (TTL).
    Deletes all entries older than CACHE_TTL seconds.
    time.time() in Python returns the current time in seconds since the Unix epoch (January 1, 1970, 00:00:00 UTC).
    
    Args:
        cache (dict): The cache dictionary with entries in format {key: (value, timestamp)}.
    """
    # Get current timestamp
    now = time.time()
    # Identify all keys with entries older than CACHE_TTL
    #for key, value(which is a tuple) in cache.items()
    keys_to_delete = [k for k, (_, ts) in cache.items() if now - ts > CACHE_TTL]
    # Delete all expired entries
    for k in keys_to_delete:
        del cache[k]

# ---------------------------
# FASTAPI APP
# ---------------------------
# Initialize FastAPI application for the Code Review Assistant with multi-level caching
app = FastAPI(title="Code Review Assistant with Caching")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all websites
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
    expose_headers=["*"] # expose all headers ie allow client side JS to access them
)




#NOTE qstn requires "/" to be the POST endpoint
@app.post("/")
async def main_query(request: QueryRequest):
    """
    Main query endpoint that processes user queries with multi-level caching strategy.
    Implements exact match caching and semantic similarity caching for performance optimization.
    time.time() in Python returns the current time in seconds since the Unix epoch (January 1, 1970, 00:00:00 UTC).
    
    Args:
        request (QueryRequest): Request object containing 'query' and 'application' fields.
        
    Returns:
        dict: Response containing:
            - answer (str): The generated or cached answer
            - cached (bool): Whether the response was from cache
            - latency (float): Response time in milliseconds
            - cacheKey (str): The cache key used for this query
    """
    # Record start time for latency measurement
    start_time = time.time()
    # Normalize the input query
    query = normalize(request.query)
    # Increment total request counter for analytics
    analytics["totalRequests"] += 1

    # -------- STRATEGY 1: Exact match cache --------
    # Generate MD5 hash of normalized query for exact match lookup
    key = md5_hash(query)
    # Clean up expired entries from both caches before lookups
    cleanup_ttl(exact_cache)
    cleanup_ttl(semantic_cache)

    # Check if query exists in exact match cache
    if key in exact_cache:
        # Retrieve cached answer and ignore timestamp
        #(answer of the query,timestamp)
        answer, _ = exact_cache[key]
        # Update analytics for cache hit
        analytics["cacheHits"] += 1
        # Calculate response latency in milliseconds
        latency = (time.time() - start_time) * 1000
        return {"answer": answer, "cached": True, "latency": latency, "cacheKey": key}

    # -------- STRATEGY 2: Semantic similarity cache --------
    # Compute embedding vector for the query
    query_emb = compute_embedding(query)
    # Search through semantic cache for similar queries
    
    #embedding vector tuple, value: (answer, timestamp) - in semantic_cache dict
    #coz list(mutable) cant be key so tuple format

    for emb_tuple, (ans, ts) in semantic_cache.items():
        # Calculate cosine similarity between query embedding and cached embeddings
        if cosine_similarity(query_emb, emb_tuple) > SEMANTIC_THRESHOLD:
            # Found a semantically similar cached query
            analytics["cacheHits"] += 1
            # Calculate response latency in milliseconds
            latency = (time.time() - start_time) * 1000
            return {"answer": ans, "cached": True, "latency": latency, "cacheKey": str(emb_tuple)}

    # -------- Cache miss: call OpenAI API --------
    # No cache hit found, call OpenAI API to generate new answer
    try:
        answer = call_openai(query)
    except Exception as e:
        # Return HTTP 500 error if API call fails
        raise HTTPException(status_code=500, detail=str(e))

    # -------- Update caches with new response --------
    # Store in exact match cache with current timestamp
    exact_cache[key] = (answer, time.time())
    # Store in semantic cache using embedding tuple as key
    #coz list(mutable) cant be key so tuple format
    semantic_cache[tuple(query_emb)] = (answer, time.time())

    # Apply cache eviction policies if caches exceed maximum size
    evict_cache(exact_cache)
    evict_cache(semantic_cache)

    # -------- Update analytics --------
    # Increment cache miss counter
    analytics["cacheMisses"] += 1
    # Update total cache size
    analytics["cacheSize"] = len(exact_cache) + len(semantic_cache)
    # Calculate estimated cost savings from cache hits
    cached_tokens = analytics["cacheHits"] * AVG_TOKENS_PER_REQUEST
    total_tokens = analytics["totalRequests"] * AVG_TOKENS_PER_REQUEST
    analytics["costSavings"] = (total_tokens - cached_tokens) * MODEL_COST_PER_1M / 1_000_000
    analytics["hitRate"] = (analytics["cacheHits"] / analytics["totalRequests"]) if analytics["totalRequests"] > 0 else 0
    analytics["savingsPercent"]= int(analytics["hitRate"] * 100)

    # Calculate total response latency in milliseconds
    latency = (time.time() - start_time) * 1000
    return {"answer": answer, "cached": False, "latency": latency, "cacheKey": key}

# ---------------------------
# ANALYTICS ENDPOINT
# ---------------------------
@app.get("/analytics")
async def get_analytics():
    """
    Endpoint to retrieve caching analytics and performance metrics.

    Returns:
        dict: Analytics data including:
            - hitRate (float): Proportion of requests served from cache.
                            Formula: cacheHits / totalRequests (range: 0 to 1)

            - totalRequests (int): Total number of queries received by the system
                                (both cached and uncached).

            - cacheHits (int): Number of queries that were served directly from cache
                            without calling the LLM.

            - cacheMisses (int): Number of queries not found in cache and therefore
                                required an LLM API call.

            - cacheSize (int): Current number of entries stored in the cache
                            (exact + semantic combined).

            - costSavings (float): Estimated money saved (in dollars) by avoiding
                                LLM calls for cached queries.

            - savingsPercent (float): Percentage of requests saved due to caching.
                                    Formula: (cacheHits / totalRequests) * 100

            - strategies (list): List of caching strategies implemented in the system
                                (e.g., exact match, semantic similarity, LRU, TTL).
    """

    return analytics

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app,port=8003)

