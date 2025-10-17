import unittest
import tempfile
from pathlib import Path
from io import BytesIO
import sys

class TestPdfOcrCore(unittest.TestCase):
    def setUp(self):
        from src.infrastructure.services.pdf_ocr import (
            load_pdf_bytes,
            extract_native_per_page_from_bytes,
            tokenize,
            avg_tokens_per_page,
            normalize_line,
            is_gcs_uri,
        )
        self.load_pdf_bytes = load_pdf_bytes
        self.extract_native_per_page_from_bytes = extract_native_per_page_from_bytes
        self.tokenize = tokenize
        self.avg_tokens_per_page = avg_tokens_per_page
        self.normalize_line = normalize_line
        self.is_gcs_uri = is_gcs_uri

    def test_load_pdf_bytes_local(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"hello world")
            tmp_path = tmp.name
        try:
            data = self.load_pdf_bytes(tmp_path)
            self.assertEqual(data, b"hello world")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_load_pdf_bytes_gcs(self):
        # Patch gcs_read_bytes and is_gcs_uri
        import src.infrastructure.services.pdf_ocr as pdf_ocr
        pdf_ocr.gcs_read_bytes = lambda x: b"gcs-bytes"
        self.assertEqual(self.load_pdf_bytes("gs://bucket/key"), b"gcs-bytes")

    def test_extract_native_per_page_from_bytes(self):
        # Create a minimal PDF with PyPDF2
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with BytesIO() as bio:
            writer.write(bio)
            pdf_bytes = bio.getvalue()
        # Should return one page with empty string
        pages = self.extract_native_per_page_from_bytes(pdf_bytes)
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0], "")

    def test_tokenize(self):
        self.assertEqual(self.tokenize("abc 123"), ["abc", "123"])
        self.assertEqual(self.tokenize("Olá, mundo!"), ["Olá", "mundo"])
        self.assertEqual(self.tokenize("\t\n"), [])

    def test_avg_tokens_per_page(self):
        self.assertEqual(self.avg_tokens_per_page(["a b", "c d e"]), 2.5)
        self.assertEqual(self.avg_tokens_per_page([""]), 0.0)
        self.assertEqual(self.avg_tokens_per_page([]), 0.0)

    def test_normalize_line(self):
        # Remove excess whitespace
        self.assertEqual(self.normalize_line("  abc   def  "), "abc def")
        # Remove long alphanumeric sequences (may leave a double space)
        self.assertEqual(self.normalize_line("abc 1234567890123456 def"), "abc  def")
        # Remove page markers
        # Abbreviated with accent 'Pág.' is not removed by current regex and should remain unchanged
        self.assertEqual(self.normalize_line("Pág. 2 / 10"), "Pág. 2 / 10")
        self.assertEqual(self.normalize_line("Página 3 / 10"), "")
        self.assertEqual(self.normalize_line("Pag. 1 / 2"), "")

    def test_repetition_coverage_basic_and_edge_cases(self):
        from src.infrastructure.services.pdf_ocr import repetition_coverage

        # Case 1: no lines -> returns 0.0
        self.assertEqual(repetition_coverage(["", "  ", "\n\n"], min_line_len=6), 0.0)

        # Build pages with repeated header/footer and unique content
        header = "Company XYZ"          # len 11
        footer = "Page footer 2025"     # len 16
        pages = [
            f"{header}\ncontent A\n{footer}",
            f"{header}\ncontent B\n{footer}",
            f"{header}\ncontent C",
            f"{header}\ncontent D\n{footer}",
            "content E",
        ]

        # Precomputed total_chars = 137 (see reasoning), n_pages = 5
        # With repeat_pages_frac=0.6 -> min_pages=int(3.0)=3, repeated lines: header(4), footer(3)
        cov = repetition_coverage(pages, min_line_len=6, top_k=10, repeat_pages_frac=0.6)
        self.assertAlmostEqual(cov, 135/137, places=6)

        # top_k=1 -> only the most repeated (header, len=11) considered
        cov_top1 = repetition_coverage(pages, min_line_len=6, top_k=1, repeat_pages_frac=0.6)
        self.assertAlmostEqual(cov_top1, 55/137, places=6)

        # repeat_pages_frac so high that none qualifies -> 0.0
        cov_none = repetition_coverage(pages, min_line_len=6, top_k=10, repeat_pages_frac=1.0)
        self.assertEqual(cov_none, 0.0)

    def test_should_force_ocr_cases(self):
        from src.infrastructure.services.pdf_ocr import should_force_ocr

        # Case A: avg_tokens below threshold triggers force
        pages_low_tokens = ["word", "two", "three"]  # avg tokens ~1 per page
        force, avg_tok, rep_cov = should_force_ocr(
            pages_low_tokens,
            min_tokens=5,
            repeat_threshold=0.9,
            repeat_pages_frac=0.8,
        )
        self.assertTrue(force)
        self.assertLess(avg_tok, 5)
        self.assertGreaterEqual(rep_cov, 0.0)

        # Case B: repetition coverage triggers force
        header = "Linha Repetida Muito Longa"
        pages_rep = [
            f"{header}\nconteudo A",
            f"{header}\nconteudo B",
            f"{header}\nconteudo C",
            "conteudo diverso sem repeticao",
        ]
        force2, avg_tok2, rep_cov2 = should_force_ocr(
            pages_rep,
            min_tokens=1,              # easy pass on tokens
            repeat_threshold=0.10,      # low threshold so repetition wins
            repeat_pages_frac=0.5,      # header appears em 3/4 páginas
        )
        self.assertTrue(force2)
        self.assertGreaterEqual(rep_cov2, 0.10)

        # Case C: gibberish (low uniqueness) triggers force
        pages_gib = ["aaa\nbbb", "ccc"]  # uniq chars muito baixo
        force3, avg_tok3, rep_cov3 = should_force_ocr(
            pages_gib,
            min_tokens=1,
            repeat_threshold=1.0,
            repeat_pages_frac=0.9,
        )
        self.assertTrue(force3)

        # Case D: all good -> no force
        pages_ok = [
            "Este documento possui conteudo significativo e variado sem repeticoes.",
            "Cada pagina contem texto legivel, com palavras longas suficientes.",
            "Diversidade adequada de caracteres e sem marcadores de pagina.",
        ]
        force4, avg_tok4, rep_cov4 = should_force_ocr(
            pages_ok,
            min_tokens=3,          # média de tokens por página é bem maior
            repeat_threshold=0.5,   # rep_cov esperado baixo
            repeat_pages_frac=0.8,
        )
        self.assertFalse(force4)
        self.assertGreater(avg_tok4, 3)
        self.assertLess(rep_cov4, 0.5)


if __name__ == "__main__":
    unittest.main()