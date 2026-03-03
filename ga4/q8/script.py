import re

file_path = "q-parse-partial-json.jsonl"

total_sales = 0

with open(file_path, "r") as f:
    for line in f:
        # Search for sales value using regex
        match = re.search(r'"sales":\s*(\d+)', line)
        
        if match:
            sales_value = int(match.group(1))
            total_sales += sales_value

print("Total Sales:", total_sales)