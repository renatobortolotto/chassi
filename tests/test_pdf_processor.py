import unittest
from unittest import mock
from flask import Flask


class TestPdfProcessorResource(unittest.TestCase):
    server = Flask("test_flask_app")

    def setUp(self):
        from src.application.pdf_processor import ResourcePdfProcessor
        self.ResourcePdfProcessor = ResourcePdfProcessor

    @mock.patch("src.application.pdf_processor.service.ocr.gcs_write_text", return_value="gs://bucket/in/concat-abc.txt")
    @mock.patch("src.application.pdf_processor.service.ocr.concat_many_pdfs_to_text", return_value="lorem ipsum")
    @mock.patch("src.application.pdf_processor.service.ocr.gcs_list_pdfs", return_value=["gs://bucket/in/escritura.pdf"])    
    def test_post_happy_path(self, m_list, m_concat, m_write_txt):
        with self.server.test_request_context(json={
            "pdfs_dir": "gs://bucket/in",
        }):
            res = self.ResourcePdfProcessor()
            body, status = res.post()
            self.assertEqual(status, 200)
            self.assertIn("txt_uri", body)
            self.assertNotIn("payload_uri", body)

    def test_post_validation_errors(self):
        from src.application.pdf_processor import ResourcePdfProcessor

        with self.server.test_request_context(json={
            "pdfs_dir": "not-gs",
        }):
            res = ResourcePdfProcessor()
            body, status = res.post()
            self.assertEqual(status, 400)