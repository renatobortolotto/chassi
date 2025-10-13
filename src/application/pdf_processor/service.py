from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.infrastructure.services import pdf_ocr as ocr
from src.infrastructure.services import txt_to_api as tta
import os

# API externa fixa (LLM)
# Ajuste estes valores conforme o seu ambiente corporativo.
LLM_API_BASE = os.environ.get("LLM_API_BASE", "http://llm-api:8000/api")
LLM_API_ENDPOINT = os.environ.get("LLM_API_ENDPOINT", "/extrator_dados_debentures")


@dataclass
class PdfProcessConfig:
    pdfs_dir: str
    payload_dir: str
    # API externa é fixa; não é necessário no payload
    auth_header: Optional[str] = None
    file_names: Optional[List[str]] = None
    patterns: Optional[List[str]] = None
    dpi: int = 300
    lang: str = "por+eng"
    min_tokens: int = 120
    repeat_th: float = 0.30
    repeat_pages: float = 0.6
    timeout: float = 60.0
    retries: int = 3


def process_pdfs(cfg: PdfProcessConfig) -> Tuple[Dict[str, Any], int]:
    # 1) Lista PDFs
    if not (isinstance(cfg.pdfs_dir, str) and cfg.pdfs_dir.startswith("gs://")):
        return {"error": "'pdfs_dir' deve ser uma URI gs://bucket/prefix"}, 400
    if not (isinstance(cfg.payload_dir, str) and cfg.payload_dir.startswith("gs://")):
        return {"error": "'payload_dir' deve ser uma URI gs://bucket/prefix"}, 400
    # API é fixa neste serviço; não é necessário validar no payload

    if cfg.patterns:
        pdfs = ocr.find_pdfs_by_patterns(cfg.pdfs_dir, cfg.patterns, recursive=True)
    else:
        pdfs = ocr.gcs_list_pdfs(cfg.pdfs_dir, recursive=True, file_names=cfg.file_names)
    if not pdfs:
        return {"message": "Nenhum PDF encontrado no prefixo informado."}, 404

    # 2) Extrai e concatena texto
    text = ocr.concat_many_pdfs_to_text(
        pdf_identifiers=pdfs,
        dpi=cfg.dpi,
        lang=cfg.lang,
        min_tokens=cfg.min_tokens,
        repeat_th=cfg.repeat_th,
        repeat_pages_frac=cfg.repeat_pages,
    )

    # 3) Grava TXT
    from datetime import datetime
    import time
    start = time.perf_counter()
    date_str = datetime.now().strftime("%Y%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    elapsed = time.perf_counter() - start
    elapsed_str = f"{elapsed:.2f}s"
    txt_name = f"concat-text-{date_str}-{time_str}-{elapsed_str}.txt"
    txt_uri = ocr.gcs_write_text(cfg.pdfs_dir, txt_name, text)

    # 4) POST para API externa
    base = LLM_API_BASE.rstrip("/")
    ep = LLM_API_ENDPOINT if str(LLM_API_ENDPOINT).startswith("/") else f"/{LLM_API_ENDPOINT}"
    url = f"{base}{ep}"
    headers = {"Content-Type": "application/json"}
    if cfg.auth_header:
        headers["Authorization"] = cfg.auth_header
    body = {"prompt": text}

    resp = tta.post_with_retries(url, body, headers, timeout=cfg.timeout, retries=cfg.retries)

    try:
        payload: Any = resp.json()
    except Exception:
        payload = {"status_code": getattr(resp, "status_code", None), "text": getattr(resp, "text", "")}

    if isinstance(payload, dict) and "text" in payload:
        raw = payload["text"]
        parsed = tta.extract_json_from_text(raw)
        if parsed is not None:
            payload["data"] = parsed
            payload["text_clean"] = parsed
        else:
            payload["text_clean"] = tta.sanitize_text(raw)
    elif not isinstance(payload, dict):
        payload = {"status_code": getattr(resp, "status_code", None), "text": str(payload)}

    to_save = payload.get("data") if isinstance(payload, dict) else payload
    if to_save is None:
        to_save = payload

    base_name = txt_name.rsplit(".", 1)[0]
    payload_name = f"payload-{base_name}-{date_str}{time_str}.json"
    payload_uri = tta.gcs_write_json(cfg.payload_dir, payload_name, to_save)

    return {
        "message": "Processamento concluído",
        "pdfs_count": len(pdfs),
        "txt_uri": txt_uri,
        "payload_uri": payload_uri,
        "api_url": url,
    }, 200
