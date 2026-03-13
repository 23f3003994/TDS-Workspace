# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas"]
# ///


import pandas as pd
import math

#uv run script.py 
# Haversine Formula (for reference):

# R = 6371 km (Earth's mean radius)
# Δlat = lat2 − lat1 (in radians)
# Δlon = lon2 − lon1 (in radians)
# a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
# distance = R × 2 × atan2(√a, √(1−a))

df = pd.read_csv("rideshare_trips.csv")
df["start_time"] = pd.to_datetime(df["start_time"], format='ISO8601')

# Step A: Filter peak hours
df["hour"] = df["start_time"].dt.hour
peak = df[(df["hour"] >= 17) & (df["hour"] < 21)]

# Step B: Haversine distance
def haversine(row):
    R = 6371
    lat1, lon1 = math.radians(row["pickup_lat"]), math.radians(row["pickup_lon"])
    lat2, lon2 = math.radians(row["dropoff_lat"]), math.radians(row["dropoff_lon"])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

peak = peak.copy()
peak["dist_km"] = peak.apply(haversine, axis=1)
print(peak.head())
long_trips = peak[peak["dist_km"] > 4]
print(long_trips.head())


# Step C: Top driver
result = long_trips.groupby("driver_id")["fare_amount"].sum()
print(result.head())
print(type(result))#series  

top_driver = result.idxmax()#index is driver id now 
top_fare = round(result.max(), 2)
print(f"{top_driver}, {top_fare}")



