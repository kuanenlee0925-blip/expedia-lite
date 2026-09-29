"""ZIP controller checks use synthetic credentials and mocked HTTP responses only."""
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import zip_lookup


class ZipLookupTests(unittest.TestCase):
    def setUp(self):
        key = patch.object(zip_lookup.config, "GEOAPIFY_API_KEY", "synthetic-test-key")
        key.start()
        self.addCleanup(key.stop)
        self.http = patch("zip_lookup.urlopen")
        self.request = self.http.start()
        self.addCleanup(self.http.stop)

    def respond(self, payload):
        response = io.BytesIO(json.dumps(payload).encode())
        response.status = 200
        self.request.return_value = response

    def match(self, **changes):
        return {"postcode": "16802", "country_code": "us", "lat": 40.8,
                "lon": -77.86, "city": "University Park", **changes}

    def test_success_and_request_contract(self):
        self.respond({"results": [self.match()]})
        self.assertEqual(zip_lookup.lookup_zip("16802"), {
            "postcode": "16802", "country_code": "us", "latitude": 40.8,
            "longitude": -77.86, "locality": "University Park"})
        args, kwargs = self.request.call_args
        url = urlsplit(args[0])
        self.assertEqual((url.scheme, url.netloc, url.path),
                         ("https", "api.geoapify.com", "/v1/geocode/search"))
        self.assertEqual(parse_qs(url.query), {
            "postcode": ["16802"], "type": ["postcode"], "filter": ["countrycode:us"],
            "format": ["json"], "apiKey": ["synthetic-test-key"]})
        self.assertEqual(kwargs, {"timeout": 10})

    def test_unresolved_mismatch_and_invalid_coordinates(self):
        for results in ([], [self.match(postcode="16801")], [self.match(country_code="ca")],
                        [self.match(lat=None)], [self.match(lat=True)], [self.match(lat="40.8")],
                        [self.match(lat=float("nan"))], [self.match(lon=float("inf"))],
                        [self.match(lat=91)], [self.match(lon=-181)]):
            with self.subTest(results=results):
                self.respond({"results": results})
                self.assertIsNone(zip_lookup.lookup_zip("16802"))

    def test_skips_mismatch_and_locality_is_optional(self):
        self.respond({"results": [self.match(postcode="16801"), self.match(city=None)]})
        location = zip_lookup.lookup_zip("16802")
        self.assertEqual(location["postcode"], "16802")
        self.assertNotIn("locality", location)

    def test_provider_failures_are_sanitized(self):
        secret_url = "https://api.geoapify.com/?apiKey=synthetic-test-key"
        for error in (URLError(secret_url), TimeoutError(secret_url),
                      HTTPError(secret_url, 500, secret_url, {}, None)):
            with self.subTest(error=type(error).__name__):
                self.request.side_effect = error
                with self.assertRaises(zip_lookup.ZipLookupError) as caught:
                    zip_lookup.lookup_zip("16802")
                self.assertEqual(str(caught.exception), "ZIP lookup provider request failed.")
                self.assertTrue(caught.exception.__suppress_context__)

    def test_malformed_provider_response(self):
        for payload in ({}, {"results": None}, {"results": [None]}, []):
            self.respond(payload)
            with self.assertRaises(zip_lookup.ZipLookupError):
                zip_lookup.lookup_zip("16802")
        response = io.BytesIO(b"not JSON")
        response.status = 200
        self.request.return_value = response
        with self.assertRaisesRegex(zip_lookup.ZipLookupError, "provider request failed"):
            zip_lookup.lookup_zip("16802")

    def test_invalid_input_and_missing_configuration_do_not_request(self):
        for postcode in (16802, "", "16802-1234", " 16802", "ABCDE"):
            with self.assertRaises(ValueError):
                zip_lookup.lookup_zip(postcode)
        with patch.object(zip_lookup.config, "GEOAPIFY_API_KEY", ""):
            with self.assertRaisesRegex(zip_lookup.ZipLookupError, "not configured"):
                zip_lookup.lookup_zip("16802")
        self.request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
