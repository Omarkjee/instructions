import requests
from pathlib import Path

BASE = 'http://localhost:8000'

def test_verify_samples():
    p = Path(__file__).parent.parent / 'static' / 'samples'
    files = []
    for f in p.glob('*.png'):
        files.append(('files', (f.name, open(f, 'rb'), 'image/png')))

    resp = requests.post(f'{BASE}/api/verify', files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert 'results' in data

if __name__ == '__main__':
    print('Run this after starting the app locally:')
    print('python -m pytest tests/test_verify.py -q')
