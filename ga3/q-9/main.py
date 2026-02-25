import sys
import fitz  # PyMuPDF
import json

# Arguments: pdf file name and word to search
pdf_file = sys.argv[1]
word_to_find = sys.argv[2]

# Open PDF
doc = fitz.open(pdf_file)
page = doc[0]  # first page (index 0)

# Search for the word
rects = page.search_for(word_to_find)

#[Rect(167.49876403808594, 225.6748504638672, 190.06675720214844, 244.91085815429688),Rect(...),....]
# Convert Rect objects to integer lists
bounding_boxes = [[int(r.x0), int(r.y0), int(r.x1), int(r.y1)] for r in rects]

# Print as JSON array
print(json.dumps(bounding_boxes))