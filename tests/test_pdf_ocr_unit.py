import unittest


class TestParseGcsUri(unittest.TestCase):
    def setUp(self):
        from src.infrastructure.services.pdf_ocr import parse_gcs_uri, is_gcs_uri
        self.parse_gcs_uri = parse_gcs_uri
        self.is_gcs_uri = is_gcs_uri

    def test_is_gcs_uri(self):
        self.assertTrue(self.is_gcs_uri("gs://bucket"))
        self.assertTrue(self.is_gcs_uri("gs://bucket/prefix"))
        self.assertFalse(self.is_gcs_uri("http://bucket/prefix"))
        self.assertFalse(self.is_gcs_uri("/local/path"))

    def test_parse_bucket_only(self):
        bucket, prefix = self.parse_gcs_uri("gs://my-bucket")
        self.assertEqual(bucket, "my-bucket")
        self.assertEqual(prefix, "")

    def test_parse_bucket_with_trailing_slash(self):
        bucket, prefix = self.parse_gcs_uri("gs://my-bucket/")
        self.assertEqual(bucket, "my-bucket")
        self.assertEqual(prefix, "")

    def test_parse_bucket_with_prefix(self):
        bucket, prefix = self.parse_gcs_uri("gs://my-bucket/some/prefix")
        self.assertEqual(bucket, "my-bucket")
        self.assertEqual(prefix, "some/prefix")

    def test_parse_bucket_with_prefix_trailing_slash(self):
        bucket, prefix = self.parse_gcs_uri("gs://my-bucket/some/prefix/")
        self.assertEqual(bucket, "my-bucket")
        self.assertEqual(prefix, "some/prefix")

    def test_parse_invalid_scheme_raises(self):
        with self.assertRaises(AssertionError):
            self.parse_gcs_uri("http://my-bucket/prefix")


if __name__ == "__main__":
    unittest.main()
