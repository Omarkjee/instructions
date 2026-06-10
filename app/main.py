from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi import Header
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.ocr import analyze_image_bytes
import uvicorn
import os
import logging
import json
from pathlib import Path
import json
from datetime import datetime

app = FastAPI(title="Label Verifier Prototype")

app.mount("/static", StaticFiles(directory="static"), name="static")

API_KEY = os.environ.get("API_KEY")
DATA_DIR = os.environ.get("DATA_DIR", "/data")
SECRETS_PATH = Path(__file__).resolve().parents[1] / "secrets" / "api_keys.json"
allowed_keys = None
if SECRETS_PATH.exists():
    try:
        allowed_keys = json.loads(SECRETS_PATH.read_text()).get("keys", [])
        allowed_keys = {k["key"] for k in allowed_keys}
    except Exception:
        allowed_keys = None

# logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("label-verifier")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return FileResponse("static/index.html")


def _check_api_key(request: Request):
    if API_KEY:
        key = request.headers.get("x-api-key") or request.headers.get("X-API-KEY")
        if not key or key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _persist_result(res: dict):
    try:
        if DATA_DIR:
            os.makedirs(DATA_DIR, exist_ok=True)
            path = os.path.join(DATA_DIR, "results.jsonl")
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("Failed to persist result: %s", e)


@app.post("/api/verify")
async def verify(request: Request, files: list[UploadFile] | None = None):
    # API key check: 1) check secrets file keys 2) fallback to single API_KEY env
    key = request.headers.get("x-api-key") or request.headers.get("X-API-KEY")
    if allowed_keys is not None:
        if not key or key not in allowed_keys:
            raise HTTPException(status_code=401, detail="invalid api key")
    elif API_KEY:
        if not key or key != API_KEY:
            raise HTTPException(status_code=401, detail="invalid api key")
    if not files:
        return JSONResponse({"error": "No files uploaded"}, status_code=400)

    results = []
    for f in files:
        data = await f.read()
        result = analyze_image_bytes(data)
        result["filename"] = f.filename
        result["timestamp"] = datetime.utcnow().isoformat() + "Z"
        results.append(result)
        logger.info("Processed %s, needs_manual_review=%s, confidence=%s", f.filename, result.get("needs_manual_review"), result.get("confidence"))
        _persist_result({"filename": f.filename, "result": result})

    return {"results": results}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")
