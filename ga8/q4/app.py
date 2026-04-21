from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from contextlib import asynccontextmanager
from pydantic import BaseModel

class PredictRequest(BaseModel):
    text: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.classifier = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(req: PredictRequest):
    result = app.state.classifier(req.text)[0]
    return {
        "label": result["label"],
        "score": round(result["score"], 4)
    }