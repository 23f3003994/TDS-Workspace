## This vercel app has the fastapi endpoints of GA2 of the the following questions
Q2 , Q3

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
(I used option A)



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

### Step 2: Test the endpoint
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

---
# Q3 - Code Interpreter with AI Error Analysis

vercel app of this is in vercel-ga2

## Project Architecture

```
User → FastAPI endpoint → Run code (tool) → Check if success
                                              ↓
                                         Success = true?
                                        /            \
                                      Yes             No
                                       ↓              ↓
                                  Return result   AI analyzes traceback
                                                      ↓
                                              Return line numbers + traceback
```

## Implementation Flow

```
Input: {"code": "..."}
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Tool - execute_python_code()                        │
│   • Runs code with exec()                                   │
│   • Captures stdout/stderr                                  │
│   • Returns: {success: bool, output: str}                   │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Check - Is Success True?                            │
├─────────────────────────────────────────────────────────────┤
│ ✓ Yes → Return {error: [], result: output}                  │
│ ✗ No  → Proceed to Step 3                                   │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: AI Agent (only if error)                            │
│   • Input: code + traceback                                 │
│   • Uses LLM with structured output                         │
│   • Returns: error line numbers                             │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Final Response                                      │
│   Return: {error: [lines], result: traceback}               │
└─────────────────────────────────────────────────────────────┘
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

### Step 1: Verify Server is Running
Open browser and go to: =`http://127.0.0.1:8000/docs` (Swagger UI) and check the `/code-interpreter` endpoint

### Step 2: Test the endpoint
 
 > Test 1: Successful Code (No Error)

```bash
curl -X POST "http://localhost:8000/code-interpreter" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = 5\ny = 10\nprint(x + y)"
  }'
  ```
Expected Response
```json
{
  "error": [],
  "result": "15\n"
}
```

 > Test 2: Code With Error (Division by Zero)

 ```bash
curl -X POST "http://localhost:8000/code-interpreter" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = 10\ny = 0\nresult = x / y\nprint(result)"
  }'
  ```
Expected Response (line number may vary slightly but should be 3)

```json
{
  "error": [3],
  "result": "Traceback (most recent call last):\n  File \"\", line 3, in <module>\nZeroDivisionError: division by zero\n"
}
```

> Test 3: Syntax Error Case

 ```bash
curl -X POST "http://localhost:8000/code-interpreter" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = 10\ny =\nprint(x+y)"
  }'
```
This checks whether AI correctly identifies the syntax error line.

---
# Q12 - Function Calling

## project architecture
```
Employee types query (Web UI)
        ↓
HTTP GET → /execute?q=...
        ↓
FastAPI receives query
        ↓
Regex-based template matching
        ↓
Identify correct function + extract parameters
        ↓
Return JSON:
{name, arguments}
```

> This mimicks OpenAI’s function selection behavior, but using rule-based logic instead of AI.
> We are building the routing logic that OpenAI would normally do.

**Compare Both Approaches Side-by-Side**

🔹 **Approach A (Real GPT Function Calling)**

```
User Query
   ↓
Send to OpenAI with function schemas
   ↓
GPT decides function + arguments
   ↓
Return JSON
```


🔹**Approach B (This Assignment)**

```
User Query
   ↓
FastAPI regex matching
   ↓
YOU decide function + arguments
   ↓
Return same JSON format

We are simulating what GPT would have done.
```
---
## local testing

1. `pip install requirements.txt`
2. In wsl - `uvicorn main:app --reload` (default 8000)  or `uvicorn main:app --reload --port 8001`
   Your Final API Endpoint: `http://127.0.0.1:8000/execute`
3. send a curl request from another terminal

**Example Test URLs**

Ticket Status
` http://127.0.0.1:8000/execute?q=What is the status of ticket 83742? `

Response:

```json
{
  "name": "get_ticket_status",
  "arguments": "{\"ticket_id\": 83742}"
}
```
Schedule Meeting
`http://127.0.0.1:8000/execute?q=Schedule a meeting on 2025-02-15 at 14:00 in Room A.`

Expense Balance
`http://127.0.0.1:8000/execute?q=Show my expense balance for employee 10056.`

Performance Bonus
`http://127.0.0.1:8000/execute?q=Calculate performance bonus for employee 10056 for 2025.`

Report Office Issue
`http://127.0.0.1:8000/execute?q=Report office issue 45321 for the Facilities department.`

---