from google import genai
from google.genai import types
import hashlib
import json
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

EMAIL = "23f3003994@ds.study.iitm.ac.in"
paragraph = "Frank Johansson is a 37-year-old ML engineer working at Spotify in Mumbai."

prompt = f"""Extract the following fields from this paragraph:
- "name": full name (string)
- "age": age as integer
- "city": city name (string)
- "role": job role (string)
- "company": company name (string)

Paragraph: {paragraph}

Return ONLY the JSON object, no markdown, no explanation."""

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0
    )
)

data = json.loads(response.text)

name = data["name"]
age = int(data["age"])
city = data["city"]
role = data["role"]
company = data["company"]

verify_input = f"{EMAIL}:{name}:{age}:{city}:{role}:{company}"
verify_hash = hashlib.sha256(verify_input.encode()).hexdigest()[:14]

print(f"Submit: {name},{age},{city},{role},{company},{verify_hash}")