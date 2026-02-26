import sys
from google import genai
import json

video_path = sys.argv[1]

client = genai.Client()

print("Uploading video...")
file = client.files.upload(file=video_path)

while file.state != "ACTIVE":
    file = client.files.get(name=file.name)

print("Video ready!")

prompt = """
You are analyzing an event check-in video.

The video shows attendee names and their registration dates on screen.

Your task:
1. Extract ALL attendee name and date pairs shown in the video.
2. There are exactly 20 attendees.
3. Format dates strictly as dd/mm/yyyy.
4. Return ONLY a JSON array:
   [{"name": "...", "date": "dd/mm/yyyy"}, ...]

Rules:
- Do not miss any attendee
- Do not repeat duplicates
- Ensure date format is dd/mm/yyyy
- Output ONLY valid JSON
"""
try: 
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[file, prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "date": {"type": "string"}
                    },
                    "required": ["name", "date"]
                }
            }
        }
    )
except Exception as e:
    print("Error during content generation:", e)
    sys.exit(1)

print("RAW OUTPUT:", response.text)

data = json.loads(response.text)
print(len(data))   ## 20
print(json.dumps(data, indent=2))


