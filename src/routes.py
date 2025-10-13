from src.controller.app import app
from src.application.extrator_dados_debenture import ResourceExtratorDadosDebenture

def create_routes(app_instance=None):
    """Creates Routes"""
    api = app if app_instance is None else app_instance
    api.create_route(ResourceExtratorDadosDebenture, "/extrator_dados_debenture")