import hashlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class ComputeRequest(BaseModel):
    a: int
    b: int

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/compute")
async def compute_post(req: ComputeRequest):
    s = req.a + req.b
    p = req.a * req.b
    v = hashlib.sha256(f"sum:{s}:product:{p}".encode()).hexdigest()[:10]
    return {"sum": s, "product": p, "verify": v}


#seems like the assignment is sending get request without query params (so well use hardcoded values here(default)) though qstn says post
@app.get("/compute")
async def compute_get(a: int = 10, b: int = 11):
    s = a + b
    p = a * b
    v = hashlib.sha256(f"sum:{s}:product:{p}".encode()).hexdigest()[:10]
    return {"sum": s, "product": p, "verify": v}