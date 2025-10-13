"""
Thin adapter over the context txt_to_api helpers, with lazy import and safe fallbacks.
"""
from typing import Any, Dict, Optional


def _tta():
    from importlib import import_module
    return import_module("context.pdf_extractor.txt_to_api")


def post_with_retries(url: str, json_body: Dict[str, Any], headers: Dict[str, str], timeout: float, retries: int):
    mod = _tta()
    return mod.post_with_retries(url, json_body, headers, timeout=timeout, retries=retries)


def gcs_write_json(gs_dir: str, filename: str, payload: Dict[str, Any]) -> str:
    mod = _tta()
    return mod.gcs_write_json(gs_dir, filename, payload)


def extract_json_from_text(s: str):
    mod = _tta()
    if hasattr(mod, "extract_json_from_text"):
        return mod.extract_json_from_text(s)
    return None


def sanitize_text(s: str) -> str:
    mod = _tta()
    if hasattr(mod, "sanitize_text"):
        return mod.sanitize_text(s)
    return str(s or "")
