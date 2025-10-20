import unittest
from unittest import mock
import numpy as np
from PIL import Image


class TestPdfOcrPreprocess(unittest.TestCase):
    def setUp(self):
        import src.infrastructure.services.pdf_ocr as pdf_ocr
        self.mod = pdf_ocr

    def test_choose_psm(self):
        self.assertEqual(self.mod._choose_psm(0), 3)
        self.assertEqual(self.mod._choose_psm(119.9), 3)
        self.assertEqual(self.mod._choose_psm(200), 4)
        self.assertEqual(self.mod._choose_psm(299.9), 4)
        self.assertEqual(self.mod._choose_psm(300), 6)

    def test_deskew_no_lines_returns_original(self):
        gray = np.zeros((32, 32), dtype=np.uint8)
        with mock.patch.object(self.mod.cv2, 'HoughLines', return_value=None):
            out = self.mod._deskew(gray)
        self.assertTrue(np.array_equal(gray, out))

    def test_deskew_with_angles_rotates(self):
        gray = np.zeros((32, 32), dtype=np.uint8)
        # Make image non-uniform so rotation produces change
        gray[2:6, 2:6] = 255
        # Force HoughLines to return one line with theta slightly off 90 deg
        lines = np.array([[[0.0, np.deg2rad(92.0)]]], dtype=np.float32)
        with mock.patch.object(self.mod.cv2, 'HoughLines', return_value=lines):
            out = self.mod._deskew(gray)
        self.assertEqual(out.shape, gray.shape)
        # Result should be different due to rotation
        self.assertGreater(int(np.sum(np.abs(out.astype(int) - gray.astype(int)))), 0)

    def test_preprocess_basic(self):
        pil = Image.new('L', (64, 64), color=200)
        out = self.mod._preprocess(pil)
        self.assertIsInstance(out, np.ndarray)
        self.assertEqual(out.shape, (64, 64))
        self.assertEqual(out.dtype, np.uint8)

    @mock.patch('src.infrastructure.services.pdf_ocr.pytesseract.image_to_string')
    @mock.patch('src.infrastructure.services.pdf_ocr.cv2.connectedComponents')
    @mock.patch('src.infrastructure.services.pdf_ocr.convert_from_bytes')
    def test_ocr_all_pages_from_bytes(self, m_convert, m_conn, m_ocr):
        # Mock two PIL images returned from pdf2image
        m_convert.return_value = [Image.new('L', (32, 32), color=220), Image.new('L', (32, 32), color=180)]
        # connectedComponents returns (num_labels, labels), we only use num_labels
        m_conn.side_effect = [(150, None), (320, None)]  # densities mapping to psm 4 then 6
        m_ocr.side_effect = ["foo", "bar"]

        out = self.mod.ocr_all_pages_from_bytes(b"%PDF-1.4 fake")
        self.assertIn("---- página 1 ----\nfoo", out)
        self.assertIn("---- página 2 ----\nbar", out)

    @mock.patch('src.infrastructure.services.pdf_ocr.pytesseract.image_to_string')
    @mock.patch('src.infrastructure.services.pdf_ocr.convert_from_bytes')
    @mock.patch('src.infrastructure.services.pdf_ocr.extract_native_per_page_from_bytes')
    @mock.patch('src.infrastructure.services.pdf_ocr.load_pdf_bytes')
    @mock.patch('src.infrastructure.services.pdf_ocr.should_force_ocr')
    def test_extract_text_forced_ocr(self, m_force, m_load, m_native, m_convert, m_ocr):
        m_force.return_value = (True, 1.0, 0.0)
        m_load.return_value = b"%PDF-1.4 fake"
        m_convert.return_value = [Image.new('L', (16, 16), color=200)]
        m_ocr.return_value = "ok"
        m_native.return_value = [""]

        out = self.mod.extract_text("gs://bucket/file.pdf", dpi=200, lang="por", min_tokens=10, repeat_th=0.5, repeat_pages_frac=0.6)
        self.assertIn("---- página 1 ----\nok", out)

    @mock.patch('src.infrastructure.services.pdf_ocr.extract_native_per_page_from_bytes')
    @mock.patch('src.infrastructure.services.pdf_ocr.load_pdf_bytes')
    @mock.patch('src.infrastructure.services.pdf_ocr.should_force_ocr')
    def test_extract_text_native_ok(self, m_force, m_load, m_native):
        m_force.return_value = (False, 50.0, 0.05)
        m_load.return_value = b"%PDF-1.4 fake"
        m_native.return_value = ["alpha", "", "beta"]

        out = self.mod.extract_text("/local/file.pdf", dpi=300, lang="por+eng", min_tokens=10, repeat_th=0.5, repeat_pages_frac=0.6)
        # Should include only non-empty pages with headers
        self.assertIn("---- página 1 ----\nalpha", out)
        self.assertIn("---- página 3 ----\nbeta", out)
        self.assertNotIn("página 2", out)

    @mock.patch('src.infrastructure.services.pdf_ocr.extract_text', return_value='content text')
    def test_concat_many_pdfs_to_text(self, m_ex):
        files = ["gs://bucket/a.pdf", "/tmp/b.pdf"]
        out = self.mod.concat_many_pdfs_to_text(files, dpi=200, lang='por', min_tokens=10, repeat_th=0.5, repeat_pages_frac=0.6)
        # Should contain headers for each file and the content once per file
        self.assertIn("---- a.pdf ----\ncontent text", out)
        self.assertIn("---- b.pdf ----\ncontent text", out)


if __name__ == '__main__':
    unittest.main()
