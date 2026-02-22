# LLM Structured Output - FastAPI Sentiment Analysis

vercel app of this is in vercel-ga2

## project architecture

Request flow:
```
Client
  │
  ▼
POST /comment  ──►  Pydantic (CommentRequest validates input)
  │
  ▼
OpenAI gpt-4.1-mini
  │  response_format: json_schema (enforces structure)
  ▼
Pydantic (SentimentResponse validates output)
  │  Literal["positive","negative","neutral"]
  │  Field(ge=1, le=5)
  ▼
JSON Response  ──►  Client
{ "sentiment": "positive", "rating": 5 }
```
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
$env:OPENAI_API_KEY="#################################"
$env:OPENAI_BASE_URL="https://aipipe.org/openai/v1"

# On Linux/Mac (bash/zsh)
export OPENAI_API_KEY="#################################"
export OPENAI_BASE_URL="https://aipipe.org/openai/v1"
```

---

## Running Locally
(I used option A )



### Option A: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8001

# If uvicorn is not installed globally, use uv:
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### Option B: Using main.py with uvicorn programmatically (Fast - if dependencies installed globally)
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
Open browser and go to: =`http://127.0.0.1:8001/docs` (Swagger UI) and check the /comment endpoint

### Step 2: Test the  endpoint
```bash
Test using curl:

curl -X POST "http://127.0.0.1:8001/comment" \
-H "Content-Type: application/json" \
-d '{"comment":"This product is amazing!"}'

Expected:

{
  "sentiment": "positive",
  "rating": 5
}
```
