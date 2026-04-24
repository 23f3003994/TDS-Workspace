import hashlib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class HashRequest(BaseModel):
    text: str
    salt: str

@app.get("/health")
async def health():
    return {"status": "ok", "service": "hash-api"}

@app.post("/hash")
async def compute_hash(req: HashRequest):
    text = req.text.strip()
    salt = req.salt.strip()

    if not text:
        return {"error": "text must not be empty"}, 400

    sha = hashlib.sha256(text.encode()).hexdigest()[:16]
    salted_sha = hashlib.sha256(f"{text}:{salt}".encode()).hexdigest()[:16]
    reversed_text = text[::-1]
    length = len(text)

    return {
        "sha256": sha,
        "salted_sha256": salted_sha,
        "reversed": reversed_text,
        "length": length
    }