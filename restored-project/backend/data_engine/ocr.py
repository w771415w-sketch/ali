# -*- coding: utf-8 -*-
"""Optional real OCR adapter. It never silently invents OCR text."""
from __future__ import annotations
from pathlib import Path
import shutil


def available() -> bool:
    try:
        import pytesseract  # noqa: F401
        return bool(shutil.which("tesseract"))
    except Exception:
        return False


def image_to_text(path: str | Path, lang: str = "ara+eng") -> str:
    try:
        import pytesseract
        from PIL import Image
    except Exception as e:
        raise RuntimeError("OCR requires Pillow + pytesseract") from e
    if not shutil.which("tesseract"):
        raise RuntimeError("Tesseract executable is not installed or not on PATH")
    return pytesseract.image_to_string(Image.open(path), lang=lang)
