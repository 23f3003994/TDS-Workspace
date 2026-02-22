## This vercel app has the fastapi endpoints of GA2 of the the following questions
Q2 , 

## Final Deployment Structure for Vercel

## step- 1
main.py  (in api folder)
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




## Q2 - LLM Structured Output - FastAPI Sentiment Analysis

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
(I used option A, )



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

### Step 2: Test the /similarity endpoint
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
