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
wh_df = pd.read_csv("q-geospatial-python-closest-warehouses.csv")
order_df = pd.read_csv("q-geospatial-python-closest-orders.csv")



# Compute distance to each warehouse
for wh_id in wh_df["warehouse_id"]:
    lat = wh_df[wh_df["warehouse_id"] == wh_id]["latitude"].iloc[0]
   
    lon = wh_df[wh_df["warehouse_id"] == wh_id]["longitude"].iloc[0]
    order_df[wh_id] = order_df.apply(
        lambda row: haversine(row["latitude"], row["longitude"], lat, lon),
        axis=1
    )

# Assign nearest warehouse
order_df["Assigned"] = order_df[wh_df["warehouse_id"]].idxmin(axis=1)
print(order_df.head())

# Count deliveries
counts = order_df["Assigned"].value_counts()
print(counts)
print(type(counts))#series
# Find busiest warehouse
warehouse = counts.idxmax()#row index of max value
count = counts.max()#max value

print(f"{warehouse}, {count} orders")