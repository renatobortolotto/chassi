import unittest


class TestPdfOcrMetrics(unittest.TestCase):
    def setUp(self):
        from src.infrastructure.services.pdf_ocr import (
            _printable_ratio,
            _alpha_num_ratio,
            _mean_word_len,
            _slash_seq_frac,
            _unique_chars,
            text_quality_metrics,
        )
        self._printable_ratio = _printable_ratio
        self._alpha_num_ratio = _alpha_num_ratio
        self._mean_word_len = _mean_word_len
        self._slash_seq_frac = _slash_seq_frac
        self._unique_chars = _unique_chars
        self.text_quality_metrics = text_quality_metrics

    def test_printable_ratio(self):
        self.assertEqual(self._printable_ratio(""), 0.0)
        # All allowed (letters with accents, digits, punctuation, space and newline)
        self.assertEqual(self._printable_ratio("Olá 123.\n"), 1.0)
        # Contains a non-printable char (bell) -> ratio < 1
        self.assertAlmostEqual(self._printable_ratio("A\x07B"), 2 / 3, places=6)

    def test_alpha_num_ratio(self):
        self.assertEqual(self._alpha_num_ratio(""), 0.0)
        self.assertAlmostEqual(self._alpha_num_ratio("abc123!!"), 6 / 8, places=6)

    def test_mean_word_len(self):
        self.assertEqual(self._mean_word_len([]), 0.0)
        self.assertEqual(self._mean_word_len(["aa", "bbb", "c"]), 2.0)

    def test_slash_seq_frac(self):
        self.assertEqual(self._slash_seq_frac(""), 0.0)
        self.assertEqual(self._slash_seq_frac("no matches here"), 0.0)
        s = " /12 something /9 and /123 end"
        self.assertGreater(self._slash_seq_frac(s), 0.0)
        self.assertLessEqual(self._slash_seq_frac(s), 1.0)

    def test_unique_chars(self):
        self.assertEqual(self._unique_chars(""), 0)
        self.assertEqual(self._unique_chars("abca"), 3)

    def test_text_quality_metrics(self):
        # Empty pages
        self.assertEqual(self.text_quality_metrics([]), (0, 0, 0, 0, 0))

        pages = [
            "Hello 123",
            "Página 1 / 2\nHello",
            "gibberish\x00",
        ]
        pr, ar, mwl, sfrac, uniq = self.text_quality_metrics(pages)
        # Basic sanity checks and boundaries
        self.assertGreaterEqual(pr, 0.0)
        self.assertLessEqual(pr, 1.0)
        self.assertGreaterEqual(ar, 0.0)
        self.assertLessEqual(ar, 1.0)
        self.assertGreaterEqual(mwl, 0.0)
        self.assertGreaterEqual(sfrac, 0.0)
        self.assertLessEqual(sfrac, 1.0)
        # Unique chars should equal the set size of concatenated pages
        expected_uniq = len(set("".join(pages)))
        self.assertEqual(uniq, expected_uniq)


if __name__ == "__main__":
    unittest.main()
