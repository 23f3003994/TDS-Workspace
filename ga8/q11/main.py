from google import genai
from google.genai import types
import hashlib
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

EMAIL = "23f3003994@ds.study.iitm.ac.in"

sentences = [
    "The worst flight experience ever, delayed for hours with no communication.",
    "She did an excellent job organizing the event, everything was perfect.",
    "The hotel room was dirty, smelled bad, and had cockroaches in the bathroom."
]

all_labels = []
total_words = 0
total_chars = 0

for i, sentence in enumerate(sentences):
    prompt = f"""Classify the sentiment of this sentence as either POSITIVE or NEGATIVE.
Respond with ONLY one word: POSITIVE or NEGATIVE. No explanation.

Sentence: "{sentence}" """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=5,
            temperature=0,
        )
    )

    label = response.text.strip().upper()
    # safety check
    if "POSITIVE" in label:
        label = "POSITIVE"
    elif "NEGATIVE" in label:
        label = "NEGATIVE"

    all_labels.append(label)
    total_words += len(sentence.split())
    total_chars += len(sentence)
    print(f"Sentence {i+1}: {label}")

labels_csv = ",".join(all_labels)
verify_input = f"{EMAIL}:{labels_csv}:{total_words}:{total_chars}"
verify_hash = hashlib.sha256(verify_input.encode()).hexdigest()[:14]

print(f"\nSubmit: {labels_csv},{total_words},{verify_hash}")
