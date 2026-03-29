from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional
import uvicorn
import os

#uvicorn main:app --reload --host 127.0.0.1 --port 8000
app = FastAPI()

# Enable COR
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize OpenAI client
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""),base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1"))

# Load CSV once at startup
# df = pd.read_csv("sensor_data.csv", parse_dates=["timestamp"])
# Get the directory where main.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "sensor_data.csv")

# Load CSV using absolute path
df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

# Simple dictionary cache: key = query params, value = stats result
cache = {}

@app.get("/stats")
def get_stats(
    response: Response,
    location: Optional[str] = None,
    sensor: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    # Build a cache key from the query parameters
    cache_key = (location, sensor, start_date, end_date)

    # If we've seen this exact request before → return cached result
    if cache_key in cache:
        response.headers["X-Cache"] = "HIT"
        return cache[cache_key]

    # Filter the dataframe step by step
    filtered = df.copy()

    if location:
        filtered = filtered[filtered["location"] == location]
    if sensor:
        filtered = filtered[filtered["sensor"] == sensor]
    if start_date:
        filtered = filtered[filtered["timestamp"] >= pd.to_datetime(start_date,utc=True)]
    if end_date:
        filtered = filtered[filtered["timestamp"] <= pd.to_datetime(end_date,utc=True)]

    # Calculate stats
    if filtered.empty:
        result = {"stats": {"count": 0, "avg": None, "min": None, "max": None}}
    else:
        result = {
            "stats": {
                "count": int(len(filtered)),
                "avg": round(float(filtered["value"].mean()), 4),
                "min": round(float(filtered["value"].min()), 4),
                "max": round(float(filtered["value"].max()), 4),
            }
        }

    # Save to cache for next time
    cache[cache_key] = result
    print(cache_key)
    print(cache)
    response.headers["X-Cache"] = "MISS"
    return result

if __name__ == "__main__":
    uvicorn.run(app, port=8000)

# # Path param — location is IN the URL
# @app.get("/stats/{location}")
# def get_stats(location: str):
#     return {"location": location}

# # Multiple path params
# @app.get("/stats/{location}/{sensor}")
# def get_stats(location: str, sensor: str):
#     return {"location": location, "sensor": sensor}

# # Mix of BOTH path + query params
# @app.get("/stats/{location}")
# def get_stats(
#     location: str,          # 👈 path param (from URL)
#     sensor: Optional[str] = None,      # 👈 query param (after ?)
#     start_date: Optional[str] = None,  # 👈 query param
# ):
#     return {"location": location, "sensor": sensor}
# ```

# Called like:
# ```
# /stats/zone-d?sensor=light&start_date=2024-01-01