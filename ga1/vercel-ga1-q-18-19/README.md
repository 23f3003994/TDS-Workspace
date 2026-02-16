# Q-18: Build Semantic Search with Re-ranking & Q-19: Vector Databases
## Final Deployment Structure for Vercel

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



## Q-18
## project explanation

Architecture

Query
   ↓
Embedding
   ↓
Cosine similarity (top 12)
   ↓
LLM rerank (batched)
   ↓
Return top 7


# Semantic Search - Running Guide

## Project Overview
This is a semantic search application that:
1. Takes a user query as input
2. Converts it to embeddings
3. Finds similar documents using cosine similarity (top 12)
4. Re-ranks results using LLM (batched processing)
5. Returns top 7 most relevant results

---

## Prerequisites Setup

### Step 1: Install Dependencies
```bash
# Install required packages globally or via uv
pip install fastapi uvicorn requests openai pydantic numpy 
# OR
uv pip install fastapi uvicorn requests openai pydantic numpy 

# Using uv (if uv is installed)
uv init semantic_search
uv add fastapi uvicorn requests openai pydantic numpy 

# Add a requirements.txt file for deployment to vercel or railway
pip freeze > requirements.txt
```

### Step 2: Set Environment Variables
Before running, you MUST set these environment variables:

```bash
# On PowerShell (Windows)
$env:OPENAI_API_KEY="#################################"
$env:OPENAI_BASE_URL="https://aipipe.org/openai/v1"

# On Linux/Mac (bash/zsh)
export OPENAI_API_KEY="#################################"
export OPENAI_BASE_URL="https://aipipe.org/openai/v1"
```

---

## Running Locally

### Option A: Using Python directly (Fast - if dependencies installed globally but must have option c __name__ code)
```bash
# Terminal 1: Run the FastAPI server
python3 main.py
# Server runs on http://127.0.0.1:8000
```

### Option B: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# If uvicorn is not installed globally, use uv:
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Option C: Using main.py with uvicorn programmatically
```python
# Add this to the end of main.py:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Then run:
python3 main.py
# OR
uv run main.py
```

---

## Testing the API Locally

### Step 1: Verify Server is Running
Open browser and go to: `http://127.0.0.1:8000/docs` (Swagger UI)

### Step 2: Test the /search endpoint
```bash
# Terminal 2: Send a search query
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "climate change",
    "k": 15,
    "rerank": true,
    "rerankK": 5
  }'
```

### Expected Response:
```json
{
  "results": [
    {
      "id": 42,
      "score": 0.92,
      "content": "News article about climate change and agriculture impacts...",
      "metadata": {
        "topic": "climate change",
        "source": "news_articles"
      }
    },
    {
      "id": 7,
      "score": 0.88,
      "content": "Another relevant document about environmental science...",
      "metadata": {
        "topic": "environment",
        "source": "news_articles"
      }
    }
  ],
  "reranked": true,
  "metrics": {
    "latency": 285,
    "totalDocs": 104,
    "searchLatency": 145,
    "rerankLatency": 140
  }
}
```

---

## API Models Documentation

### SearchRequest (Request Body)

The request model defines what parameters you send to the `/search` endpoint:

```python
class SearchRequest(BaseModel):
    query: str                          # The search query text
    k: int = Field(12, ge=1, le=100)   # Number of initial similar docs to retrieve (default: 12, range: 1-100)
    rerank: bool = True                # Whether to apply LLM re-ranking (default: True)
    rerankK: int = Field(7, ge=1)      # Number of final results after re-ranking (default: 7, min: 1)
```

**Parameters Explained:**
- **query** (required): The search query string
  - Example: `"climate change impacts on agriculture"`
  
- **k** (optional): Initial number of documents to retrieve using vector similarity
  - Default: 12
  - Range: 1 to 100
  - Higher k = more documents to consider before re-ranking
  
- **rerank** (optional): Whether to use LLM for re-ranking results
  - Default: True (uses OpenAI GPT-4o-mini)
  - Set to False to skip re-ranking and return top k documents directly
  
- **rerankK** (optional): Final number of results to return after re-ranking
  - Default: 7
  - Minimum: 1
  - Note: `rerankK` must be ≤ `k`

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "climate change",
    "k": 15,
    "rerank": true,
    "rerankK": 5
  }'
```

---

### SearchResponse (Response Body)

The response model defines what the API returns:

```python
class SearchResponse(BaseModel):
    results: List[DocumentResult]      # List of search result documents
    reranked: bool                     # Whether LLM re-ranking was applied
    metrics: Dict[str, Any]            # Performance metrics and metadata
```

**Fields Explained:**

- **results**: List of DocumentResult objects
  - Contains the final search results
  - Each result includes: id, score, content, and metadata
  - Sorted by relevance (highest score first)
  
- **reranked**: Boolean indicating if LLM re-ranking was applied
  - True: Results were re-ranked using OpenAI
  - False: Results are raw vector similarity matches
  
- **metrics**: Dictionary with performance information
  - `latency`: Total request time in milliseconds
  - `searchLatency`: Vector similarity search time in ms
  - `rerankLatency`: LLM re-ranking time in ms
  - `totalDocs`: Total number of documents available

### DocumentResult (Individual Result)

Each result in the response contains:

```python
class DocumentResult(BaseModel):
    id: int                           # Unique document identifier
    score: float                      # Relevance score (0.0 to 1.0)
    content: str                      # The actual document text
    metadata: Dict[str, Any]          # Additional document information
```

**Example Response:**
```json
{
  "results": [
    {
      "id": 42,
      "score": 0.92,
      "content": "News article about climate change and agriculture impacts...",
      "metadata": {
        "topic": "climate change",
        "source": "news_articles"
      }
    },
    {
      "id": 7,
      "score": 0.88,
      "content": "Another relevant document about environmental science...",
      "metadata": {
        "topic": "environment",
        "source": "news_articles"
      }
    }
  ],
  "reranked": true,
  "metrics": {
    "latency": 285,
    "totalDocs": 104,
    "searchLatency": 145,
    "rerankLatency": 140
  }
}
```

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

## Exposing to Public with ngrok

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com or use package manager
```

### Step 2: Create ngrok tunnel (in another terminal)
```bash
# Terminal 3: Create public URL
ngrok http 8000
# This will give you a public URL like: https://xxxx-xx-xxx-xxx.ngrok.io
```

### Step 3: Test via Public URL
Go to: `https://xxxx-xx-xxx-xxx.ngrok.io/docs` (replace with your ngrok URL)

Or use curl:
```bash
curl -X POST https://xxxx-xx-xxx-xxx.ngrok.io/search \
  -H "Content-Type: application/json" \
  -d '{"query":"your search query here"}'
```

---

## Troubleshooting

### Issue: Permission/API Key Error
- **Solution**: Re-run the environment variable commands and verify they're set:
```bash
echo $env:OPENAI_API_KEY  # PowerShell
echo $OPENAI_API_KEY      # Linux/Mac
```
- If still failing, try running the command again

### Issue: Port 8000 already in use
- **Solution**: Use a different port:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### Issue: Dependencies not found
- **Solution**: Install them globally:
```bash
pip install fastapi uvicorn requests openai pydantic numpy
```

### Issue: Slow response with `uv run`
- **Solution**: Use `python3` directly if dependencies are installed globally:
```bash
python3 main.py
```

---

## Summary of Commands

| Task | Command |
|------|---------|
| Set API Key (PowerShell) | `$env:OPENAI_API_KEY="..."` |
| Run Server (Fast) | `python3 main.py` |
| Run Server (Auto-reload) | `uvicorn main:app --reload --host 127.0.0.1 --port 8000` |
| Open API Docs | `http://127.0.0.1:8000/docs` |
| Test Search | `curl -X POST http://127.0.0.1:8000/search` |
| Expose Publicly | `ngrok http 8000` |












## Q-19




## project explanation

Architecture

Query
   ↓
Embedding (OpenAI)
   ↓
Cosine Similarity (Vector Search)
   ↓
Return Top 3 Matches


# Similarity Search - Running Guide

## Project Overview
This is a simple similarity search application that:
1. Takes a list of documents and a search query as input
2. Converts both documents and query to embeddings
3. Finds the most similar documents using cosine similarity
4. Returns top 3 matching documents
5. **No LLM re-ranking** (kept simple and fast)

**Key Difference from Semantic Search**: Documents are provided per request (not pre-loaded), making it suitable for dynamic/user-provided content.

---

## Prerequisites Setup

### Step 1: Install Dependencies
```bash
# Install required packages globally or via uv
pip install fastapi uvicorn requests openai pydantic numpy
# OR
uv pip install fastapi uvicorn requests openai pydantic numpy

# Using uv (if uv is installed)
uv init similarity_search
uv add fastapi uvicorn requests openai pydantic numpy

# Add a requirements.txt file for deployment to vercel or railway
pip freeze > requirements.txt
```

### Step 2: Set Environment Variables
Before running, you MUST set these environment variables:

```bash
# On PowerShell (Windows)
$env:OPENAI_API_KEY="######################################"
$env:OPENAI_BASE_URL="https://aipipe.org/openai/v1"

# On Linux/Mac (bash/zsh)
export OPENAI_API_KEY="####################################"
export OPENAI_BASE_URL="https://aipipe.org/openai/v1"
```

---

## Running Locally

### Option A: Using Python directly (Fast - if dependencies installed globally)
```bash
# Terminal 1: Run the FastAPI server
python3 main.py
# Server runs on http://127.0.0.1:8001
```

### Option B: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8001

# If uvicorn is not installed globally, use uv:
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### Option C: Using main.py with uvicorn programmatically
```python
# main.py already includes:
if __name__ == "__main__":
    uvicorn.run(app, port=8001)

# Then run:
python3 main.py
# OR
uv run main.py
```

---

## Testing the API Locally

### Step 1: Verify Server is Running
Open browser and go to: `http://127.0.0.1:8001/docs` (Swagger UI)

### Step 2: Test the /similarity endpoint
```bash
# Terminal 2: Send a similarity search request
curl -X POST http://127.0.0.1:8001/similarity \
  -H "Content-Type: application/json" \
  -d '{
    "docs": [
      "Machine learning is a subset of artificial intelligence",
      "Python is a programming language",
      "The sky is blue and beautiful",
      "Deep learning uses neural networks",
      "FastAPI is a modern web framework"
    ],
    "query": "What is machine learning?"
  }'
```

### Expected Response:
```json
{
  "matches": [
    "Machine learning is a subset of artificial intelligence",
    "Deep learning uses neural networks",
    "FastAPI is a modern web framework"
  ]
}
```

The response returns the top 3 most semantically similar documents to the query.

---

## API Models Documentation

### SearchRequest (Request Body)

The request model defines what you send to the `/similarity` endpoint:

```python
class SearchRequest(BaseModel):
    docs: List[str]    # List of documents to search through
    query: str         # The search query
```

**Parameters Explained:**

- **docs** (required): List of document strings
  - Example: `["Document 1 content...", "Document 2 content...", ...]`
  - These are the documents you want to search through
  - Can be any number of documents
  
- **query** (required): The search query string
  - Example: `"Find documents about machine learning"`
  - Will be converted to an embedding and compared against all docs

**Example Requests:**

Simple search:
```bash
curl -X POST http://127.0.0.1:8001/similarity \
  -H "Content-Type: application/json" \
  -d '{
    "docs": ["AI is the future", "Python rocks", "Hello world"],
    "query": "artificial intelligence"
  }'
```

Large document search:
```bash
curl -X POST http://127.0.0.1:8001/similarity \
  -H "Content-Type: application/json" \
  -d '{
    "docs": [
      "First long document content...",
      "Second long document content...",
      "Third long document content...",
      "Fourth long document content..."
    ],
    "query": "specific topic to search for"
  }'
```

---

### SearchResponse (Response Body)

The response model contains the search results:

```python
class SearchResponse(BaseModel):
    matches: List[str]  # The top 3 most similar documents
```

**Fields Explained:**

- **matches**: List of the top 3 most similar document strings
  - Ordered by relevance (highest similarity first)
  - Contains the actual document text, not scores or IDs
  - Maximum length: 3 documents

**Example Response:**
```json
{
  "matches": [
    "Machine learning is a subset of artificial intelligence",
    "Deep learning uses neural networks for pattern recognition",
    "Artificial neural networks are inspired by biological neurons"
  ]
}
```

---

## Processing Pipeline

When you make a similarity search request, here's what happens:

1. **Request Reception** → API receives SearchRequest with docs and query
2. **Query Embedding** → Query converted to vector using OpenAI text-embedding-3-small
3. **Document Embeddings** → All provided documents converted to vectors
4. **Cosine Similarity** → Calculate similarity score between query and each document
5. **Sorting** → Sort documents by similarity score (highest first)
6. **Result Return** → Return top 3 most similar documents as SearchResponse

**Performance**: The entire process typically completes in 200-500ms depending on the number of documents.

---

## Exposing to Public with ngrok

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com or use package manager
```

### Step 2: Create ngrok tunnel (in another terminal)
```bash
# Terminal 3: Create public URL
ngrok http 8001
# This will give you a public URL like: https://xxxx-xx-xxx-xxx.ngrok.io
```

### Step 3: Test via Public URL
Go to: `https://xxxx-xx-xxx-xxx.ngrok.io/docs` (replace with your ngrok URL)

Or use curl:
```bash
curl -X POST https://xxxx-xx-xxx-xxx.ngrok.io/similarity \
  -H "Content-Type: application/json" \
  -d '{
    "docs": ["Your document 1", "Your document 2"],
    "query": "search query"
  }'
```

---

## Troubleshooting

### Issue: Permission/API Key Error
- **Solution**: Re-run the environment variable commands and verify they're set:
```bash
echo $env:OPENAI_API_KEY  # PowerShell
echo $OPENAI_API_KEY      # Linux/Mac
```
- If still failing, try running the command again

### Issue: Port 8001 already in use
- **Solution**: Use a different port:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8002
```

### Issue: Dependencies not found
- **Solution**: Install them globally:
```bash
pip install fastapi uvicorn requests openai pydantic numpy
```

### Issue: Empty matches returned
- **Solution**: Check if documents are similar enough to query
  - Try with documents that have more overlap with the query
  - Similarity threshold is based on cosine similarity (0-1 scale)

### Issue: Slow response
- **Solution**: For large number of documents (>100):
  - Reduce the number of documents per request
  - Consider batching requests
  - Typical: 50 docs = ~200-300ms, 500 docs = ~800-1200ms

---

## Summary of Commands

| Task | Command |
|------|---------|
| Set API Key (PowerShell) | `$env:OPENAI_API_KEY="..."` |
| Run Server (Fast) | `python3 main.py` |
| Run Server (Auto-reload) | `uvicorn main:app --reload --host 127.0.0.1 --port 8001` |
| Open API Docs | `http://127.0.0.1:8001/docs` |
| Test Similarity | `curl -X POST http://127.0.0.1:8001/similarity` |
| Expose Publicly | `ngrok http 8001` |

---

## Comparison: Similarity Search vs Semantic Search

| Feature | Similarity Search (q-19) | Semantic Search (q-18) |
|---------|-------------------------|----------------------|
| Documents | Provided per request | Pre-loaded from file |
| Endpoint | `/similarity` | `/search` |
| Top Results | Top 3 | Top 7 |
| Re-ranking | No | Yes (LLM-based) |
| Use Case | Dynamic content, ad-hoc search | Static document database |
| Speed | Faster (no re-ranking) | Slower (includes LLM) |
| Port | 8001 | 8000 |

---

## Running Locally

### Option A: Using Python directly (Fast - if dependencies installed globally)
```bash
# Terminal 1: Run the FastAPI server
python3 main.py
# Server runs on http://127.0.0.1:8001
```

### Option B: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8001

# If uvicorn is not installed globally, use uv:
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### Option C: Using main.py with uvicorn programmatically
```python
# Add this to the end of main.py:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

# Then run:
python3 main.py
# OR
uv run main.py
```

---

## Testing the API Locally

### Step 1: Verify Server is Running
Open browser and go to: `http://127.0.0.1:8001/docs` (Swagger UI)

### Step 2: Test the /search endpoint
```bash
# Terminal 2: Send a search query
curl -X POST http://127.0.0.1:8001/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "climate change",
    "k": 15,
    "rerank": true,
    "rerankK": 5
  }'
```

### Expected Response:
```json
{
  "results": [
    {
      "id": 42,
      "score": 0.92,
      "content": "News article about climate change and agriculture impacts...",
      "metadata": {
        "topic": "climate change",
        "source": "news_articles"
      }
    },
    {
      "id": 7,
      "score": 0.88,
      "content": "Another relevant document about environmental science...",
      "metadata": {
        "topic": "environment",
        "source": "news_articles"
      }
    }
  ],
  "reranked": true,
  "metrics": {
    "latency": 285,
    "totalDocs": 104,
    "searchLatency": 145,
    "rerankLatency": 140
  }
}
```

---

## API Models Documentation

### SearchRequest (Request Body)

The request model defines what parameters you send to the `/search` endpoint:

```python
class SearchRequest(BaseModel):
    query: str                          # The search query text
    k: int = Field(12, ge=1, le=100)   # Number of initial similar docs to retrieve (default: 12, range: 1-100)
    rerank: bool = True                # Whether to apply LLM re-ranking (default: True)
    rerankK: int = Field(7, ge=1)      # Number of final results after re-ranking (default: 7, min: 1)
```

**Parameters Explained:**
- **query** (required): The search query string
  - Example: `"climate change impacts on agriculture"`
  
- **k** (optional): Initial number of documents to retrieve using vector similarity
  - Default: 12
  - Range: 1 to 100
  - Higher k = more documents to consider before re-ranking
  
- **rerank** (optional): Whether to use LLM for re-ranking results
  - Default: True (uses OpenAI GPT-4o-mini)
  - Set to False to skip re-ranking and return top k documents directly
  
- **rerankK** (optional): Final number of results to return after re-ranking
  - Default: 7
  - Minimum: 1
  - Note: `rerankK` must be ≤ `k`

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8001/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "climate change",
    "k": 15,
    "rerank": true,
    "rerankK": 5
  }'
```

---

### SearchResponse (Response Body)

The response model defines what the API returns:

```python
class SearchResponse(BaseModel):
    results: List[DocumentResult]      # List of search result documents
    reranked: bool                     # Whether LLM re-ranking was applied
    metrics: Dict[str, Any]            # Performance metrics and metadata
```

**Fields Explained:**

- **results**: List of DocumentResult objects
  - Contains the final search results
  - Each result includes: id, score, content, and metadata
  - Sorted by relevance (highest score first)
  
- **reranked**: Boolean indicating if LLM re-ranking was applied
  - True: Results were re-ranked using OpenAI
  - False: Results are raw vector similarity matches
  
- **metrics**: Dictionary with performance information
  - `latency`: Total request time in milliseconds
  - `searchLatency`: Vector similarity search time in ms
  - `rerankLatency`: LLM re-ranking time in ms
  - `totalDocs`: Total number of documents available

### DocumentResult (Individual Result)

Each result in the response contains:

```python
class DocumentResult(BaseModel):
    id: int                           # Unique document identifier
    score: float                      # Relevance score (0.0 to 1.0)
    content: str                      # The actual document text
    metadata: Dict[str, Any]          # Additional document information
```

**Example Response:**
```json
{
  "results": [
    {
      "id": 42,
      "score": 0.92,
      "content": "News article about climate change and agriculture impacts...",
      "metadata": {
        "topic": "climate change",
        "source": "news_articles"
      }
    },
    {
      "id": 7,
      "score": 0.88,
      "content": "Another relevant document about environmental science...",
      "metadata": {
        "topic": "environment",
        "source": "news_articles"
      }
    }
  ],
  "reranked": true,
  "metrics": {
    "latency": 285,
    "totalDocs": 104,
    "searchLatency": 145,
    "rerankLatency": 140
  }
}
```

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

## Exposing to Public with ngrok

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com or use package manager
```

### Step 2: Create ngrok tunnel (in another terminal)
```bash
# Terminal 3: Create public URL
ngrok http 8001
# This will give you a public URL like: https://xxxx-xx-xxx-xxx.ngrok.io
```

### Step 3: Test via Public URL
Go to: `https://xxxx-xx-xxx-xxx.ngrok.io/docs` (replace with your ngrok URL)

Or use curl:
```bash
curl -X POST https://xxxx-xx-xxx-xxx.ngrok.io/search \
  -H "Content-Type: application/json" \
  -d '{"query":"your search query here"}'
```

---

## Troubleshooting

### Issue: Permission/API Key Error
- **Solution**: Re-run the environment variable commands and verify they're set:
```bash
echo $env:OPENAI_API_KEY  # PowerShell
echo $OPENAI_API_KEY      # Linux/Mac
```
- If still failing, try running the command again

### Issue: Port 8000 already in use
- **Solution**: Use a different port:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### Issue: Dependencies not found
- **Solution**: Install them globally:
```bash
pip install fastapi uvicorn requests openai pydantic numpy
```

### Issue: Slow response with `uv run`
- **Solution**: Use `python3` directly if dependencies are installed globally:
```bash
python3 main.py
```

---

## Summary of Commands

| Task | Command |
|------|---------|
| Set API Key (PowerShell) | `$env:OPENAI_API_KEY="..."` |
| Run Server (Fast) | `python3 main.py` |
| Run Server (Auto-reload) | `uvicorn main:app --reload --host 127.0.0.1 --port 8001` |
| Open API Docs | `http://127.0.0.1:8001/docs` |
| Test Search | `curl -X POST http://127.0.0.1:8001/search` |
| Expose Publicly | `ngrok http 8001` |
