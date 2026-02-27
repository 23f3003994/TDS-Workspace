# ---------------------------------------------
# Robust Structured Data Extraction with Schema Validation
# ---------------------------------------------

# Step 0: Install necessary packages
# pip install pydantic openai

from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
import json
import os


# Create OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)
# -------------------------------
# Step 1: Define JSON Schema using Pydantic
# -------------------------------
class ResearchPaper(BaseModel):
    title: str
    authors: str
    abstract: str
    year: Optional[int] = None
    keywords: Optional[List[str]] = None
    methodology: Optional[str] = None

# -------------------------------
# Step 2: Improved Prompt Creation
# -------------------------------
def create_prompt(text: str) -> str:
    # JSON skeleton included to reduce errors
    json_skeleton = {
        "title": "",
        "authors": "",
        "abstract": "",
        "year": None,
        "keywords": [],
        "methodology": ""
    }
    return f"""
Extract the following research paper information from the text.

Rules:
1. Required fields: title, authors, abstract
2. Optional fields: year, keywords, methodology
3. Field types:
   - title, authors, abstract, methodology → string
   - year → integer
   - keywords → array of strings
4. Edge cases:
   - If a field is missing or ambiguous, set its value to null
   - Keywords must always be an array (even if only 1)
   - Do NOT include extra fields
5. Return ONLY valid JSON (no extra text). Use the following skeleton:

{json.dumps(json_skeleton, indent=2)}

Text:
"{text}"
"""

# -------------------------------
# Step 3: LLM Extraction Function
# -------------------------------


def extract_with_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}  # structured output
    )
    return response.choices[0].message.content

# -------------------------------
# Step 4: Validate Extracted JSON
# -------------------------------
def validate_data(data_json: str):
    try:
        paper = ResearchPaper.model_validate_json(data_json)
        return True, paper, []
    except Exception as e:
        return False, None, [str(e)]

# -------------------------------
# Step 5: Retry Logic (max 2 retries)
# -------------------------------
def extract_with_retry(text: str, max_retries: int = 2):
    errors = []
    for attempt in range(max_retries + 1): # 3 tries coz first is actual try , then 2 retries
        prompt = create_prompt(text)
        raw_json = extract_with_llm(prompt)

        valid, paper, validation_errors = validate_data(raw_json)

        if valid:
            # Confidence decreases if retried
            confidence = 0.95 if attempt == 0 else 0.8
            return paper.dict(), True, confidence, [], attempt

        errors.extend(validation_errors)

    # If all retries fail
    return None, False, 0.5, errors, max_retries

# -------------------------------
# Step 6: Run Pipeline on Sample Text
# -------------------------------
sample_text = """
Title: Deep Learning for NLP. Authors: Smith et al. Year: 2024. Abstract: We propose a novel architecture... Keywords: NLP, transformers. Methodology: We trained on 1B tokens
"""

data, validated, confidence, errors, retries = extract_with_retry(sample_text)

# -------------------------------
# Step 7: Build Final Output JSON
# -------------------------------
result = {
    "schema": ResearchPaper.model_json_schema(),
    "extracted": data,
    "validated": validated,
    "confidence": confidence,
    "errors": errors,
    "retryCount": retries,
    "model": "gpt-4.1-mini"
}

# Pretty print JSON output
print(json.dumps(result, indent=2))