# Build Semantic Search with Re-ranking

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
$env:OPENAI_API_KEY="***REMOVED***"
$env:OPENAI_BASE_URL="https://aipipe.org/openai/v1"

# On Linux/Mac (bash/zsh)
export OPENAI_API_KEY="***REMOVED***"
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
