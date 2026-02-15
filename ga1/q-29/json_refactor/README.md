# Refactor JSON for Compression
## IoT Sensor Data Compression

## Task

You have a JSON file with 200 sensor readings. Each record is an object with 6 fields.

**Problem:** This format is inefficient - column names are repeated 200 times!

**Solution:** Refactor to a columnar format:
```json
{
  "columns": ["field1", "field2", ...],
  "rows": [
    [value1, value2, ...],
    [value1, value2, ...],
    ...
  ]
}
```

This format:
- Stores column names only once
- Each row is just an array of values
- Reduces file size by ~40-60%
- Commonly used in data warehouses and analytics

## Instructions

1. Read `data.json`
2. Extract the column names from the first object
3. Convert each object to an array of values (in column order)
4. Create output: `{"columns": [...], "rows": [[...], [...], ...]}`
5. Submit the refactored JSON

## Example

**Before:**
```json
[
  {"id": 1, "name": "Alice", "score": 95},
  {"id": 2, "name": "Bob", "score": 87}
]
```

**After:**
```json
{
  "columns": ["id", "name", "score"],
  "rows": [
    [1, "Alice", 95],
    [2, "Bob", 87]
  ]
}
```
