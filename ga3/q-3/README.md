# Code Interpreter with AI Error Analysis 

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
