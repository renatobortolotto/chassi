"""
Internal helpers to POST text to an external API and save JSON payloads (local or GCS).
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re

import requests

try:  # optional GCS
    from google.cloud import storage  # type: ignore
except Exception:  # pragma: no cover
    storage = None  # type: ignore


def is_gcs_uri(s: str) -> bool:
    return isinstance(s, str) and s.startswith("gs://")


def parse_gcs_uri(uri: str) -> Tuple[str, str]:
    assert uri.startswith("gs://")
    no_scheme = uri[5:]
    parts = no_scheme.split("/", 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ""
    return bucket, key


def gcs_client():  # pragma: no cover
    if storage is None:
        raise RuntimeError(
            "google-cloud-storage não instalado. pip install google-cloud-storage"
        )
    return storage.Client()


def gcs_write_json(gs_dir: str, filename: str, payload: Dict[str, Any]) -> str:  # pragma: no cover
    bucket, prefix = parse_gcs_uri(gs_dir)
    key = f"{prefix.rstrip('/')}/{filename}" if prefix else filename
    data = json.dumps(payload, ensure_ascii=False)
    client = gcs_client()
    blob = client.bucket(bucket).blob(key)
    blob.upload_from_string(data, content_type="application/json; charset=utf-8")
    return f"gs://{bucket}/{key}"


def post_with_retries(url: str, json_body: Dict[str, Any], headers: Dict[str, str], timeout: float, retries: int):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, json=json_body, headers=headers, timeout=timeout)
            return resp
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(min(2 ** attempt, 8))
    if last_exc:
        raise last_exc
    raise RuntimeError("Falha HTTP desconhecida")


def extract_json_from_text(s: str):
    if not isinstance(s, str):
        return None
    s = s.replace("\r\n", "\n")
    for pat in (r"```json\s*(\{.*?\})\s*```", r"```\s*(\{.*?\})\s*```"):
        m = re.search(pat, s, flags=re.DOTALL | re.IGNORECASE)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    m = re.search(r"\bjson\s*(\{.*\})\s*$", s, flags=re.DOTALL | re.IGNORECASE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return None


def sanitize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"```+json", "", s, flags=re.IGNORECASE)
    s = re.sub(r"```+", "", s)
    s = s.replace("**", "").replace("__", "")
    s = re.sub(r"`+", "", s)
    s = re.sub(r"(?m)^\s*([*\-–•]|\d+\.)\s+", "", s)
    s = re.sub(r"(?m)^\s*#{1,6}\s*", "", s)
    s = re.sub(r"\n{2,}", "\n", s).replace("\n", " ")
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()
