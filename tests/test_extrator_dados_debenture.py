import unittest
from unittest import mock

from flask import Flask


class TestServer(unittest.TestCase):
    server = Flask("test_flask_app")
    def setUp(self):
        from  src.application.extrator_dados_debenture import ResourceExtratorDadosDebenture
        self.resource_extrator_dados_debenture = ResourceExtratorDadosDebenture

    def test_get(self):
        with self.server.test_request_context():
            resource = self.resource_extrator_dados_debenture()
            self.assertEqual(resource.get(), ({"data": [{'id': 1, 'name': 'example'}]}, 200))
    
    def test_post(self):
        with self.server.test_request_context(json={"id": 2, "name": "example2"}) as context:
            resource = self.resource_extrator_dados_debenture()
            self.assertEqual(resource.post(), ({"message": "Inserted Successfully"}, 201))

    @mock.patch("src.application.extrator_dados_debenture.process_pdfs")
    def test_post_process_pdfs(self, m_process):
        m_process.return_value = ({"message": "Processamento concluído"}, 200)
        payload = {
            "pdfs_dir": "gs://bucket/in",
            "payload_dir": "gs://bucket/out",
        }
        with self.server.test_request_context(json=payload) as context:
            resource = self.resource_extrator_dados_debenture()
            body, status = resource.post()
            self.assertEqual(status, 200)
            self.assertIn("Processamento concluído", body.get("message", ""))
    
    def test_put(self):
        with self.server.test_request_context(method="PUT", json={"name": "example2_updated"}) as context:
            context.request.values = {"id": 2}
            resource = self.resource_extrator_dados_debenture()
            self.assertEqual(resource.put(), ({"message": "Updated Successfully"}, 200))
    
    def test_put_error(self):
        with self.server.test_request_context(method="PUT", json={"name": "example2_updated"}) as context:
            context.request.values = {"id": None}
            resource = self.resource_extrator_dados_debenture()
            self.assertEqual(resource.put(), ({"message": "Update Error"}, 400))
    
    def test_put_error_not_found_error(self):
        with self.server.test_request_context(method="PUT", json={"name": "example2_updated"}) as context:
            context.request.values = {"id": 999}
            resource = self.resource_extrator_dados_debenture()
            self.assertEqual(resource.put(), ({"message": "ID not found"}, 400))
    
    def test_delete(self):
        with self.server.test_request_context(method="POST", json={"id": 2, "name": "example2"}) as context:
            context.request.values = {"id": 2}
            resource = self.resource_extrator_dados_debenture()
            resource.post()

        with self.server.test_request_context(method="DELETE") as context:
            context.request.values = {"id": 2}
            resource = self.resource_extrator_dados_debenture()
            self.assertEqual(resource.delete(), ({"message": "Deleted Successfully"}, 200))

    def test_delete_error(self):
        with self.server.test_request_context(method="DELETE") as context:
            context.request.values = {"id": None}
            resource = self.resource_extrator_dados_debenture()
            self.assertEqual(resource.delete(), ({"message": "Delete Error"}, 400))

    def test_delete_error_not_found(self):
        with self.server.test_request_context(method="DELETE") as context:
            context.request.values = {"id": 999}
            resource = self.resource_extrator_dados_debenture()
            self.assertEqual(resource.delete(), ({"message": "ID not found"}, 400))

if __name__ == "__main__":
    unittest.main()