import sys
from google import genai
import os

# ---------- Step 1: Get inputs ----------
pdf_path = sys.argv[1]        # expenses.pdf
target_date = sys.argv[2]     # "10Jan"

# ---------- Step 2: Create client ----------
 
#Key "GEMINI_API_KEY" comes from environment → client auto-reads it
# # it uses the "GEMINI_API_KEY" from environment variables by default ie, we must export it 
client = genai.Client() 

#if its my aipipe token just pass it explicitly like this
# client = genai.Client(
#     api_key=os.getenv("AIPIPE_TOKEN"),
#     http_options={
#         "base_url": "https://aipipe.org/geminiv1beta"
#     }
# )  but this aipipe maynot support files.upload, so it throws error when we use client.files.upload

# ---------- Step 3: Upload file ----------
print("Uploading PDF to Gemini...")
file = client.files.upload(file=pdf_path)

# Wait until file becomes ACTIVE
while file.state != "ACTIVE":
    file = client.files.get(name=file.name)

print("File uploaded and ready!")

# ---------- Step 4: Prompt Gemini ----------
prompt = f"""
You are analysing a multi-page PDF of expense entries.

Each entry contains:
- A date in January written in many formats
- Examples: 10Jan, Jan10, January 10, 10JAN, 10January, Jan 10, 10 January,10JAN
- An amount with currency: Rs / Rupees / Dollar / Dollars / USD

Your task:
1. Find ALL expense entries across ALL pages whose date is 10th January (any format variant).
2. Convert any Dollar/USD amounts to Rupees using: 1 Dollar = 80 Rs.
3. Keep Rupee amounts unchanged.
4. Return ONLY a JSON array of final amounts in Rupees.

Important:
- Do not miss any format variant of January 10.
- There might be other variants other than the examples mentioned, so be thorough.
- Do not include entries from other dates.
- Carefully scan all pages.
- Output only a JSON list of numbers, no text.
"""
try: 

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[file, prompt],
        config={
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "array",
            "items": {"type": "number"}
        }}
    )
except Exception as e:
    print("Error during content generation:", e)
    sys.exit(1)

# ---------- Step 5: Parse JSON ----------
import json
print("RAW OUTPUT:", response.text)

if not response.text.strip():
    raise ValueError("Model returned empty output!")

amounts = json.loads(response.text)
# ---------- Step 6: Sum ----------
total = sum(amounts)

print(f"\nTotal spent on {target_date}: Rs {total}")