from atomic import Resource, request

from src.controller.app import app  
from src.infrastructure.database.database_in_memory import extrator_dados_debenture
from src.application.pdf_processor.service import PdfProcessConfig, process_pdfs


class ResourceExtratorDadosDebenture(Resource):
    def get(self):
        return {"data": extrator_dados_debenture["extrator_dados_debenture"]}, 200
    
    def post(self):
        arguments = request.get_json(force=True) or {}
        # Se payload contiver campos do pipeline de PDFs, aciona o processamento
        if all(k in arguments for k in ("pdfs_dir", "payload_dir", "api_url")):
            cfg = PdfProcessConfig(
                pdfs_dir=arguments.get("pdfs_dir"),
                payload_dir=arguments.get("payload_dir"),
                api_url=arguments.get("api_url"),
                endpoint=arguments.get("endpoint", "/extrator_dados_debentures"),
                auth_header=arguments.get("auth_header"),
                dpi=int(arguments.get("dpi", 300)),
                lang=str(arguments.get("lang", "por+eng")),
                min_tokens=int(arguments.get("min_tokens", 120)),
                repeat_th=float(arguments.get("repeat_th", 0.30)),
                repeat_pages=float(arguments.get("repeat_pages", 0.6)),
                timeout=float(arguments.get("timeout", 60.0)),
                retries=int(arguments.get("retries", 3)),
            )
            body, status = process_pdfs(cfg)
            return body, status

        # Caso contrário, mantém o comportamento CRUD anterior (compatível com testes)
        extrator_dados_debenture["extrator_dados_debenture"].append(
            {
                "id": arguments.get("id"),
                "name": arguments.get("name"),
            }
        )
        return {"message": "Inserted Successfully"}, 201
    
    def delete(self):
        id = request.values.get("id")
        users = extrator_dados_debenture["extrator_dados_debenture"]
        if id:
            for index, user in enumerate(users):
                if user.get("id") == int(id):
                    users.pop(index)
                    return {"message": "Deleted Successfully"}, 200
            # id fornecido mas não encontrado
            return {"message": "ID not found"}, 400
        # id ausente
        return {"message": "Delete Error"}, 400
    
    def put(self):
        id = request.values.get("id")
        users = extrator_dados_debenture["extrator_dados_debenture"]
        arguments = request.get_json(force=True)
        if id:
            for index, user in enumerate(users):
                if user.get("id") == int(id):
                    users[index].update({"name": arguments.get("name")})
                    return {"message": "Updated Successfully"}, 200
            # id fornecido mas não encontrado
            return {"message": "ID not found"}, 400
        # id ausente
        return {"message": "Update Error"}, 400