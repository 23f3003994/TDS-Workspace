import hashlib
import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/config")
async def config():
    theme = os.environ.get("THEME_COLOR", "NOT_SET")
    mode = os.environ.get("APP_MODE", "NOT_SET")
    build = os.environ.get("BUILD_NUMBER", "NOT_SET")
    config_str = f"{theme}:{mode}:{build}"
    config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:12]
    return {
        "theme_color": theme,
        "app_mode": mode,
        "build_number": build,
        "config_hash": config_hash
    }
