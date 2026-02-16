#python3 main.py runs faster than uv run main.py (python3 works as i have installed all dependencies globally)
# ngrok http 8000 in another poweshell
#and go to http://..../docs try out search
#ans is http://..../search
#sometimes permission error issues of api key can happen-just run again
#used claude-ai's help to generate some parts-tds-ga1/q-18-fastapi-claudai is the file it gave
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from typing import List, Dict, Any
import os
import json
import numpy as np
import uvicorn
import openai  # pip install openai
import time
import cohere
from werkzeug.exceptions import HTTPException

#COHERE is not needed

# Set token and base URL
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")#.environ.get("ENV_VARIABLE_NAME", "default_value")

# Initialize Cohere # for reranking ..actually can use the same for vector similarity, compute embeddings too
co = cohere.Client(os.environ.get("COHERE_API_KEY", "")) #free account key setup

#export COHERE_API_KEY=###############################

#must set them
# export OPENAI_API_KEY=################################
# export OPENAI_BASE_URL=https://aipipe.org/openai/v1



#to run locally: uv run uvicorn main:app --reload  (reload for auto restart on code changes) i have pip installed fastapi and uvicorn
#then check in another terminal by: curl -X POST http://127.0.0.1:8000/api/latency   -H "Content-Type: application/json"   -d '{"regions":["amer"],"threshold_ms":157}'

#Note:
# run in the terminal (if uvicorn is not globally installed)
# uv run uvicorn filename:app --reload --host 127.0.0.1 --port 8000
#  (if uvicorn is  globally installed)
# uvicorn filename:app --reload --host 127.0.0.1 --port 8000


#or use 
# import uvicorn

# if __name__ == "__main__":
#     uvicorn.run(app,port=8000)

#and run 
# uv run main.py   
# (need uv to run only if we havent globally installed any of the libraries/dependencies needed elso just run python3 main.py)

#after locally testing output
# run

app = FastAPI()
# Middleware for simple cases

# Middleware handles most requests automatically
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all websites
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
    expose_headers=["*"] # expose all headers ie allow client side JS to access them
)


# Global storage
documents = []
document_embeddings = None

# Request body model
# class SearchRequest(BaseModel):
#     query: str
#     k: int = 12
#     rerank: bool = True
#     rerankK: int = 7


# Pydantic models
class SearchRequest(BaseModel):
    query: str
    k: int = Field(12, ge=1, le=100)  # Find most similar k(default 12), ge>= le <=
    rerank: bool = True
    rerankK: int = Field(7, ge=1)#Ask LLM which (rerankk default-7) are most relevant

# if rerank is True
#     rerank top k
#     select top rerankK


class DocumentResult(BaseModel):
    """
    Represents ONE search result document returned by the API.

    id: Unique document identifier (integer)
    score: Similarity or reranked score (float between 0–1)
    content: The actual document text
    metadata: Additional optional information about the document

    Dict[str, Any] means:
        - key must be a string
        - value can be ANY type (int, float, string, list, dict, etc.)
    """
    id: int
    score: float
    content: str
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """
    Represents the FULL API response for a search request.

    results: List of DocumentResult objects
    reranked: Boolean indicating whether LLM reranking was applied
    metrics: Extra information like latency, model used, etc.

    Dict[str, Any] here allows flexible metrics like:
        {
            "vector_latency_ms": 12,
            "rerank_latency_ms": 45,
            "total_latency_ms": 57
        }
    """
    results: List[DocumentResult]
    reranked: bool
    metrics: Dict[str, Any]

########for q-19#########################################################

class SearchRequest1(BaseModel):
    docs: List[str]
    query: str

# if rerank is True
#     rerank top k
#     select top rerankK




class SearchResponse1(BaseModel):
    matches: List[str]
############################Q-19############################################

#VIDEO DEMO PURPOSES ONLY
#root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}



# Dummy search endpoint (use this endpoint to check the queries being sent by the question
#so that we can modify the documents based on that query
# @app.post("/search")
# def search(req: SearchRequest):
#     return {"message": "This is a placeholder. Query received:", "query": req.query}



def load_documents():
    """Load news articles"""
    global documents
    
    # # Try to load from file
    # if os.path.exists('/mnt/user-data/uploads/news_articles.json'):
    #     with open('/mnt/user-data/uploads/news_articles.json', 'r') as f:
    #         data = json.load(f)
    #         documents = [{"id": i, "content": doc.get("content", str(doc)), 
    #                      "metadata": doc.get("metadata", {})} 
    #                     for i, doc in enumerate(data)]
    # else:

    # Generate sample documents
    #x modulo 5 ie remainder obtained by dividing any number x by 5 will be in [0,1,2,3,4] only
    topics = ["climate change", "technology", "politics", "sports", "economy"]
    documents = [
        {
            "id": i,
            "content": f"News article {i} about {topics[i % len(topics)]}",
            "metadata": {"topic": topics[i % len(topics)]}
        }
        for i in range(104)
    ]
    
    return documents

def compute_embeddings():
    """Compute embeddings using OpenAI"""
    global document_embeddings
    
    print("Computing embeddings with OPenAI...")
    
    texts = [doc["content"] for doc in documents]


    #if cohere
    # response = co.embed(
    #     texts=texts,
    #     model="embed-english-light-v3.0",
    #     input_type="search_document"
    # )
    
    # document_embeddings = np.array(response.embeddings)
    
    response = openai.embeddings.create(
        model="text-embedding-3-small",  # model supported by AI Pipe
        input=texts
    )
    """
    -------------------------
    What the response looks like:
    -------------------------

    response is an OpenAI object similar to:

    {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": [0.0123, -0.0045, 0.9912, ...]
            },
            {
                "object": "embedding",
                "index": 1,
                "embedding": [-0.2211, 0.7712, -0.1123, ...]
            },
            ...
        ],
        "model": "text-embedding-3-small",
        "usage": {
            "prompt_tokens": 123,
            "total_tokens": 123
        }
    }

    Important parts:
    - response.data → list of embedding objects
    - Each item.embedding → list of floats (vector)
    - Length of embedding depends on model (e.g., 1536 dimensions)
    """

    # Extract only the embedding vectors from the response
    # Each item.embedding is a list of floats
    # Example:
    # item.embedding = [0.0123, -0.0045, 0.9912, ...]
    
    # Each embedding is a list of floats
    document_embeddings = np.array([item.embedding for item in response.data])
    """
    After conversion:

    document_embeddings becomes a 2D NumPy array

    Shape:
        (number_of_documents, embedding_dimension)

    Example:
        (104, 1536)

    That means:
        - 104 documents
        - Each document has a 1536-dimensional vector
    """
    print(document_embeddings.shape) #eg (104,1053)..104 docs each has 1053 dimension embedding
    print(f"Computed {len(document_embeddings)} embeddings") #104 



#or look at similarity API in https://github.com/sanand0/aipipe?tab=readme-ov-file#native-provider-api-keys
def vector_search(query, k=12):
    """Initial retrieval using vector similarity"""
    start_time = time.time()   #Track latency in milliseconds
     
     #if cohere
     # Get query embedding
    # query_response = co.embed(
    #     texts=[query],
    #     model="embed-english-light-v3.0",
    #     input_type="search_query"
    # )
    # query_emb = np.array(query_response.embeddings[0])
    # Get query embedding
    query_response = openai.embeddings.create(
        model="text-embedding-3-small",  # model supported by AI Pipe
        input=query
    )
  
    query_emb = np.array(query_response.data[0].embedding)
    
    # Compute cosine similarities
    similarities = []
    for i, doc_emb in enumerate(document_embeddings):
        sim = np.dot(query_emb, doc_emb) / (
            np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)
        )
        similarities.append({
            "id": documents[i]["id"],
            "score": float(sim),
            "content": documents[i]["content"],
            "metadata": documents[i].get("metadata", {})
        })
        """
        document_embeddings is a 2D NumPy array:

            Shape:
                (num_documents, embedding_dimension)

        doc_emb is one document vector:
            Shape:
                (1536,)
        """

        # Cosine similarity formula:
        #
        # sim = (A · B) / (||A|| * ||B||)
        #
        # A · B          → dot product
        # ||A||, ||B||   → vector magnitudes (Euclidean norm)
        #
        # Result range:
        #   -1 → opposite meaning
        #    0 → unrelated
        #    1 → very similar

    """
    similarities now looks like:

    [
        {
            "id": 12,
            "score": 0.8234,
            "content": "Machine learning is a subset of AI.",
            "metadata": {...}
        },
        {
            "id": 3,
            "score": 0.7121,
            "content": "FastAPI is a Python framework.",
            "metadata": {...}
        },
        ...
    ]

    One entry per document.
    """

    # -----------------------------------
    # STEP 3: Sort by similarity score
    # -----------------------------------
    similarities.sort(key=lambda x: x["score"], reverse=True)
    latency = int((time.time() - start_time) * 1000)
    
    return similarities[:k], latency



# def rerank_with_cohere(query, candidates, top_k=7):
#     """Re-rank using Cohere's rerank API"""
#     start_time = time.time()
    
#     # Prepare documents for reranking
#     docs = [c["content"] for c in candidates]
    
#     # Use Cohere's rerank endpoint
#     response = co.rerank(
#         query=query,
#         documents=docs,
#         top_n=top_k,
#         model="rerank-english-v3.0"
#     )
    
#     # Map back to original documents with new scores
#     results = []
#     for result in response.results:
#         idx = result.index
#         results.append({
#             "id": candidates[idx]["id"],
#             "score": float(result.relevance_score),
#             "content": candidates[idx]["content"],
#             "metadata": candidates[idx].get("metadata", {})
#         })
    
#     latency = int((time.time() - start_time) * 1000)
#     return results, latency


#or use openai itself(batch version)
def rerank_with_openai(query, candidates, top_k=7):
    """
    Re-rank documents using OpenAI LLM.

    Requirements satisfied:
    - Score from 0–10
    - Normalize to 0–1
    - Batch all candidates in ONE request
    """

    start_time = time.time()
    print(query)

    # Prepare numbered documents
    docs_text = ""
    for i, candidate in enumerate(candidates):
        docs_text += f"\nDocument {i}:\n{candidate['content']}\n"

    prompt = f"""
You are a search relevance scorer.

Query:
{query}

Below are candidate documents.

For each document, return a relevance score from 0 to 10.
Return ONLY a JSON list of numbers in order.

Example:
[7, 3, 10, 1]

Documents:
{docs_text}
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # Extract model output
    output_text = response.choices[0].message.content.strip()

    """
    Expected model output:
    [8, 2, 9, 4, 1, 6]
    """

    try:
        scores = eval(output_text)  # safer version would use json.loads
    except:
        scores = [0] * len(candidates)

    # Normalize scores (0–10 → 0–1)
    normalized_scores = [s / 10.0 for s in scores]

    results = []

    for i, candidate in enumerate(candidates):
        results.append({
            "id": candidate["id"],
            "score": normalized_scores[i],
            "content": candidate["content"],
            "metadata": candidate.get("metadata", {})
        })

    # Sort by reranked score
    #RESULTS IS A LIST OF DICTS OF top k matching docs
    results.sort(key=lambda x: x["score"], reverse=True)

    latency = int((time.time() - start_time) * 1000)

    return results[:top_k], latency

@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    try:
        if req.rerankK > req.k:
            raise HTTPException(status_code=400, detail=f"rerankK must be <= k")
        
        # Vector search
        candidates, search_latency = vector_search(req.query, req.k)
        
        # Re-ranking
        if req.rerank and candidates:
            results, rerank_latency = rerank_with_openai(req.query, candidates, req.rerankK)
        else:
            results = candidates[:req.rerankK]#if rerank is false we just select top 7  from the top 12 we found
            rerank_latency = 0
        
        result_objects = [
            DocumentResult(**r) for r in results
        ]
# Convert each dictionary in `results` into a Pydantic DocumentResult object
# `r` is a dictionary like:
# {
#     "id": 12,
#     "score": 0.87,
#     "content": "Machine learning is a subset of AI.",
#     "metadata": {...}
# }
#
# The **r syntax unpacks the dictionary:
# It is equivalent to:
# DocumentResult(
#     id=r["id"],
#     score=r["score"],
#     content=r["content"],
#     metadata=r["metadata"]
# )
#
# This ensures:
# - Type validation (id must be int, score must be float, etc.)
# - Proper formatting for FastAPI response
# - Automatic schema documentatio
        return SearchResponse(
            results=result_objects,
            reranked=req.rerank,
            metrics={
                "latency": search_latency + rerank_latency,
                "totalDocs": len(documents),
                "searchLatency": search_latency,
                "rerankLatency": rerank_latency
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    




###########################################Q-19##############################################

def compute_embeddings1(docs):
    """Compute embeddings using OpenAI"""
    
    print("Computing embeddings with OPenAI...")
    #list of contents
    texts = docs


    #if cohere
    # response = co.embed(
    #     texts=texts,
    #     model="embed-english-light-v3.0",
    #     input_type="search_document"
    # )
    
    # document_embeddings = np.array(response.embeddings)
    
    response = openai.embeddings.create(
        model="text-embedding-3-small",  # model supported by AI Pipe
        input=texts
    )
    """
    -------------------------
    What the response looks like:
    -------------------------

    response is an OpenAI object similar to:

    {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": [0.0123, -0.0045, 0.9912, ...]
            },
            {
                "object": "embedding",
                "index": 1,
                "embedding": [-0.2211, 0.7712, -0.1123, ...]
            },
            ...
        ],
        "model": "text-embedding-3-small",
        "usage": {
            "prompt_tokens": 123,
            "total_tokens": 123
        }
    }

    Important parts:
    - response.data → list of embedding objects
    - Each item.embedding → list of floats (vector)
    - Length of embedding depends on model (e.g., 1536 dimensions)
    """

    # Extract only the embedding vectors from the response
    # Each item.embedding is a list of floats
    # Example:
    # item.embedding = [0.0123, -0.0045, 0.9912, ...]
    
    # Each embedding is a list of floats
    doc_embeddings = np.array([item.embedding for item in response.data])
    print(doc_embeddings[0][0:2])
    print(len(doc_embeddings[0]))
    """
    After conversion:

    document_embeddings becomes a 2D NumPy array

    Shape:
        (number_of_documents, embedding_dimension)

    Example:
        (104, 1536)

    That means:
        - 104 documents
        - Each document has a 1536-dimensional vector
    """
    
    return doc_embeddings



#or look at similarity API in https://github.com/sanand0/aipipe?tab=readme-ov-file#native-provider-api-keys
def vector_search1(docs,query, k=3):
    """Initial retrieval using vector similarity"""
    start_time = time.time()   #Track latency in milliseconds
     
     #if cohere
     # Get query embedding
    # query_response = co.embed(
    #     texts=[query],
    #     model="embed-english-light-v3.0",
    #     input_type="search_query"
    # )
    # query_emb = np.array(query_response.embeddings[0])
    #Get query embedding
    query_response = openai.embeddings.create(
        model="text-embedding-3-small",  # model supported by AI Pipe
        input=query
    )
  
    query_emb = np.array(query_response.data[0].embedding)
    doc_embeddings=compute_embeddings1(docs)
    print(doc_embeddings.shape) #eg (104,1053)..104 docs each has 1053 dimension embedding
    print(f"Computed {len(doc_embeddings)} embeddings") #104 
    # Compute cosine similarities
    similarities = []
    for i, doc_emb in enumerate(doc_embeddings):
        sim = np.dot(query_emb, doc_emb) / (
            np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)
        )
        similarities.append({
            "score": float(sim),
            "content": docs[i],
            
        })
        """
        document_embeddings is a 2D NumPy array:

            Shape:
                (num_documents, embedding_dimension)

        doc_emb is one document vector:
            Shape:
                (1536,)
        """

        # Cosine similarity formula:
        #
        # sim = (A · B) / (||A|| * ||B||)
        #
        # A · B          → dot product
        # ||A||, ||B||   → vector magnitudes (Euclidean norm)
        #
        # Result range:
        #   -1 → opposite meaning
        #    0 → unrelated
        #    1 → very similar

    """
    similarities now looks like:

    [
        {
            "score": 0.8234,
            "content": "Machine learning is a subset of AI.",
            
        },
        {
            "score": 0.7121,
            "content": "FastAPI is a Python framework.",
            
        ...
    ]

    One entry per document.
    """

    # -----------------------------------
    # STEP 3: Sort by similarity score
    # -----------------------------------
    similarities.sort(key=lambda x: x["score"], reverse=True)
    latency = int((time.time() - start_time) * 1000)
    
    return similarities[:k], latency


# def rerank_with_cohere(query, candidates, top_k=3):
#     #candidates is from vector search so its a list of dicts
#     """Re-rank using Cohere's rerank API"""
#     start_time = time.time()
    
#     # Prepare documents for reranking
#     docs = [c["content"] for c in candidates]
    
#     # Use Cohere's rerank endpoint
#     response = co.rerank(
#         query=query,
#         documents=docs,
#         top_n=top_k,
#         model="rerank-english-v3.0"
#     )
    
#     """
#     --------------------------------------
#     What Cohere's rerank response looks like
#     --------------------------------------
#     response = {
#         "results": [
#             {
#                 "index": 2,                # index of doc in original 'docs' list
#                 "relevance_score": 0.92    # how relevant doc is to query (0 to 1)
#             },
#             {
#                 "index": 0,
#                 "relevance_score": 0.78
#             },
#             ...
#         ]
#     }

#     IMPORTANT:
#     - index → tells which original document matched
#     - relevance_score → semantic relevance (higher = better)
#     - results are already sorted in descending relevance
#     """
    
#     # Map back to original documents with new scores
#     results = []
#     for result in response.results:
#         idx = result.index
#         results.append({
#             "score": float(result.relevance_score),
#             "content": candidates[idx]["content"]
            
#         })
    
#     latency = int((time.time() - start_time) * 1000)
#     return results, latency


@app.post("/similarity", response_model=SearchResponse1)
async def similarity(req: SearchRequest1):
    try:
        
        # Vector search
        #when i used just 3 here without reranking the result was not correct ..so iam doint my vector search with total length of docs then reranking to 3 with the help of llm
        candidates, search_latency = vector_search1(req.docs,req.query,3) #if reranking use len(docs) not 3
        results=candidates
        #if reranking
        # results, rerank_latency = rerank_with_cohere(req.query, candidates, 3)
        
        result_objects = [
            r["content"] for r in results
        ]

        return SearchResponse1(
            matches=result_objects
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#############################################Q19####################################################

#dont use this for vercel

# if __name__ == "__main__":
#     print("Initializing with (FastAPI)...")
#     load_documents()
#     compute_embeddings()
#     print("Ready!")
#     print(document_embeddings[0])
#     print(len(document_embeddings[0]))
#     print("API Docs: http://localhost:8000/docs")
#     uvicorn.run(app,port=8000)

#use
@app.on_event("startup")
async def startup_event():
    print("Initializing with FastAPI...")
    load_documents()
    compute_embeddings()
    print("Ready!")
    print(document_embeddings[0])
    print(len(document_embeddings[0]))
