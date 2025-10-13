import unittest
from src.controller import app


class TestServer(unittest.TestCase):
    def test_import_server(self):
        self.assertTrue(app)

    def test_run_server(self):
        server = app.Atomic(__name__)
        server.create_app()
        self.assertTrue(__name__, "Initializing")


if __name__ == "__main__":
    unittest.main()