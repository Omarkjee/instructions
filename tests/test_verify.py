import requests
from pathlib import Path

BASE = "http://localhost:8000"


def test_verify_samples():
    base_dir = Path(__file__).parent.parent / "static"
    candidates = list((base_dir / "samples_augmented").glob("*.png"))
    if not candidates:
        candidates = list((base_dir / "samples").glob("*.png"))
    assert candidates, "No sample images found for test"

    files = []
    open_fhs = []
    for p in candidates[:3]:
        fh = p.open("rb")
        open_fhs.append(fh)
        files.append(("files", (p.name, fh, "image/png")))

    try:
        resp = requests.post(f"{BASE}/api/verify", files=files)
    finally:
        for fh in open_fhs:
            fh.close()
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    for r in data["results"]:
        assert "needs_manual_review" in r
        assert "confidence" in r


if __name__ == "__main__":
    print("Run this after starting the app locally:")
    print("python -m pytest tests/test_verify.py -q")
