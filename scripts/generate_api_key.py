#!/usr/bin/env python3
"""Generate and rotate API keys stored in secrets/api_keys.json"""
import os
import json
import secrets
from pathlib import Path

SECRETS_DIR = Path(__file__).resolve().parents[1] / "secrets"
SECRETS_DIR.mkdir(parents=True, exist_ok=True)
KEY_FILE = SECRETS_DIR / "api_keys.json"

def load_keys():
    if KEY_FILE.exists():
        return json.loads(KEY_FILE.read_text())
    return {"keys": []}

def save_keys(data):
    KEY_FILE.write_text(json.dumps(data, indent=2))

def generate_key(note: str = ""):
    k = secrets.token_urlsafe(32)
    data = load_keys()
    data.setdefault("keys", [])
    data["keys"].append({"key": k, "note": note})
    save_keys(data)
    return k

def list_keys():
    data = load_keys()
    for i, item in enumerate(data.get("keys", []), 1):
        print(i, item.get("note", ""), item.get("key")[:8] + "...")

def revoke(index: int):
    data = load_keys()
    keys = data.get("keys", [])
    if 0 <= index < len(keys):
        removed = keys.pop(index)
        save_keys(data)
        print("Removed:", removed.get("note"))
    else:
        print("Index out of range")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--generate", "-g", action="store_true", help="Generate a new API key")
    p.add_argument("--note", "-n", default="", help="Note to associate with key")
    p.add_argument("--list", "-l", action="store_true", help="List keys")
    p.add_argument("--revoke", "-r", type=int, help="Revoke key by 0-based index")
    args = p.parse_args()
    if args.generate:
        k = generate_key(args.note)
        print("New API key:", k)
    elif args.list:
        list_keys()
    elif args.revoke is not None:
        revoke(args.revoke)
    else:
        p.print_help()
