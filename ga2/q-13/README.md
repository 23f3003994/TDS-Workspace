# FastAPI server to serve data 

## Prerequisites Setup

### Step 1: Install Dependencies 
```bash
# Install required packages globally or via uv
pip install fastapi uvicorn requests openai pydantic numpy 
# OR
uv pip install fastapi uvicorn requests openai pydantic numpy 

# Using uv (if uv is installed)
uv init project_nam
uv add fastapi uvicorn requests openai pydantic numpy 

# Add a requirements.txt file for deployment to vercel or railway
pip freeze > requirements.txt
```

## Running Locally

### Option A: Using Python directly (Fast - if dependencies installed globally but must have option c __name__ code)
```bash
# Terminal 1: Run the FastAPI server
#I ran this
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

### Step 2: Test the /api endpoint
just go to
http://127.0.0.1:8000/api endpoint --> should return all students' data
also 
check
http://127.0.0.1:8000/api?class=1A
http://127.0.0.1:8000/api?class=1A&class=1B