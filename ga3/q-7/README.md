# LLM Audio Processing – YouTube Topic Timestamp Finder

## Project architecture

This code builds a FastAPI web service that:

> Given a YouTube video URL + a topic →
returns the timestamp where that topic first appears in the transcript.

#### Overall System Flow (Architecture)

Here is the conceptual pipeline:
```
Client (Postman / Frontend)
        |
        |  POST /ask  (video_url + topic)
        v
FastAPI Endpoint (/ask)
        |
        |--> Step 1: Extract Video ID from URL
        |
        |--> Step 2: Fetch YouTube Transcript
        |
        |--> Step 3: Try Exact String Match
        |       (fast search)
        |
        |--> If not found:
        |        Step 4: Semantic Search using Gemini (LLM)
        |
        v
Return timestamp (HH:MM:SS)
```
Two Search Strategies Used

**Method 1: Exact Search (Fast)**

Loop through transcript lines

Check if topic string exists

If yes → return timestamp immediately

**Method 2: Semantic Search (Smart fallback)**

If exact match fails:

Send transcript to Gemini AI

Ask: “When is this topic first spoken?”

Gemini returns timestamp

So this API is:

Fast when simple
Smart when complex

## local testing

1. `pip install requirements.txt`
2. `export AIPIPE_TOKEN="..."`
3. In wsl - `uvicorn main:app --reload` (default 8000)  or `uvicorn main:app --reload --port 8001`
4. In powershell - `ngrok http 8000` (or 8001)
5. send a curl request from another terminal
```bash
    curl -X POST "http://localhost:8000/ask"   
    -H "Content-Type: application/json"   
    -d '{
    "video_url": "https://youtu.be/xxpc-HPKN28",
    "topic": "And those variables would be your data. But if you chose samples, that you know, just"
    }'
```

  expected output:

  ```json
  {"timestamp":"00:10:15","video_url":"https://youtu.be/xxpc-HPKN28","topic":"And those variables would be your data. But if you chose samples, that you know, just"}
  ```

> NOTE:  It's always better to do this in a virtual environment.

