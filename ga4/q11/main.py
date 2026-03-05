
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from openai import OpenAI
import os
import json

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class SentencesRequest(BaseModel):
    sentences: List[str]

class SentimentResult(BaseModel):
    sentence: str
    sentiment: str

class SentencesResponse(BaseModel):
    results: List[SentimentResult]


@app.post("/sentiment", response_model=SentencesResponse)
def analyze_sentiment(data: SentencesRequest):

    numbered = "\n".join(f"{i+1}. {s}" for i, s in enumerate(data.sentences))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sentiment classifier. "
                    "Classify each sentence as exactly one of: happy, sad, neutral."
                )
            },
            {
                "role": "user",
                "content": f"Classify the sentiment of each sentence:\n{numbered}"
            }
        ],
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "sentiment_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sentence": {"type": "string"},
                                    "sentiment": {
                                        "type": "string",
                                        "enum": ["happy", "sad", "neutral"]
                                    }
                                },
                                "required": ["sentence", "sentiment"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["results"],
                    "additionalProperties": False
                }
            }
        }
    )

    parsed = json.loads(response.choices[0].message.content)

    # Preserve original sentence text and order
    results = [
        {"sentence": original, "sentiment": item["sentiment"]}
        for original, item in zip(data.sentences, parsed["results"])
    ]

    return {"results": results}