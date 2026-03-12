import os
import numpy as np
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)

headlines = [
"Researchers identify new biomarker for early detection of pancreatic cancer",
"Public health officials urge vaccination as flu season begins earlier than usual",
"Mental health app demonstrates effectiveness in reducing anxiety symptoms",
"Clinical trial shows promising results for Alzheimer's disease treatment",
"Study links ultra-processed food consumption to increased cardiovascular risk",
"Cybersecurity firm discovers critical zero-day vulnerability in popular browser"
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=headlines
)

embeddings = np.array([item.embedding for item in response.data])

centroid = embeddings.mean(axis=0)

def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

distances = [cosine_distance(e, centroid) for e in embeddings]

outlier_index = np.argmax(distances)

print("Outlier headline:")
print(headlines[outlier_index])