
"""
Sentiment Analysis API using FastAPI and OpenAI GPT.

This module provides a FastAPI application that analyzes the sentiment of user comments
using OpenAI's GPT model. It includes CORS support for cross-origin requests and
validates input/output using Pydantic models.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal
from pydantic import BaseModel, Field
from openai import OpenAI

# Create OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)

# Create FastAPI app
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class CommentRequest(BaseModel):
    """
    Request model for comment analysis.

    Attributes:
        comment (str): The user comment to analyze for sentiment.
    """
    comment: str

class SentimentResponse(BaseModel):
    """
    Response model for sentiment analysis.

    Attributes:
        sentiment (Literal["positive", "negative", "neutral"]): The sentiment classification.
        rating (int): A rating from 1 to 5 (1=highly negative, 3=neutral, 5=highly positive).
    """
    sentiment: Literal["positive", "negative", "neutral"]
    rating: int = Field(..., ge=1, le=5)

@app.post("/comment", response_model=SentimentResponse)
async def analyze_comment(request: CommentRequest):
    """
    Analyze the sentiment of a user comment using OpenAI GPT.

    This endpoint takes a comment, sends it to the OpenAI GPT model for sentiment analysis,
    and returns the sentiment classification and rating.

    Args:
        request (CommentRequest): The request containing the comment to analyze.

    Returns:
        SentimentResponse: The sentiment analysis result with sentiment and rating.

    Raises:
        HTTPException: If the comment is empty (422) or if there's an API error (500).

    LLM Response Format:
        The LLM is instructed to return a JSON object in the following format:
        {
            "sentiment": "positive" | "negative" | "neutral",
            "rating": 1-5 (integer, where 1=highly negative, 3=neutral, 5=highly positive)
        }
        Example: {"sentiment": "positive", "rating": 4}
    """
    # Validate input: check if comment is empty or whitespace-only
    if not request.comment or not request.comment.strip():
        raise HTTPException(status_code=422, detail="Comment cannot be empty")

    try:
        # Call OpenAI API for sentiment analysis
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a sentiment analysis assistant. "
                        "Analyze the sentiment of the given comment and return a JSON object with:\n"
                        "- sentiment: one of 'positive', 'negative', or 'neutral'\n"
                        "- rating: integer from 1 to 5 (5=highly positive, 3=neutral, 1=highly negative)\n"
                        "Return only valid JSON, nothing else."
                    )
                },
                {
                    "role": "user",
                    "content": request.comment
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "sentiment_analysis",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "sentiment": {
                                "type": "string",
                                "enum": ["positive", "negative", "neutral"]
                            },
                            "rating": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5
                            }
                        },
                        "required": ["sentiment", "rating"],
                        "additionalProperties": False
                    }
                }
            }
        )

        # The 'response' variable is a ChatCompletion object from OpenAI API.
        # Structure:
        # response.choices: list of completion choices (usually 1 item)
        # response.choices[0].message.content: the JSON string returned by the LLM
        # Example content: '{"sentiment": "positive", "rating": 4}'
        #
        # Full example of the 'response' object:
        # {
        #   "id": "chatcmpl-123",
        #   "object": "chat.completion",
        #   "created": 1677652288,
        #   "model": "gpt-4.1-mini",
        #   "choices": [
        #     {
        #       "index": 0,
        #       "message": {
        #         "role": "assistant",
        #         "content": "{\"sentiment\": \"positive\", \"rating\": 4}"
        #       },
        #       "finish_reason": "stop"
        #     }
        #   ],
        #   "usage": {
        #     "prompt_tokens": 50,
        #     "completion_tokens": 10,
        #     "total_tokens": 60
        #   }
        # }

        # Parse the JSON response from the LLM
        import json
        result = json.loads(response.choices[0].message.content)
        return SentimentResponse(sentiment=result["sentiment"], rating=result["rating"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API error: {str(e)}")
