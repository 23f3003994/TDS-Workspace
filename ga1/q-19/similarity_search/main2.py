##### FILE NOT NEEDED


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
from openai import OpenAI
import os

app = FastAPI()

# Enable CORS
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""),base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1"))

class SearchRequest(BaseModel):
    docs: List[str]
    query: str

class SearchResponse(BaseModel):
    matches: List[str]

def get_embedding(text: str) -> List[float]:
    """Get embedding for a text using OpenAI's text-embedding-3-small model."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    
    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

@app.post("/similarity", response_model=SearchResponse)
async def similarity_search(request: SearchRequest):
    """
    Perform semantic search on documents using embeddings and cosine similarity.
    
    Returns the top 3 most similar documents to the query.
    """
    # Get embedding for the query
    query_embedding = get_embedding(request.query)
    
    # Get embeddings for all documents
    doc_embeddings = [get_embedding(doc) for doc in request.docs]
    
    # Calculate similarity scores
    similarities = []
    for idx, doc_embedding in enumerate(doc_embeddings):
        similarity = cosine_similarity(query_embedding, doc_embedding)
        similarities.append((idx, similarity, request.docs[idx]))
    
    # Sort by similarity score (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get top 3 matches
    top_3 = similarities[:3]
    matches = [doc for _, _, doc in top_3]
    
    return SearchResponse(matches=matches)

@app.get("/")
async def root():
    return {"message": "InfoCore Semantic Search API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
