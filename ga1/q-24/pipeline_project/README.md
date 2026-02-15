# Build an AI-Powered Data Pipeline

## Pipeline Project - Running Guide

## Project Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE PROCESSING FLOW                         │
└─────────────────────────────────────────────────────────────────────┘

                          User Request
                    (email, source)
                          ↓
        ╔═══════════════════════════════════════════════════╗
        ║  STAGE 1: FETCH POSTS (fetch_posts)              ║
        ║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
        ║  • Call JSONPlaceholder API                      ║
        ║  • Get first 3 posts                             ║
        ║  • Handle network errors                         ║
        ╚═══════════════════════════════════════════════════╝
                          ↓
                    [3 Posts Retrieved]
                          ↓
        ╔═══════════════════════════════════════════════════╗
        ║  STAGE 2: ANALYZE EACH POST (analyze_text)       ║
        ║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
        ║  For each post:                                  ║
        ║  • Extract post body text                        ║
        ║  • Send to OpenAI (GPT-4o-mini)                  ║
        ║  • Get analysis (2 sentences)                    ║
        ║  • Classify sentiment (optimistic/pessimistic/balanced)║
        ║  • Handle AI errors gracefully                   ║
        ╚═══════════════════════════════════════════════════╝
                          ↓
            [Analysis + Sentiment for Each Post]
                          ↓
        ╔═══════════════════════════════════════════════════╗
        ║  STAGE 3: STORE RESULTS (store_result)           ║
        ║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
        ║  For each result:                                ║
        ║  • Create result object with metadata            ║
        ║  • Load existing db.json (if exists)             ║
        ║  • Append new result to database                 ║
        ║  • Write updated JSON to file                    ║
        ║  • Handle storage errors                         ║
        ╚═══════════════════════════════════════════════════╝
                          ↓
              [All Results Stored in db.json]
                          ↓
        ╔═══════════════════════════════════════════════════╗
        ║  STAGE 4: SEND NOTIFICATION (send_notification)  ║
        ║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
        ║  • Notify user via email (mocked)                ║
        ║  • Log notification sent                         ║
        ║  • Handle notification errors                    ║
        ╚═══════════════════════════════════════════════════╝
                          ↓
             ┌────────────────────────────┐
             │  RETURN API RESPONSE       │
             ├────────────────────────────┤
             │ • items (analysis results) │
             │ • notificationSent (bool)  │
             │ • processedAt (timestamp)  │
             │ • errors (error list)      │
             └────────────────────────────┘
```

---
#i ran this just on local host and didnt use ngrok
## Prerequisites Setup

### Step 1: Install Dependencies
```bash
# Install required packages globally or via uv
pip install fastapi uvicorn requests openai pydantic
# OR
uv pip install fastapi uvicorn requests openai pydantic

#i did
uv init pipeline_project
uv add fastapi uvicorn requests python-openai pydantic

#Add a requirements.txt file just in case to deploy to vercel or railway etc
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
#I ran this
python3 main.py
# Server runs on http://127.0.0.1:8002
```

### Option B: Using uvicorn (Recommended - with auto-reload on code changes)
```bash
# Terminal 1: Run the FastAPI server with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8002

# If uvicorn is not installed globally, use uv:
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8002
```

### Option C: Using main.py with uvicorn programmatically
```python
# Add this to the end of main.py:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)

# Then run:
python3 main.py
# OR
uv run main.py
```

---

## Testing the API Locally

### Step 1: Verify Server is Running
Open browser and go to: `http://127.0.0.1:8002/docs` (Swagger UI)

### Step 2: Test the /pipeline endpoint
```bash
# Terminal 2: Send a test request
curl -X POST http://127.0.0.1:8002/pipeline \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","source":"test"}'
```

### Expected Response:
```json
{
  "items": [
    {
      "original": "post body text",
      "analysis": "AI analysis result",
      "sentiment": "optimistic",
      "stored": true,
      "timestamp": "2026-02-13T14:30:45.123456Z"
    }
  ],
  "notificationSent": true,
  "processedAt": "2026-02-13T14:30:45.123456Z",
  "errors": []
}
```

---

## Exposing to Public with ngrok

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com or use package manager
```

### Step 2: Create ngrok tunnel (in another terminal)
```bash
# Terminal 3: Create public URL
ngrok http 8002
# This will give you a public URL like: https://xxxx-xx-xxx-xxx.ngrok.io
```

### Step 3: Test via Public URL
Go to: `https://xxxx-xx-xxx-xxx.ngrok.io/docs` (replace with your ngrok URL)

Or use curl:
```bash
curl -X POST https://xxxx-xx-xxx-xxx.ngrok.io/pipeline \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","source":"test"}'
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
uvicorn main:app --reload --host 127.0.0.1 --port 8002
```

### Issue: Dependencies not found
- **Solution**: Install them globally:
```bash
pip install fastapi uvicorn requests openai pydantic
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
| Run Server (Auto-reload) | `uvicorn main:app --reload --host 127.0.0.1 --port 8002` |
| Open API Docs | `http://127.0.0.1:8002/docs` |
| Test Endpoint | `curl -X POST http://127.0.0.1:8002/pipeline` |
| Expose Publicly | `ngrok http 8002` |