import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# Haversine function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


# Load CSV
df = pd.read_csv("q-geospatial-nearest-warehouse.csv")

# Warehouse coordinates
warehouses = {
    "Delhi": (28.6139, 77.209),
    "Mumbai": (19.076, 72.8777),
    "Chennai": (13.0827, 80.2707)
}

# Compute distance to each warehouse
for name, (lat, lon) in warehouses.items():
    df[name] = df.apply(
        lambda row: haversine(row["Latitude"], row["Longitude"], lat, lon),
        axis=1
    )

# Assign nearest warehouse
df["Assigned"] = df[["Delhi", "Mumbai", "Chennai"]].idxmin(axis=1)
print(df.head())

# Count deliveries
counts = df["Assigned"].value_counts()
print(counts)
print(type(counts))#series
# Find busiest warehouse
warehouse = counts.idxmax()#row index of max value
count = counts.max()#max value

print(f"{warehouse}, {count}")