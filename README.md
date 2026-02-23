# TDS-Workspace

[![Daily Repo Update](https://github.com/23f3003994/TDS-Workspace/actions/workflows/daily-update.yml/badge.svg)](https://github.com/23f3003994/TDS-Workspace/actions/workflows/daily-update.yml)

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




## there is no local testing folders for these 26,27,28 qstns
## its just this vercel folder
## so can do local testing by following the below steps



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
### What I did
Created vercel-ga1-26-27-28 folder
	|-----------api
		        |------------main.py
	|-----------vercel.json
	|-----------requirements.txt

for local testing either set this folder as a uv folder and use the above prerequisites step 
or 
since everything is actually installed globally..no need of them
 just add the below code in main.py (make sure to comment it before deploying)
  
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,port=8003)
```
and run 

```bash
python3 main.py

or

uvicorn api.main:app –reload --host 127.0.0.1 --port 8003
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
# Server runs on http://127.0.0.1:8003
```

### Option B: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8003

# If uvicorn is not installed globally, use uv:
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8003
```

### Option C: Using main.py with uvicorn programmatically
```python
# Add this to the end of main.py:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,port=8003)

# Then run:
python3 main.py
# OR
uv run main.py
```
---
