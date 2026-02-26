# AI Video Attendee Extraction – Gemini Video API

> The video is in tds/tds-ga3 folder --> attendee_checkin_23f3003994.webm
> Its in the local repository o this TDS-Workspace too, I havent pushed it to github

### Project architecture

```
[Local Video File] 
      │
      ▼
[GenAI Client: client.files.upload()]
      │  (poll until ACTIVE)
      ▼
[Gemini Files API] 
      │  (analyzes frames & audio)
      ▼
[Gemini LLM: generate_content]
      │  (prompted to extract name+date)
      ▼
[Structured JSON Output] ---> Parsed & Pretty-printed in Python

```

```bash
pip install google-genai
export GEMINI_API_KEY="your_key_here"
```
> Used gemini api key from google ai studio( free tier) and not ai pipe token

#### What You’ll Finally Do

**Run:**

` python3 main.py attendee_checkin_23f3003994.webm `

**Output:**

You will see something like this printed in the terminal:

**Step 2a**: Upload messages
Uploading video...
Video ready!


**Step 2b**: Raw JSON from Gemini
RAW OUTPUT: [
  {"name": "Alice Smith", "date": "03/07/2025"},
  {"name": "Benjamin Patel", "date": "21/11/2024"},
  {"name": "Carla Gomes", "date": "12/05/2025"},
  {"name": "David Lee", "date": "08/09/2025"},
  ...
  {"name": "Zara Khan", "date": "15/06/2025"}
]

This is the full array of 20 objects.

**Step 2c**: Pretty-printed version
[
  {
    "name": "Alice Smith",
    "date": "03/07/2025"
  },
  {
    "name": "Benjamin Patel",
    "date": "21/11/2024"
  },
  {
    "name": "Carla Gomes",
    "date": "12/05/2025"
  },
  ...
  {
    "name": "Zara Khan",
    "date": "15/06/2025"
  }
]