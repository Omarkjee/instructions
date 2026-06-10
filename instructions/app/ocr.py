from io import BytesIO
from PIL import Image, ImageFilter, ImageOps
import pytesseract
import re


def _preprocess_image(img: Image.Image) -> Image.Image:
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img


def extract_text_from_bytes(data: bytes) -> str:
    img = Image.open(BytesIO(data))
    img = _preprocess_image(img)
    text = pytesseract.image_to_string(img)
    return text


def find_abv(text: str) -> str | None:
    m = re.search(r"(\d{1,2}(?:\.\d)?\s*%\s*(?:Alc\.|Alc|Alcohol)\/Vol\.|\d{1,2}%\s*Alc)", text, re.IGNORECASE)
    return m.group(0).strip() if m else None


def find_net_contents(text: str) -> str | None:
    m = re.search(r"(\d+\s*(?:mL|ML|L|liters|ounces|fl oz))", text, re.IGNORECASE)
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
    # naive: first line with uppercase words of length>2
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:6]:
        if sum(1 for w in line.split() if len(w) > 2) >= 1:
            return line
    return None


def analyze_image_bytes(data: bytes) -> dict:
    try:
        text = extract_text_from_bytes(data)
    except Exception as e:
        return {"error": f"OCR error: {e}"}

    result = {
        "raw_text": text,
        "brand": find_brand(text),
        "abv": find_abv(text),
        "net_contents": find_net_contents(text),
        "government_warning": find_government_warning(text),
    }
    return result
