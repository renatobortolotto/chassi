import unittest
import tempfile
from pathlib import Path
from unittest import mock


class TestFindPdfsByPatterns(unittest.TestCase):
    def setUp(self):
        from src.infrastructure.services import pdf_ocr as ocr
        self.ocr = ocr

    # GCS branch: mocks is_gcs_uri True and gcs_list_pdfs results
    def test_gcs_branch_with_patterns_and_sort(self):
        with mock.patch.object(self.ocr, "is_gcs_uri", return_value=True), \
             mock.patch.object(self.ocr, "gcs_list_pdfs", return_value=[
                 "gs://bkt/prefix/Álbum-contrato.pdf",
                 "gs://bkt/prefix/EsCritura-2020.pdf",
                 "gs://bkt/prefix/Manual-xyz.pdf",
                 "gs://bkt/prefix/outro.pdf",
             ]):
            hits = self.ocr.find_pdfs_by_patterns(
                "gs://bkt/prefix", ["escritura", "contrato", "manual"], recursive=True
            )
            # All three that match should be included, sorted case/accent-insensitive by name
            self.assertEqual(
                hits,
                [
                    "gs://bkt/prefix/Álbum-contrato.pdf",
                    "gs://bkt/prefix/EsCritura-2020.pdf",
                    "gs://bkt/prefix/Manual-xyz.pdf",
                ],
            )

    # Local branch: directory not found -> FileNotFoundError
    def test_local_missing_directory_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.ocr.find_pdfs_by_patterns("/definitely/not/here", ["x"]) 

    # Local branch: recursive True finds nested, accent-insensitive matching
    def test_local_recursive_true(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "ESCRITURA-1.pdf").write_text("")
            (base / "contrato de distribuicao.pdf").write_text("")  # without cedilla
            (base / "manual.txt").write_text("")  # ignored (not pdf)
            nested = base / "nested"
            nested.mkdir()
            (nested / "contrato_de_distribuição2.pdf").write_text("")  # with cedilla

            hits = self.ocr.find_pdfs_by_patterns(
                str(base), ["escritura", "distribuição"], recursive=True
            )
            # Should include 3 pdfs from both levels, sorted by name
            self.assertEqual(len(hits), 3)
            self.assertEqual(
                [Path(h).name for h in hits],
                [
                    "contrato de distribuicao.pdf",
                    "contrato_de_distribuição2.pdf",
                    "ESCRITURA-1.pdf",
                ],
            )

    # Local branch: recursive False ignores nested
    def test_local_recursive_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "escritura-1.pdf").write_text("")
            nested = base / "nested"
            nested.mkdir()
            (nested / "escritura-2.pdf").write_text("")

            hits = self.ocr.find_pdfs_by_patterns(str(base), ["escritura"], recursive=False)
            self.assertEqual(hits, [str(base / "escritura-1.pdf")])


if __name__ == "__main__":
    unittest.main()
