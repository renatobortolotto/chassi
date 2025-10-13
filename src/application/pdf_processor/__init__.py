from atomic import Resource, request

from .service import PdfProcessConfig, process_pdfs


class ResourcePdfProcessor(Resource):
    def post(self):
        data = request.get_json(force=True) or {}
        cfg = PdfProcessConfig(
            pdfs_dir=data.get("pdfs_dir"),
            payload_dir=data.get("payload_dir"),
            auth_header=data.get("auth_header"),
            file_names=data.get("file_names"),
            patterns=data.get("patterns"),
            dpi=int(data.get("dpi", 300)),
            lang=str(data.get("lang", "por+eng")),
            min_tokens=int(data.get("min_tokens", 120)),
            repeat_th=float(data.get("repeat_th", 0.30)),
            repeat_pages=float(data.get("repeat_pages", 0.6)),
            timeout=float(data.get("timeout", 60.0)),
            retries=int(data.get("retries", 3)),
        )
        body, status = process_pdfs(cfg)
        return body, status
