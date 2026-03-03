import json
from datetime import datetime

file_path = "q-json-sensor-rollup.jsonl"

start_time = datetime.fromisoformat("2024-06-02T07:59:45.042+00:00")
end_time = datetime.fromisoformat("2024-06-15T07:59:45.042+00:00")

total_temp = 0
count = 0

with open(file_path, "r") as f:
    for line in f:
        record = json.loads(line)

        # Filter site
        if record["site"] != "Lab-East":
            continue

        # Filter device prefix
        if not record["device"].startswith("condenser"):
            continue

        # Filter status
        if record["status"] in ["maintenance", "offline"]:
            continue

        # Filter time window
        timestamp = datetime.fromisoformat(
            record["captured_at"].replace("Z", "+00:00")
        )

        if not (start_time <= timestamp <= end_time):
            continue

        # Extract temperature
        temp_value = record["metrics"]["temperature"]["value"]
        temp_unit = record["metrics"]["temperature"]["unit"]

        # Convert to Celsius if needed
        if temp_unit == "F":
            temp_value = (temp_value - 32) * 5/9

        total_temp += temp_value
        count += 1

# Compute final average
if count > 0:
    average_temp = round(total_temp / count, 2)
    print("Average temperature:", average_temp, "°C")
else:
    print("No valid records found.")