# TDS-Workspace/ga2/q-18/main.py

from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Enable CORS for all origins
# Middleware handles most requests automatically
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all websites
    allow_methods=["POST"],  # allow POST requests only
    allow_headers=["*"],  # allow all headers
    expose_headers=["*"] # expose all headers ie allow client side JS to access them
)
MAX_FILE_SIZE = 51 * 1024  # 51 KB
VALID_EXTENSIONS = [".csv", ".json", ".txt"]
AUTH_TOKEN = "7roiysrjz08dr6co"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), x_upload_token_9272: str = Header(None)):

    # --- Step 1: Validate API token ---
    if x_upload_token_9272 != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing token")

    # --- Step 2: Validate file type ---
    if not any(file.filename.endswith(ext) for ext in VALID_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # --- Step 3: Read file content and validate size ---
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # --- Step 4: Process CSV ---
    if file.filename.endswith(".csv"):
        try:
            # Convert bytes to pandas dataframe
            from io import StringIO
            df = pd.read_csv(StringIO(contents.decode("utf-8")))

            total_value = df["value"].sum()
            category_counts = df["category"].value_counts().to_dict()

            return {
                "email": "23f3003994@ds.study.iitm.ac.in",
                "filename": file.filename,
                "rows": len(df),
                "columns": list(df.columns),
                "totalValue": total_value,
                "categoryCounts": category_counts
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"CSV processing error: {e}")

    return {"message": "File uploaded successfully"}
