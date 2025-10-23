from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.infrastructure.services import pdf_ocr as ocr

# API externa removida neste fluxo

# Padrões default (mesma lógica do script CLI)
PATTERN_DEFAULTS: List[str] = [
    "escritura",
    "contrato de distribuição",
    "manual",
]


@dataclass
class PdfProcessConfig:
    pdfs_dir: str
    # Parâmetros opcionais do pipeline de OCR/extração
    auth_header: Optional[str] = None  # mantido para compatibilidade, não utilizado
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
    # Não há mais necessidade de 'payload_dir' nem de API externa

    if cfg.file_names:
        # Quando nomes exatos são fornecidos, respeitamos isso acima de padrões
        pdfs = ocr.gcs_list_pdfs(cfg.pdfs_dir, recursive=True, file_names=cfg.file_names)
    else:
        # Se patterns for omitido, usamos os padrões default
        use_patterns = cfg.patterns if cfg.patterns is not None else PATTERN_DEFAULTS
        pdfs = ocr.find_pdfs_by_patterns(cfg.pdfs_dir, use_patterns, recursive=True)
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

    result = {
        "message": "Processamento concluído",
        "pdfs_count": len(pdfs),
        "txt_uri": txt_uri,
    }

    return result, 200
