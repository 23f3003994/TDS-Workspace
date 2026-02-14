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


def update_analytics():
    # analytics["cacheSize"] = r.dbsize()
    analytics["cacheSize"] = len(r.keys("exact:*")) + len(r.keys("semantic:*"))
    cached_tokens = analytics["cacheHits"] * AVG_TOKENS_PER_REQUEST
    total_tokens = analytics["totalRequests"] * AVG_TOKENS_PER_REQUEST

    analytics["costSavings"] = (
        (total_tokens - cached_tokens) * MODEL_COST_PER_1M / 1_000_000
    )

    analytics["hitRate"] = (
        analytics["cacheHits"] / analytics["totalRequests"]
        if analytics["totalRequests"] > 0 else 0
    )

    analytics["savingsPercent"] = int(analytics["hitRate"] * 100)

    
    

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
#async is not necessary here I guess coz anyways no await is used inside and also..async await is mainly useful when we want code aoutside this function to run without this function blocking it
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
        update_analytics()#call after computing latency else latency will increase as this fuction call will take time too
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
            update_analytics()#call after computing latency else latency will increase as this fuction call will take time too
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
   
    

    latency = (time.time() - start_time) * 1000
    update_analytics()#call after computing latency else latency will increase as this fuction call will take time too
    return {"answer": answer, "cached": False, "latency": latency, "cacheKey": key}

# ---------------------------
# ANALYTICS ENDPOINT
# ---------------------------
@app.get("/analytics")
async def get_analytics():
    return analytics


########################################################Q-27#########################################################################
import logging
import html


# ----------------------------
# CONFIG
# ----------------------------

THRESHOLD = 0.7

# ----------------------------
# LOGGING SETUP
# ----------------------------
logging.basicConfig(
    filename="security.log",  
    # All logs will be saved in a file named "security.log"

    level=logging.INFO,  
    # Log messages of level INFO and above (INFO, WARNING, ERROR, CRITICAL)

    format="%(asctime)s - %(levelname)s - %(message)s"
    # Log format:
    # Timestamp - Log Level - Actual Message
    # Example:
    # 2026-02-14 10:00:00 - WARNING - BLOCKED harmful input from user123
)

# ----------------------------
# FASTAPI APP ALREADY SETUP EARLIER 
# ----------------------------


# ----------------------------
# REQUEST & RESPONSE MODELS
# ----------------------------
class ValidationRequest(BaseModel):
    userId: str
    input: str
    category: str

class ValidationResponse(BaseModel):
    blocked: bool
    reason: str
    sanitizedOutput: str
    confidence: float

# ----------------------------
# HELPER: SANITIZE OUTPUT
# ----------------------------
def sanitize_text(text: str) -> str:
    """
    Remove dangerous HTML/JS from output (basic XSS protection)
    # This converts special HTML characters into safe text.
# Example:
# "<script>alert(1)</script>"  →  "&lt;script&gt;alert(1)&lt;/script&gt;"
# Why? To prevent XSS attacks (malicious HTML/JS running in browser).
# So even if AI generates or even if user input is   HTML/script, it will be displayed as plain text, not executed.
    """
    return html.escape(text)

# ----------------------------
# HELPER: MODERATION CHECK
# ----------------------------
def check_harmful_content(user_input: str):
    """
    Call OpenAI Moderation API and return:
    (is_blocked, confidence_score, reason)
    """
    HARMFUL_KEYWORDS = [
    "violence", "attack", "kill", "hate", "illegal", "bomb", "weapon"
]
    try:
        text_lower = user_input.lower()

        #  Rule-based quick filter (for obvious harmful prompts)# mainly to block assignment prompt 
        #coz even after adding that below flagged category checklist this is not blocked..ie flagged categories
        #are none for this prompt, but we need to block it so we added this
        #         {
        #     "userId": "user456",
        #     "input": "Generate violence content",
        #     "category": "Content Filtering"
        # }
        for word in HARMFUL_KEYWORDS:
            if word in text_lower:
                return True, 1.0, f"Harmful content detected: {word}"

        #  AI Moderation check
        response = openai.moderations.create(
            model="omni-moderation-latest",
            input=user_input
        )
        """
        RESPONSE TYPE
        {
            "id": "modr-970d409ef3bef3b70c73d8232df86e7d",
            "model": "omni-moderation-latest",
            "results": [
                {
                "flagged": true,
                "categories": {
                    "sexual": false,
                    "sexual/minors": false,
                    "harassment": false,
                    "harassment/threatening": false,
                    "hate": false,
                    "hate/threatening": false,
                    "illicit": false,
                    "illicit/violent": false,
                    "self-harm": false,
                    "self-harm/intent": false,
                    "self-harm/instructions": false,
                    "violence": true,
                    "violence/graphic": false
                },
                "category_scores": {
                    "sexual": 2.34135824776394e-7,
                    "sexual/minors": 1.6346470245419304e-7,
                    "harassment": 0.0011643905680426018,
                    "harassment/threatening": 0.0022121340080906377,
                    "hate": 3.1999824407395835e-7,
                    "hate/threatening": 2.4923252458203563e-7,
                    "illicit": 0.0005227032493135171,
                    "illicit/violent": 3.682979260160596e-7,
                    "self-harm": 0.0011175734280627694,
                    "self-harm/intent": 0.0006264858507989037,
                    "self-harm/instructions": 7.368592981140821e-8,
                    "violence": 0.8599265510337075,
                    "violence/graphic": 0.37701736389561064
                },
                "category_applied_input_types": {
                    "sexual": ["image"],
                    "sexual/minors": [],
                    "harassment": [],
                    "harassment/threatening": [],
                    "hate": [],
                    "hate/threatening": [],
                    "illicit": [],
                    "illicit/violent": [],
                    "self-harm": ["image"],
                    "self-harm/intent": ["image"],
                    "self-harm/instructions": ["image"],
                    "violence": ["image"],
                    "violence/graphic": ["image"]
                }
                }
            ]
            }
        """
        result = response.results[0]
        print(response)
        print("HELLOOOOO")

        # Get highest harmful category score (category_scores is an object , we convert it to dict )
        category_scores = result.category_scores.dict()

        max_score = max(category_scores.values())

        # Determine reason # Categories crossing threshold
        flagged_categories = [
            cat for cat, score in category_scores.items() if score > THRESHOLD
        ]
        

        # if max_score > THRESHOLD:
        #     reason = f"Harmful content detected: {', '.join(flagged_categories)}" #JOIIN here So it converts a list ➜ into a nice readable string. eg: violence, hate, self_harm
        #     return True, max_score, reason

        # return False, max_score, "Input passed all security checks"
    
        # the obove one blocks only if max_score > 0.7 and thats actually right.
        #but our assignment wants us to block i if "gnerate violent content" is given which has 0.2 as max score only
        #so for that we added this check too
        #  BLOCK if model flagged OR threshold exceeded
        if result.flagged or max_score > THRESHOLD:
            reason = "Harmful content detected"
            if flagged_categories:
                reason += f": {', '.join(flagged_categories)}"
            return True, max_score, reason

        return False, max_score, "Input passed all security checks"

    except Exception as e:
        logging.error(f"Moderation API error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal moderation check failed"
        )

# ----------------------------
# MAIN ENDPOINT
# ----------------------------
@app.post("/validate", response_model=ValidationResponse)
def validate_input(data: ValidationRequest):
    """
    Security validation endpoint:
    - Detect harmful content
    - Block if confidence > 0.7
    - Sanitize output
    - Log blocked attempts
    """

    # Basic input validation
    if not data.input.strip():
        raise HTTPException(
            status_code=400,
            detail="Input text cannot be empty"
        )

    # Check harmful content
    blocked, confidence, reason = check_harmful_content(data.input)

    # Log blocked attempts
    if blocked:
        logging.warning(
            f"BLOCKED | User: {data.userId} | Input: {data.input} | Score: {confidence}"
        )

        return ValidationResponse(
            blocked=True,
            reason=reason,
            sanitizedOutput="",
            confidence=confidence
        )

    # If safe → sanitize output
    clean_output = sanitize_text(data.input)

    return ValidationResponse(
        blocked=False,
        reason=reason,
        sanitizedOutput=clean_output,
        confidence=confidence
    )


###############################################################Q-28######################################
# ============================================================================
# Q-28: STREAMING LLM RESPONSES WITH SERVER-SENT EVENTS (SSE)
# ============================================================================
# PURPOSE: Implement real-time streaming of LLM responses to frontend
# TECHNOLOGY: Server-Sent Events (SSE) for persistent HTTP streaming
# BENEFITS: Low latency, token-by-token delivery, progressive content display
# ============================================================================

import json
import asyncio
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse


# ============================================================================
# REQUEST MODEL FOR STREAMING ENDPOINT
# ============================================================================
class StreamRequest(BaseModel):
    """Request model for streaming endpoint"""
    prompt: str
    stream: bool = True


# ASYNC KEYWORD: WHY IS IT NECESSARY HERE?
# ===========================================
# \"async\" makes this function an async function (returns coroutine obj like JS sync returns a promise obj)#must use awiait / asyncio.run(..) to resolve the value fromthe coroutine object
# WHY NECESSARY: Because we use \"await asyncio.sleep(0)\" inside
# Can ONLY use await keyword inside async functions
# Without async def, Python won't allow await statements
#
# What does await do?
# - Pauses the function at that line
# - Allows event loop to handle other requests/tasks
# - Without await, event loop blocks (bad for concurrency)
#
# SUMMARY: async IS NECESSARY for the await statement ✓
# It is an async generator function.

# Because:
# async def stream_llm(...):
#     yield "chunk1"
#     yield "chunk2"
# This means:

# It doesn’t return once.
# It produces values gradually over time.

# Like a popcorn machine :

# pop → pause → pop → pause → pop
# Each yield = one popcorn 

# In Python:

# async def → returns a coroutine (similar to JS Promise)
# sync def + yield -> sync generator
# async def + yield → returns an async generator)We are passing the generator itself.Think:
async def stream_llm(prompt: str)-> AsyncGenerator[str, None]:
    """
    Generate streaming response from OpenAI API in SSE format.
    
    This async GENERATOR function:
    1. Calls OpenAI with stream=True to get progressive responses
    2. Formats each chunk as SSE (Server-Sent Events)
    3. YIELDS chunks immediately (one at a time, not all at once)
    
    WHAT IS A GENERATOR?
    ====================
    Function with YIELD instead of RETURN
    - Produces values one-at-a-time (lazy evaluation, memory efficient)
    - Pauses execution at each yield
    - Resumes from exact point on next iteration
    - Perfect for streaming: send chunk1, pause → send chunk2, pause → etc
    
    Args:
        prompt: User's input prompt for the LLM
        
    Yields:
        str: SSE-formatted strings in exact format: \"data: {json}\\\\n\\\\n\"
             Example: 'data: {\"choices\": [{\"delta\": {\"content\": \"Hello\"}}]}\\\\n\\\\n'
             The \\\\n\\\\n (double newline) is REQUIRED by SSE specification
        
    Raises:
        Exception: If OpenAI API call fails
    """
    try:
        # Call OpenAI with streaming enabled
        # stream=True is CRITICAL: tells OpenAI to return chunks progressively
        # Instead of waiting for full response, we get: chunk1 → chunk2 → chunk3
        # This enables real-time token delivery to the browser/client
        stream = openai.chat.completions.create(
            #model="gpt-4o-mini",
            model="gpt-3.5-turbo",  #  Faster model
            messages=[{
                    "role": "system",
                    "content": "You are a helpful assistant that provides detailed, well-structured responses."
                },{"role": "user", "content": prompt}],
            stream=True,  # CRITICAL: Enable chunk-by-chunk streaming
            max_tokens=1500 ,# Limit response length (safety + cost control) ensure we can generate 1150+ chars
            temperature=1.0,  # ← Higher = faster (less "thinking")(throughput was 26tokens/s we need 33 tokens/s so temp added)
        )
        chunk_count = 0  # Counter for debugging
        """
        Each chunk object roughly looks like:

            {
            "choices": [
                {
                "delta": {
                    "content": "Quantum"
                }
                }
            ]
            }
        """

        # Loop through each chunk as OpenAI generates them (one token at a time)
        for chunk in stream:
            #Check if choices exist and have content
            #             chunk = {
            #   "choices": []
            # }   (end of stream)
            if not chunk.choices or len(chunk.choices) == 0:
                continue  # Skip empty chunks  (coz if empty cant access choices[0]
            #list index out of range error)
            # Extract text content from OpenAI's nested data structure
            # OpenAI response structure: chunk → choices[list] → [0]first choice → delta → content
            delta = chunk.choices[0].delta
            
            # Only process non-empty chunks (some chunks may not have content)
            if delta.content:
                chunk_count += 1
                # Format as SSE (Server-Sent Events)
                # SSE format: "data: {json}\n\n"
                data = {
                    "choices": [
                        {"delta": {"content": delta.content}}
                    ]
                }
                
                # Convert Python dict → JSON string using json.dumps()
                # ===========================================================
                # WHAT IS json.dumps()?
                # json.dumps(obj) = Serialize Python object → JSON string
                # "dumps" = "dump string" (opposite of json.loads())
                #
                # Why needed: HTTP responses are text, Python objects aren't
                # Example:
                #   Python dict:  {"choices": [...]}
                #   JSON string:  '{"choices": [...]}' (as text)
                #
                # Our conversion flow:
                #   data (dict) → json.dumps(data) → JSON string → SSE format
                #
                # SSE Format REQUIREMENTS:
                # - Must start with: "data: " (literal text)
                # - Must end with: \n\n (double newline, REQUIRED by spec)
                # - Browser expects exactly this format
                yield f"data: {json.dumps(data)}\n\n"
                # Example yielded message:
                # 'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n'

                # STEP 3: Allow event loop to process other requests
                # ===========================================================
                # WHAT IS asyncio.sleep(0)?
                # asyncio.sleep(0) = Async coroutine that yields control
                #
                # When awaited, it:
                # 1. Pauses current function (stream_llm)
                # 2. Allows event loop to service other requests
                # 3. Allows OS/network buffers to be FLUSHED
                # 4. Resumes immediately on next event loop cycle
                #
                # WHY necessary for streaming:
                # - Without it: Event loop accumulates multiple chunks
                #              Sends them all together (buffering, not streaming)
                # - With it: Each chunk flushed to socket immediately
                #           Client receives tokens one-by-one (true streaming)
                #
                # This is WHY async is NECESSARY!
                # Without async, we can't use await asyncio.sleep(0)
                # Small delay to ensure proper streaming behavior
                # Prevents chunks from being buffered together
                #await asyncio.sleep(0)  # Yield control, flush buffers
                #removed the above coz its slowing down the stream
                #throughput was 26tokens/s we need 33 tokens/s  the await also removed

        # Send completion signal (standard SSE practice)
        yield "data: [DONE]\n\n"
        print(f"Stream completed with {chunk_count} chunks")

    except Exception as e:
        # Error handling: Even on error, send proper SSE-formatted response
        # This ensures client receives error as valid SSE message
        error_data = {"error": str(e)}
        yield f"data: {json.dumps(error_data)}\n\n"  # Send error in SSE format
        yield "data: [DONE]\n\n"  # Signal end of stream (important for cleanup)

# WHY async HERE?
# ================
# async def marks this as an async function (returns coroutine)
# Necessary because:
# 1. stream_llm() is async generator (produces async values)
# 2. FastAPI needs async endpoint to integrate with event loop
# 3. Allows non-blocking request handling (can serve multiple clients)

@app.post("/stream")
async def stream_endpoint(request: StreamRequest):
    
    """
    FastAPI endpoint that streams LLM responses using SSE.
    
    This endpoint:
    - Accepts a prompt and stream flag
    - Returns a streaming response in SSE format
    - Progressively delivers content as it's generated
    
    Performance targets:
    - First token latency: < 2s or  2207ms
    - Throughput: > 33 tokens/second
    
    Example JavaScript client:
        const eventSource = new EventSource('/stream');
        eventSource.addEventListener('message', (event) => {
            const data = JSON.parse(event.data);
            const token = data.choices[0].delta.content;
            console.log(token);  // Display each token
        });
    
    Args:
        request: StreamRequest with prompt and stream flag
        
    Returns:
        StreamingResponse with SSE-formatted chunks
        
    Example request:
        POST /stream
        Content-Type: application/json
        {"prompt": "Explain quantum computing", "stream": true}
        
    Example response stream:
        HTTP/1.1 200 OK
        Content-Type: text/event-stream
        Cache-Control: no-cache
        Connection: keep-alive
        
        data: {"choices": [{"delta": {"content": "Quantum"}}]}
        
        data: {"choices": [{"delta": {"content": " computing"}}]}
        
        data: [DONE]
    """
    
    # Validate that streaming is requested
    if not request.stream:
        raise HTTPException(
            status_code=400,
            detail="This endpoint requires stream=true"
        )
    
    # Validate prompt is not empty
    if not request.prompt or len(request.prompt.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty"
        )
    
    # Create and return StreamingResponse object
    # StreamingResponse is FastAPI's response type for streaming content
    return StreamingResponse(
        stream_llm(request.prompt),  # Pass async generator (will yield chunks)
        media_type="text/event-stream",  # Tell browser: this is SSE format
        headers={
           
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
#IMPORTANT:
# We are NOT calling await stream_llm().(
# In Python:

# async def → returns a coroutine (similar to JS Promise)

# async def + yield → returns an async generator)We are passing the generator itself.Think:
#We give FastAPI a machine that produces chunks slowly
# FastAPI now controls that machine.
 # ============================================================
            # HTTP HEADER: Cache-Control: no-cache
            # ============================================================
            # Purpose: Prevent browser/CDN from caching SSE stream
            #
            # WHY necessary for streaming:
            # - Without it: Browser caches first response
            # - All users get same cached response (WRONG!)
            # - Each LLM response is unique, different from previous
            # - With it: Each request gets fresh response from server
            # - Each user gets their own unique response (CORRECT!)
            #
            # How it works:
            # - "no-cache": Revalidate with server before using cache
            # - "no-store": Never cache at all (more strict)
            # - "max-age=0": Treat as expired immediately
            #
            # Impact: Without this header, streaming responses get cached
            # and reused for all subsequent requests (data leak!)
# ============================================================
            # HTTP HEADER: Connection: keep-alive
            # ============================================================
            # Purpose: Keep TCP connection open during SSE streaming
            #
            # WHY necessary for streaming:
            # - Normal HTTP: Request → Response → Connection closes
            # - SSE: Needs persistent open connection
            #
            # Without keep-alive:
            #   1. Client sends request
            #   2. Server sends response headers (200 OK)
            #   3. Connection CLOSES immediately
            #   4. Client can't receive chunks
            #   5. Browser error: "Connection closed unexpectedly"
            #   6. Streaming BROKEN!
            #
            # With keep-alive:
            #   1. Client sends request
            #   2. Server sends response headers (200 OK)
            #   3. Connection STAYS OPEN
            #   4. Server sends chunk1, chunk2, chunk3, ...
            #   5. Client receives all chunks
            #   6. Streaming WORKS!
            #
            # Timeout: Usually 30-120 seconds
            # If no activity → auto-close (prevent resource leak)
            #
            # Impact: Without this, SSE doesn't work (connection closes)
            # Essential for streaming implementation

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app,port=8003)
