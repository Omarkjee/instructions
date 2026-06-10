# TODO — Project Status

## Completed
- Read and extracted requirements from original `README.md`.
- Implemented FastAPI prototype: `app/main.py` and `app/ocr.py`.
- Added minimal frontend: `static/index.html`.
- Added `Dockerfile` and `requirements.txt`.
- Added sample generator: `scripts/generate_samples.py` and sample images.
- Added basic integration test: `tests/test_verify.py`.
- Added Azure deploy helper: `deploy/deploy_to_azure.sh`.
- Consolidated documentation into single `README.md` and removed extra docs.
- Verified local run via Docker and posted sample image to `/api/verify`.

## In progress
- Obtain or provide a public/deployed application URL (Azure deployment blocked by subscription/SP permissions).

## Remaining / Recommended Next Steps
1. Resolve Azure permissions or have admin run `deploy/deploy_to_azure.sh` to publish to App Service.
2. Validate deployed public URL and update `README.md` with final URL and access notes.
3. Improve extraction accuracy:
   - Add image deskewing/denoising, tuned OCR configuration, and stronger regex rules.
   - Replace or augment OCR with a lightweight ML model for field detection.
4. Add authentication / access control for Treasury testing (App Service Auth or simple token).
5. Add logging, persistent storage (optional), and audit trail for review workflows.
6. Expand test coverage with real label images and edge cases (angles, glare, fonts).
7. Add CI/CD pipeline to build & push Docker image and run tests.
8. Produce final handoff artifacts: single-page user guide, test dataset, and deploy/run checklist for IT.

## Quick Run Commands
- Build Docker image:
  `docker build -t label-verifier:latest .`
- Run container:
  `docker run --rm --name label-verifier -p 8000:8000 label-verifier:latest`
- Local (no Docker) run (requires system Tesseract):
  ```
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
- Generate samples (local or inside container):
  `python scripts/generate_samples.py`
  or
  `docker run --rm -v "$(pwd)":/work -w /work label-verifier:latest python3 scripts/generate_samples.py`
- Deploy to Azure (example):
  `bash deploy/deploy_to_azure.sh <resourceGroup> <acrName> <appName> <location>`

## Next action for you
- Option 1 (recommended): ask your Azure admin to re-enable the subscription and either run the deploy script or create a service principal for deployment; paste the final URL here and I will validate and finalize the deliverable.
- Option 2: expose local instance with `ngrok http 8000` and paste the forwarding URL so I can validate remotely.
