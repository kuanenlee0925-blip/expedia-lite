"""Demo route checks mock the controller and never start database lifespan."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import create_app
from zip_lookup import ZipConfigurationError, ZipLookupError


class ZipRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())
        self.addCleanup(self.client.close)

    def test_success(self):
        location = {"postcode": "16802", "country_code": "us", "latitude": 40.8,
                    "longitude": -77.86, "locality": "University Park"}
        with patch("main.lookup_zip", return_value=location) as lookup:
            response = self.client.get("/api/demo/zip-location")
        lookup.assert_called_once_with("16802")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), location)

    def test_unresolved(self):
        with patch("main.lookup_zip", return_value=None) as lookup:
            response = self.client.get("/api/demo/zip-location")
        lookup.assert_called_once_with("16802")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "ZIP 16802 could not be resolved."})

    def test_entered_zip_preserves_leading_zero(self):
        location = {"postcode": "02108", "country_code": "us", "latitude": 42.36, "longitude": -71.06}
        with patch("main.lookup_zip", return_value=location) as lookup:
            response = self.client.get("/api/demo/zip-location?postcode=02108")
        lookup.assert_called_once_with("02108")
        self.assertEqual(response.json(), location)

    def test_invalid_zip_never_calls_provider(self):
        with patch("main.lookup_zip") as lookup:
            for postcode in ("", "1234", "123456", "ABCDE", "16802\n"):
                response = self.client.get("/api/demo/zip-location", params={"postcode": postcode})
                self.assertEqual(response.status_code, 422)
        lookup.assert_not_called()

    def test_failures_never_expose_exception_text(self):
        for error, status, detail in (
            (ZipConfigurationError, 503, "ZIP lookup is not configured."),
            (ZipLookupError, 502, "ZIP lookup provider request failed."),
        ):
            with self.subTest(status=status):
                with patch("main.lookup_zip", side_effect=error("https://provider/?apiKey=secret")) as lookup:
                    response = self.client.get("/api/demo/zip-location")
                lookup.assert_called_once_with("16802")
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json(), {"detail": detail})


if __name__ == "__main__":
    unittest.main()
