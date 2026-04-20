from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

df = pd.read_csv(os.path.join(BASE_DIR, "sensor_data.csv"), parse_dates=["timestamp"])
cache = {}

@app.get("/stats")
def get_stats(
    response: Response,
    location: Optional[str] = None,
    sensor: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    cache_key = (location, sensor, start_date, end_date)
    if cache_key in cache:
        response.headers["X-Cache"] = "HIT"
        return cache[cache_key]

    filtered = df.copy()
    if location:
        filtered = filtered[filtered["location"] == location]
    if sensor:
        filtered = filtered[filtered["sensor"] == sensor]
    if start_date:
        filtered = filtered[filtered["timestamp"] >= pd.to_datetime(start_date, utc=True)]
    if end_date:
        filtered = filtered[filtered["timestamp"] <= pd.to_datetime(end_date, utc=True)]

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

    cache[cache_key] = result
    response.headers["X-Cache"] = "MISS"
    return result
