"""
YouTube Transcript Search API

This FastAPI application provides an endpoint to search YouTube video transcripts
for specific topics. It supports two search methods:
1. Exact string matching in the transcript text
2. Semantic search using Google's Gemini AI model as fallback

The API accepts a YouTube URL and a topic, then returns the timestamp 
where the topic is first mentioned in the video transcript.
"""

import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from urllib.parse import urlparse, parse_qs

# Initialize FastAPI application
app = FastAPI()

# Initialize OpenAI client with custom base URL for Gemini API access
client = OpenAI(
    api_key=os.getenv("AIPIPE_TOKEN"),
    base_url="https://aipipe.org/openrouter/v1"
)

# Configure CORS middleware to allow cross-origin requests from all origins
# This is necessary for browser-based API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers to clients
)


class AskRequest(BaseModel):
    """
    Request model for the /ask endpoint.
    
    Attributes:
        video_url (str): YouTube video URL (supports youtube.com/watch?v=xxx and youtu.be/xxx formats)
        topic (str): The topic/text to search for in the video transcript
    """
    video_url: str
    topic: str


##METHOD-1 : using youtube transcript api to extract the transcript and 
# then doing a string search to find the topic in the transcript and return the timestamp

def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL.
    
    Supports two URL formats:
    - youtu.be/xxxxx (shortened URL)
    - youtube.com/watch?v=xxxxx (full URL)
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: The video ID extracted from the URL
        
    Raises:
        HTTPException: If the URL is invalid or video ID cannot be extracted
    """
    try:
        parsed = urlparse(url)
        # if it's a youtu.be URL, the video ID is the path segment after the hostname
        if parsed.hostname in ("youtu.be",):
            return parsed.path[1:]
        # if it's a youtube.com URL, extract the 'v' query parameter
        video_id = parse_qs(parsed.query).get("v", [None])[0]
        if not video_id:
            raise ValueError("Could not extract video ID")
        return video_id
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")


def fetch_transcript(video_id: str):
    """
    Fetch the transcript for a YouTube video.
    
    Attempts to fetch the transcript in the following order:
    1. English (US) transcript
    2. English transcript
    3. Any available language transcript
    
    Args:
        video_id (str): The YouTube video ID
        
    Returns:
        list: A list of transcript entries (each with 'text' and 'start' timestamp)
        None: If no transcript is available or an error occurs
        
    Raises:
        HTTPException: If the video is unavailable or cannot be found
    """
    ytt = YouTubeTranscriptApi()
    # try en-US and en first, then fall back to any available language
    try:
        return ytt.fetch(video_id, languages=["en-US", "en"])#languages added coz the input given from portal  was in en-US , when i debugged
    except NoTranscriptFound:
        try:
            # Fallback: fetch whatever language is available
            transcript_list = ytt.list(video_id)
            for transcript in transcript_list:
                return transcript.fetch()
        except Exception:
            return None
    except TranscriptsDisabled:
        return None
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="Video not found or unavailable")
    except Exception:
        return None


def ask_gemini(transcript_text: str, topic: str) -> str:
    """
    Use Google's Gemini AI model to perform semantic search on transcript.
    
    Sends the transcript and topic to Gemini API and asks it to find the timestamp
    where the topic is first mentioned, handling semantic variations and context.
    
    Args:
        transcript_text (str): The formatted transcript with timestamps
        topic (str): The topic/text to search for
        
    Returns:
        str: The timestamp in HH:MM:SS format where the topic is found
        
    Raises:
        Exception: If the API call fails
    """
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-lite-001",
        messages=[
            {
                "role": "user",
                "content": f"""Here is a YouTube transcript with timestamps:

{transcript_text}

Find the first timestamp where this is spoken: "{topic}"

Reply with ONLY the timestamp in HH:MM:SS format. Nothing else. Example: 00:05:47"""
            }
        ]
    )
    return response.choices[0].message.content.strip()


@app.post("/ask")
async def ask(request: AskRequest):
    """
    Search a YouTube video transcript for a specific topic.
    
    This endpoint implements a two-stage search strategy:
    1. First attempts exact string matching for performance
    2. Falls back to semantic search using Gemini AI if no exact match is found
    
    Args:
        request (AskRequest): Contains video_url and topic to search for
        
    Returns:
        dict: Contains:
            - timestamp (str): The HH:MM:SS timestamp of the first mention
            - video_url (str): The input video URL
            - topic (str): The input topic
            
    Raises:
        HTTPException: Various status codes for different error conditions:
            - 400: Invalid YouTube URL
            - 404: Video not found or unavailable
            - 422: No transcript available or transcript is empty
            - 500: Gemini API call failed or invalid timestamp format
    """
    # 1. Extract video ID from URL
    video_id = extract_video_id(request.video_url)

    # 2. Fetch transcript for the video
    transcript = fetch_transcript(video_id)

    if not transcript:
        raise HTTPException(status_code=422, detail="No transcript available for this video")

    # 3. Validate transcript is not empty
    entries = list(transcript)
    if not entries:
        raise HTTPException(status_code=422, detail="Transcript is empty")

    # 4. Try exact string search first (faster, no API calls)
    for entry in entries:
        if request.topic.lower() in entry.text.lower():
            # Convert seconds to HH:MM:SS format
            seconds = int(entry.start)
            timestamp = f"{seconds//3600:02}:{(seconds%3600)//60:02}:{seconds%60:02}"
            return {
                "timestamp": timestamp,
                "video_url": request.video_url,
                "topic": request.topic
            }

    # 5. Fallback to Gemini semantic search for complex queries
    # Format transcript with timestamps for Gemini
    transcript_text = "\n".join(
        f"[{int(entry.start)//3600:02}:{(int(entry.start)%3600)//60:02}:{int(entry.start)%60:02}] {entry.text}"
        for entry in entries
    )

    try:
        timestamp = ask_gemini(transcript_text, request.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini call failed: {str(e)}")

    # 6. Validate timestamp format returned from Gemini
    if not re.match(r"^\d{2}:\d{2}:\d{2}$", timestamp):
        raise HTTPException(status_code=500, detail=f"Gemini returned invalid timestamp format: {timestamp}")

    return {
        "timestamp": timestamp,
        "video_url": request.video_url,
        "topic": request.topic
    }


## earlier simpler version of above code without proper error handling (but this worked too)

# def extract_video_id(url: str) -> str:
#     # handles youtu.be/xxx and youtube.com/watch?v=xxx
#     parsed = urlparse(url)
#     if parsed.hostname == "youtu.be":
#         return parsed.path[1:]
#     return parse_qs(parsed.query)["v"][0]


# @app.post("/ask")
# async def ask(request: AskRequest):
#     video_id = extract_video_id(request.video_url)
#     ytt = YouTubeTranscriptApi()
#     transcript = ytt.fetch(video_id, languages=["en-US", "en"])#languages added coz the input given from portal  was in en-US , when i debugged

#     # First try exact string search
#     for entry in transcript:
#         if request.topic.lower() in entry.text.lower():
#             seconds = int(entry.start)
#             timestamp = f"{seconds//3600:02}:{(seconds%3600)//60:02}:{seconds%60:02}"
#             return {
#                 "timestamp": timestamp,
#                 "video_url": request.video_url,
#                 "topic": request.topic
#             }
#     #if  topic not found ie its is null(it occurred actually), we will fallback to semantic search using Gemini
#     # Fallback: send transcript to Gemini for semantic search
#     transcript_text = "\n".join(
#         f"[{int(entry.start)//3600:02}:{(int(entry.start)%3600)//60:02}:{int(entry.start)%60:02}] {entry.text}"
#         for entry in transcript
#     )

#     response = client.chat.completions.create(
#         model="google/gemini-2.0-flash-lite-001",
#         messages=[
#             {
#                 "role": "user",
#                 "content": f"""Here is a YouTube transcript with timestamps:

# {transcript_text}

# Find the first timestamp where this is spoken: "{request.topic}"

# Reply with ONLY the timestamp in HH:MM:SS format. Nothing else. Example: 00:05:47"""
#             }
#         ]
#     )

#     timestamp = response.choices[0].message.content.strip()

#     return {
#         "timestamp": timestamp,
#         "video_url": request.video_url,
#         "topic": request.topic
#     }