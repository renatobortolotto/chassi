"""
Thin adapter over the context pdf_ocr module with lazy imports.
This avoids importing heavy deps (cv2, pytesseract, etc.) at module import time.
"""
from typing import List


def is_gcs_uri(s: str) -> bool:
    return isinstance(s, str) and s.startswith("gs://")


def _pdf_ocr():
    # Lazy import to avoid hard dependency unless functions are called
    from importlib import import_module
    return import_module("context.pdf_extractor.pdf_ocr")


def gcs_list_pdfs(dir_uri: str, recursive: bool = True) -> List[str]:
    mod = _pdf_ocr()
    return mod.gcs_list_pdfs(dir_uri, recursive=recursive)


def concat_many_pdfs_to_text(
    pdf_identifiers: List[str],
    dpi: int,
    lang: str,
    min_tokens: int,
    repeat_th: float,
    repeat_pages_frac: float,
) -> str:
    mod = _pdf_ocr()
    return mod.concat_many_pdfs_to_text(
        pdf_identifiers=pdf_identifiers,
        dpi=dpi,
        lang=lang,
        min_tokens=min_tokens,
        repeat_th=repeat_th,
        repeat_pages_frac=repeat_pages_frac,
    )


def gcs_write_text(dir_uri: str, filename: str, text: str) -> str:
    mod = _pdf_ocr()
    return mod.gcs_write_text(dir_uri, filename, text)
