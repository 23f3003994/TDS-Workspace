#run on a different port coz we will have to run all servers simultaneously

#python3 main.py runs faster than uv run main.py (python3 works as i have installed all dependencies globally)
# ngrok http 8001 in another poweshell
#and go to http://..../docs try out search
#ans is http://..../search
#sometimes permission error issues of api key can happen-just run again
#used claude-ai's help to generate some parts-tds-ga1/q-18-fastapi-claudai is the file it gave
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
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
openai.api_base = os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1") #.environ.get("ENV_VARIABLE_NAME", "default_value")

# Initialize Cohere # for reranking ..actually can use the same for vector similarity, compute embeddings too
co = cohere.Client(os.environ.get("COHERE_API_KEY", "")) #free account key setup

#export COHERE_API_KEY=############################################

#must set them
# export OPENAI_API_KEY=###########################################
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
#ngrok http 8001

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




# Pydantic models
class SearchRequest(BaseModel):
    docs: List[str]
    query: str

# if rerank is True
#     rerank top k
#     select top rerankK




class SearchResponse(BaseModel):
    matches: List[str]
    


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




def compute_embeddings(documents):
    """Compute embeddings using OpenAI"""
    
    print("Computing embeddings with OPenAI...")
    #list of contents
    texts = documents


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
    print(document_embeddings[0][0:2])
    print(len(document_embeddings[0]))
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
    
    return document_embeddings



#or look at similarity API in https://github.com/sanand0/aipipe?tab=readme-ov-file#native-provider-api-keys
def vector_search(documents,query, k=3):
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
    document_embeddings=compute_embeddings(documents)
    print(document_embeddings.shape) #eg (104,1053)..104 docs each has 1053 dimension embedding
    print(f"Computed {len(document_embeddings)} embeddings") #104 
    # Compute cosine similarities
    similarities = []
    for i, doc_emb in enumerate(document_embeddings):
        sim = np.dot(query_emb, doc_emb) / (
            np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)
        )
        similarities.append({
            "score": float(sim),
            "content": documents[i],
            
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

@app.post("/similarity", response_model=SearchResponse)
async def similarity(req: SearchRequest):
    try:
        
        # Vector search
        #when i used just 3 here without reranking the result was not correct ..so iam doint my vector search with total length of docs then reranking to 3 with the help of llm
        candidates, search_latency = vector_search(req.docs,req.query,3) #if reranking use len(docs) not 3
        results=candidates
        #if reranking
        # results, rerank_latency = rerank_with_cohere(req.query, candidates, 3)
        
        result_objects = [
            r["content"] for r in results
        ]

        return SearchResponse(
            matches=result_objects
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    print("Initializing with (FastAPI)...")
    uvicorn.run(app,port=8001)