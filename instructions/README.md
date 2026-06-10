# AI-Powered Alcohol Label Verification — Prototype

This single README consolidates project background, technical requirements, setup & run instructions, a short design summary, deployment notes, and sample outputs for the prototype.

---

## Project Background (summary)

- Stakeholders: TTB Compliance Division (label reviewers and IT). They need a fast, reliable tool to verify label fields (brand, ABV, net contents, bottler, government warning).
- Goals: reduce manual verification time, support batch uploads, maintain a simple UI usable by low-tech users, and return results quickly (target ≈5s per label for adoption).
- Constraints: prototype is standalone (no COLA integration), avoid storing PII, and be mindful of Treasury network/firewall restrictions.

---

## Technical Requirements (summary)

- Extract label fields: brand name, class/type, alcohol content (ABV), net contents, bottler, country of origin, Government Health Warning.
- Provide a simple web UI for single and batch uploads and a programmatic API endpoint for verification.
- Deliverables: source repository, a single README (this file), and a public or sharable deployed prototype URL.

---

## What I built (contents)

- FastAPI backend: `app/main.py` exposes `GET /` (UI) and `POST /api/verify` (image upload).
- OCR helper: `app/ocr.py` uses `pytesseract` with basic preprocessing and regex extractors for ABV/net/warning/brand.
- Minimal frontend: `static/index.html` (single-page upload + results).
- Utility scripts: `scripts/generate_samples.py` (produce simple test label images).
- Tests: `tests/test_verify.py` (basic integration test that posts sample images to the running server).
- Container: `Dockerfile` that installs Tesseract and runs the FastAPI app.
- Deployment helper: `deploy/deploy_to_azure.sh` — guidance to push to ACR and create an App Service.

All source files live in this repository. Run and deployment instructions are below.

---

## Setup & Run (recommended: Docker)

Prerequisites: Docker Desktop (with WSL integration on Windows) or a Linux host with Docker. Docker includes Tesseract in the image so you don't need to install system OCR packages.

1) Build the image (run from the repo root):

```bash
docker build -t label-verifier:latest .
```

2) Run the container (foreground):

```bash
docker run --rm --name label-verifier -p 8000:8000 label-verifier:latest
```

3) Open the UI in a browser:

http://localhost:8000

4) API usage (single image):

```bash
curl -s -X POST -F "files=@./static/samples/sample1.png" http://localhost:8000/api/verify | python3 -m json.tool
```

Notes:
- If Docker is unavailable, see the Local Python instructions below.

---

## Local Python Run (no Docker)

Prerequisites:
- Python 3.9+ and system Tesseract OCR installed and on PATH.

On Debian/Ubuntu (example):

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip tesseract-ocr libtesseract-dev

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/generate_samples.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

Windows notes:
- Install Tesseract for Windows and add it to PATH. Activate venv with PowerShell: `.\.venv\Scripts\Activate.ps1`.

---

## Testing

- Generate sample images (either locally or inside Docker):

```bash
python scripts/generate_samples.py
# or inside Docker: docker run --rm -v "$(pwd)":/work -w /work label-verifier:latest python3 scripts/generate_samples.py
```

- Run the included test (requires `pytest`):

```bash
pytest -q
```

---

## API

- `GET /` — minimal frontend page.
- `POST /api/verify` — accept one or more `files` form fields (image uploads). Returns JSON with `results` array; each item contains `raw_text`, `brand`, `abv`, `net_contents`, `government_warning`, and `filename`.

Example response:

```json
{
   "results": [
      {
         "raw_text": "...",
         "brand": "OLD TOM DISTILLERY",
         "abv": "45% Alc./Vol. (90 Proof)",
         "net_contents": "750 mL",
         "government_warning": "GOVERNMENT WARNING: ...",
         "filename": "sample1.png"
      }
   ]
}
```

---

## Brief Design & Approach

- Approach: lightweight, pragmatic prototype that prioritizes speed and clarity over full ML accuracy. We use OCR (pytesseract) plus deterministic regex and heuristics to extract fields. This keeps the prototype self-contained and avoids dependency on external ML APIs which may be blocked in Treasury networks.
- Batch uploads: accepted by the `POST /api/verify` endpoint; the backend processes each image and returns an array of results.
- UI: intentionally minimal — large buttons, simple flow, accessible for low-tech users.

Tools used:
- Python, FastAPI, Uvicorn
- Pillow, pytesseract (Tesseract OCR)
- Docker for packaging
- Optional: Azure CLI script for container deployment

Assumptions & trade-offs:
- Prototype is standalone — no COLA integration or persistent storage.
- No long-term PII retention; images are processed and not stored (ephemeral in this deliverable).
- OCR-based approach may struggle with angled or low-quality photos; production would benefit from ML-based detection models and image preprocessing pipelines.

---

## Deployment (Azure example)

I included `deploy/deploy_to_azure.sh` that:
- Creates an Azure Container Registry (ACR), pushes the Docker image, and creates an App Service that runs the container. The script requires `az` CLI, `docker`, and an active Azure subscription.

If your subscription or permissions are restricted, you can either ask your Azure admin to run the script, or expose the running local instance via `ngrok` for short-term external testing:

```bash
ngrok http 8000
# then share the https://... forwarding URL
```

Security note: for Treasury testing you may prefer App Service with IP allowlisting or App Service Authentication; coordinate with your IT.

---

## Sample Run (local)

I tested the prototype locally (Docker) and posted a generated sample image. The prototype returned `raw_text` and extracted a plausible `brand` string; ABV/net/warning were not present in that synthetic sample.

Example discovered during local run (trimmed):

```
{
   "results": [
      {
         "raw_text": "Ae BS bas Ne 0 et ...",
         "brand": "Ae BS bas Ne 0 et",
         "abv": null,
         "net_contents": null,
         "government_warning": null,
         "filename": "sample1.png"
      }
   ]
}
```

---

## Files of interest

- `app/` — FastAPI app and OCR helpers
- `static/index.html` — frontend
- `Dockerfile`, `requirements.txt`
- `scripts/generate_samples.py`, `tests/test_verify.py`
- `deploy/deploy_to_azure.sh` — Azure deploy helper

---

## Next steps I can help with

- Deploy to Azure and validate public URL (I can validate once you provide the URL or run the script yourself and paste it here).
- Improve extraction accuracy (add image preprocessing, custom regex, or ML models).
- Add authentication, logging, and persistence for production readiness.

If you want me to proceed with any of the above, tell me which option and I'll implement it.

---

Thank you — the code and scripts are in this repository; run the Docker instructions above to start the prototype.

```
