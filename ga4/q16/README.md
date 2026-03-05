# Cross-Lingual Entity Disambiguation Challenge

## Dataset
- **documents.jsonl**: 1000 historical document excerpts across 15 languages
- **entity_reference.csv**: Reference list of 19 canonical historical entities

## Document Format (JSONL)
Each line is a JSON object with:
- `doc_id`: Unique document identifier (DOC-0001 to DOC-1000)
- `language`: ISO 639-1 language code (en, es, fr, de, it, pt, nl, ru, pl, cs, ar, zh, ja, ko, tr)
- `year`: Year of the event described
- `text`: The document text mentioning a historical figure
- `mentioned_name`: The name as it appears in the document (may include typos)
- `source_region`: Geographic region

## Entity Reference CSV
Contains canonical entity information:
- `entity_id`: Unique entity identifier (E001, E002, ...)
- `canonical_name`: The standardised English name
- `role`: Historical role (King, Emperor, etc.)
- `era`: Time period
- `region`: Geographic origin

## Task
Map each document to its correct entity_id. Names like "Juan", "Jean", "Johann",
"Giovanni", "João", and "Ivan" may all refer to DIFFERENT historical persons.
Your pipeline must disambiguate based on context, era, region, and cross-lingual
name equivalences.

## Output Format
Submit a CSV with exactly two columns:
```
doc_id,entity_id
DOC-0001,E003
DOC-0002,E017
...
```
