from google import genai
#The google.generativeai package is dead. Switch to the new google-genai package.
from google.genai import types
import hashlib
import json
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

puzzle = "Start with 4, multiply by 7, subtract 8, then divide by 2"

prompt = f"""Solve this math puzzle step by step.
Puzzle: {puzzle}

Return ONLY a valid JSON object with no extra text, no markdown, no code fences.
Format exactly like this:
{{"answer": <integer>, "steps": ["step 1 description", "step 2 description", ...]}}"""

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)

data = json.loads(response.text)
answer = data["answer"]
steps_count = len(data["steps"])

email = "23f3003994@ds.study.iitm.ac.in"
verify_input = email + ":" + str(answer) + ":" + str(steps_count)
verify_hash = hashlib.sha256(verify_input.encode()).hexdigest()[:14]

print(f"\n--- Results ---")
print(f"Answer:      {answer}")
print(f"Steps count: {steps_count}")
print(f"Verify hash: {verify_hash}")
print(f"\nSubmit this: {answer},{steps_count},{verify_hash}")