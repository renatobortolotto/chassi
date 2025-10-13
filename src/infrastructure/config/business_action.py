from audit import BvBusinessActionInterface

class BusinessActionDefinitionCustom(BvBusinessActionInterface):
    def get_business_action(self, service):
        if "/extrator_dados_debenture" in service and "GET" in service:
            return "extrator_dados_debenture_GET_ACTION"
        elif "/extrator_dados_debenture" in service and "POST" in service:
            return "extrator_dados_debenture_POST_ACTION"
        elif "/extrator_dados_debenture" in service and "DEL" in service:
            return "extrator_dados_debenture_DEL_ACTION"
        elif "/extrator_dados_debenture" in service and "PUT" in service:
            return "extrator_dados_debenture_PUT_ACTION"
        return "UNDEFINED"
    
    