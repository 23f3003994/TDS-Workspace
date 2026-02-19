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

## project explanation

## Architecture Diagram

```
Client Request (POST /api/latency)
    |
    v
FastAPI App (main.py)
    |
    +--> CORS Middleware (allows cross-origin requests)
    |
    +--> /api/latency Endpoint
        |
        +--> Parse Request Body (regions: list[str], threshold_ms: int)
        |
        +--> Load JSON Data (q-vercel-latency.json)
        |
        +--> For each region in request.regions:
        |       +--> Filter data by region
        |       +--> Extract latencies and uptimes
        |       +--> Calculate average_latency (np.mean(latencies))
        |       +--> Calculate p95_latency (np.percentile(latencies, 95))
        |       +--> Calculate avg_uptime (np.mean(uptimes))
        |       +--> Count breaches (sum(latency > threshold_ms for latency in latencies))
        |
        +--> Build Response JSON with metrics per region
        |
        v
    Response to Client (JSON with regions and metrics)
```





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

## Running Locally

### Option A: Using Python directly (Fast - if dependencies installed globally but must have option c __name__ code)
```bash
# Terminal 1: Run the FastAPI server
python3 main.py
# Server runs on http://127.0.0.1:8001
```

### Option B: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8001   or api.main

# If uvicorn is not installed globally, use uv:
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8001    or api.main
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

### Step 2: Test the /api/latency endpoint
```bash
curl -X POST http://127.0.0.1:8001/api/latency \
  -H "Content-Type: application/json" \
  -d '{"regions":["amer"],"threshold_ms":157}'
```

### Expected Response:
```json
{
  "regions": {
    "amer": {
      "average_latency": 120.5,
      "p95_latency": 180.0,
      "avg_uptime": 99.5,
      "breaches": 2
    }
  }
}
```

The response returns latency metrics for the specified regions, including average latency, P95 latency, average uptime, and the number of breaches above the threshold.

---