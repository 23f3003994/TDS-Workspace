# FastAPI Batch Sentiment Analysis 

# Prerequisites Setup

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

(I used option A)

### Option A: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8000
or on port 8000
uvicorn main:app --reload --port 8000

# If uvicorn is not installed globally, use uv:
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
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

verify server is running on

http://localhost:8000

endpoint is

POST /sentiment

Basic curl Request (Mac / Linux / Git Bash)
``` bash
curl -X POST "http://localhost:8000/sentiment" \
     -H "Content-Type: application/json" \
     -d '{
           "sentences": [
             "I love this course!",
             "This is the worst day ever.",
             "The meeting is at 3 PM."
           ]
         }'
```

Expected Response Format

You should receive something like:
``` json
{
  "results": [
    {
      "sentence": "I love this course!",
      "sentiment": "happy"
    },
    {
      "sentence": "This is the worst day ever.",
      "sentiment": "sad"
    },
    {
      "sentence": "The meeting is at 3 PM.",
      "sentiment": "neutral"
    }
  ]
}
```