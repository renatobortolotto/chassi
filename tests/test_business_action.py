import unittest
from unittest import mock

from src.infrastructure.config.business_action import BusinessActionDefinitionCustom

class TestBusinessAction(unittest.TestCase):
    @mock.patch("src.infrastructure.config.business_action.BvBusinessActionInterface")

    def test_busines_action(self, business_interface):
        self.business_action_custom = BusinessActionDefinitionCustom()

        self.assertEqual(
            self.business_action_custom.get_business_action(
                "teste"
            ),
            "UNDEFINED",
        )
        self.assertEqual(
            self.business_action_custom.get_business_action(
                "GET /extrator_dados_debenture"
            ),
            "extrator_dados_debenture_GET_ACTION",
        )
        self.assertEqual(
            self.business_action_custom.get_business_action(
                "POST /extrator_dados_debenture"
            ),
            "extrator_dados_debenture_POST_ACTION",
        )
        self.assertEqual(
            self.business_action_custom.get_business_action(
                "DEL /extrator_dados_debenture"
            ),
            "extrator_dados_debenture_DEL_ACTION",
        )
        self.assertEqual(
            self.business_action_custom.get_business_action(
                "PUT /extrator_dados_debenture"
            ),
            "extrator_dados_debenture_PUT_ACTION",
        )            