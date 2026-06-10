#!/usr/bin/env python3
"""Augment and expand sample label images into static/samples_augmented"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random
import numpy as np
import cv2

ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "static" / "samples"
OUT_DIR = ROOT / "static" / "samples_augmented"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def add_glare(img: Image.Image) -> Image.Image:
    w, h = img.size
    overlay = Image.new("RGB", img.size, (0,0,0))
    draw = ImageDraw.Draw(overlay)
    # bright ellipse
    ex = random.randint(int(w*0.2), int(w*0.8))
    ey = random.randint(int(h*0.05), int(h*0.4))
    rx = random.randint(int(w*0.15), int(w*0.4))
    ry = random.randint(int(h*0.05), int(h*0.2))
    draw.ellipse((ex-rx, ey-ry, ex+rx, ey+ry), fill=(255,255,240))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=12))
    return Image.blend(img.convert("RGB"), overlay, alpha=0.35)

def random_rotate_cv(img: Image.Image):
    a = random.uniform(-18, 18)
    arr = np.array(img)
    (h, w) = arr.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), a, 1.0)
    rotated = cv2.warpAffine(arr, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)

def add_noise(img: Image.Image) -> Image.Image:
    arr = np.array(img).astype(np.int16)
    noise = np.random.normal(0, 10, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def augment_one(p: Path, out_idx: int):
    img = Image.open(p).convert("RGB")
    ops = [random_rotate_cv, add_glare, add_noise]
    random.shuffle(ops)
    for i, op in enumerate(ops[: random.randint(1,3)]):
        img = op(img)
    # random resize
    if random.random() < 0.4:
        scale = random.uniform(0.8, 1.15)
        w,h = img.size
        img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
    out = OUT_DIR / f"aug_{out_idx:03d}_{p.name}"
    img.save(out)

def main():
    base = list(SAMPLES_DIR.glob("*.png")) + list(SAMPLES_DIR.glob("*.jpg"))
    if not base:
        print("No base samples found in static/samples. Run generate_samples.py first.")
        return
    idx = 0
    for p in base:
        # keep original copy
        dest = OUT_DIR / f"orig_{p.name}"
        if not dest.exists():
            Image.open(p).convert("RGB").save(dest)
        # produce multiple augmentations
        for i in range(8):
            augment_one(p, idx)
            idx += 1
    print(f"Wrote {idx} augmented images to {OUT_DIR}")

if __name__ == "__main__":
    main()
