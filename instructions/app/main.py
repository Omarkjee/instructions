from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.ocr import analyze_image_bytes
import uvicorn

app = FastAPI(title="Label Verifier Prototype")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return FileResponse("static/index.html")


@app.post("/api/verify")
async def verify(files: list[UploadFile] | None = None):
    if not files:
        return JSONResponse({"error": "No files uploaded"}, status_code=400)

    results = []
    for f in files:
        data = await f.read()
        result = analyze_image_bytes(data)
        result["filename"] = f.filename
        results.append(result)

    return {"results": results}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")
