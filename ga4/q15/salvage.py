import json
import hashlib

total_sum = 0

with open("corrupted_logs.json", "r") as f:
    for line in f:
        try:
            obj = json.loads(line)

            value = obj["context"]["system"]["process"]["metrics"]["metric_3013"]

            total_sum += int(value)

        except Exception:
            continue
print(total_sum)

hash_value = hashlib.sha256(str(total_sum).encode("utf-8")).hexdigest()

print(hash_value, end="")