import unittest

from src.routes import create_routes

class TestServer(unittest.TestCase):
    def test_import(self):
        self.assertTrue(create_routes)

    def test_create_routes(self):
        create_routes()
        self.assertLogs(__name__, "Initializing routes=extrator_dados_debenture")

if __name__ == "__main__":
    unittest.main()