from io import BytesIO
from PIL import Image
import pytesseract
import re
import cv2
import numpy as np


def _preprocess_image_bytes(data: bytes) -> Image.Image:
    # Use OpenCV for more robust preprocessing before OCR
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        # fall back to PIL
        return Image.open(BytesIO(data))

    # convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # denoise while keeping edges
    gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    # adaptive threshold to increase contrast
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 10)

    # optional morphological opening to remove small artifacts
    kernel = np.ones((1, 1), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

    # deskew using moments
    coords = np.column_stack(np.where(th > 0))
    angle = 0.0
    try:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = th.shape
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        th = cv2.warpAffine(th, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    except Exception:
        pass

    # convert back to PIL Image
    pil_img = Image.fromarray(th)
    return pil_img


def extract_text_from_bytes(data: bytes) -> str:
    pil_img = _preprocess_image_bytes(data)
    # tune tesseract config for single column text and faster engine
    config = "--psm 6"
    text = pytesseract.image_to_string(pil_img, config=config)
    return text


def find_abv(text: str) -> str | None:
    m = re.search(r"(\d{1,3}(?:\.\d)?\s*%\s*(?:Alc\.|Alc|Alcohol)\/?Vol\.?|\d{1,3}%\s*Alc|\d{1,3}\s*Proof)", text, re.IGNORECASE)
    return m.group(0).strip() if m else None


def find_net_contents(text: str) -> str | None:
    m = re.search(r"(\d+\s*(?:mL|ML|L|liters|litre|ounces|fl oz|milli?liters))", text, re.IGNORECASE)
    return m.group(0).strip() if m else None


def find_government_warning(text: str) -> str | None:
    # look for the standard 'GOVERNMENT WARNING' heading or long warning text
    if "GOVERNMENT WARNING" in text.upper():
        idx = text.upper().find("GOVERNMENT WARNING")
        snippet = text[idx: idx + 800]
        return snippet.strip()
    # fallback: check for key phrases
    if "mother" in text.lower() and "pregnant" in text.lower():
        # likely the standard warning body
        m = re.search(r"(if you?re pregnant.*?warning\.|pregnant.*?warning\.)", text, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(0).strip()
    return None


def find_brand(text: str) -> str | None:
    # Heuristic: prefer uppercase lines in the top region or longest line with letters
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return None
    # prefer lines that look like a title (many uppercase letters)
    candidates = sorted(lines, key=lambda s: (-sum(1 for c in s if c.isupper()), -len(s)))
    top = candidates[0]
    if len(top) >= 3 and any(c.isalpha() for c in top):
        return top
    return lines[0] if lines else None


def analyze_image_bytes(data: bytes) -> dict:
    try:
        text = extract_text_from_bytes(data)
    except Exception as e:
        return {"error": f"OCR error: {e}"}

    # compute tesseract confidence if possible
    confidence = None
    try:
        # use image_to_data to extract numeric confidences
        from PIL import Image
        img = _preprocess_image_bytes(data)
        data_out = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        confs = [int(c) for c in data_out.get('conf', []) if c.strip().lstrip('-').isdigit()]
        if confs:
            confidence = sum(confs) / len(confs)
    except Exception:
        confidence = None

    brand = find_brand(text)
    abv = find_abv(text)
    net = find_net_contents(text)
    warning = find_government_warning(text)

    # simple manual-review heuristic
    needs_manual_review = False
    # low OCR confidence
    if confidence is not None and confidence < 40:
        needs_manual_review = True
    # missing critical fields
    if not (brand and (abv or warning or net)):
        needs_manual_review = True

    result = {
        "raw_text": text,
        "brand": brand,
        "abv": abv,
        "net_contents": net,
        "government_warning": warning,
        "confidence": confidence,
        "needs_manual_review": needs_manual_review,
    }
    return result
