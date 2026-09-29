import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from fastapi.testclient import TestClient
import places
from main import create_app
from database import connect
from zip_lookup import ZipLookupError, ZipRateLimitError

FIXTURE = json.loads((Path(__file__).parent / 'data/places-fixture.json').read_text())
CENTER = {'postcode': '16802', 'country_code': 'us', 'latitude': 40.803167822, 'longitude': -77.861384958}


class PlacesTests(unittest.TestCase):
    def search(self, payload=FIXTURE):
        with patch('places.lookup_zip', return_value=CENTER), patch('places.urlopen', return_value=io.BytesIO(json.dumps(payload).encode())) as request:
            result = places.search_hotels('16802')
            query = parse_qs(urlsplit(request.call_args.args[0]).query)
            self.assertEqual(query['categories'], ['accommodation.hotel'])
            self.assertEqual(query['filter'], ['circle:-77.861384958,40.803167822,5000'])
            self.assertEqual(request.call_args.kwargs['timeout'], 10)
            return result

    def test_matching_radius_and_missing_fields(self):
        result = self.search()
        self.assertEqual(len(result['hotels']), 2)
        self.assertIsNone(result['hotels'][1]['name'])
        self.assertEqual(result['omitted'], 1)

    def test_empty_and_invalid_response(self):
        self.assertEqual(self.search({'features': []})['hotels'], [])
        with self.assertRaises(ZipLookupError):
            self.search({})

    def test_unresolved_does_not_request_places(self):
        with patch('places.lookup_zip', return_value=None), patch('places.urlopen') as request:
            self.assertIsNone(places.search_hotels('16802'))
            request.assert_not_called()

    def test_failure_and_rate_limit(self):
        for status, error in [(500, ZipLookupError), (429, ZipRateLimitError)]:
            with patch('places.lookup_zip', return_value=CENTER), patch('places.urlopen', side_effect=HTTPError('private-url', status, 'private-message', {}, None)):
                with self.assertRaises(error) as caught:
                    places.search_hotels('16802')
                self.assertNotIn('private', str(caught.exception))

    def test_shortlist_duplicate_snapshot_restart_and_remove(self):
        result = self.search()
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'test.sqlite3'
            with TestClient(create_app(path)) as client, patch('main.search_hotels', return_value=result):
                self.assertEqual(client.get('/api/hotels?postcode=16802').status_code, 200)
                url = '/api/shortlist?place_id=fixture-hotel-a'
                self.assertTrue(client.post(url).json()['created'])
                self.assertFalse(client.post(url).json()['created'])
                with connect(path) as db:
                    self.assertEqual(db.execute('SELECT count(*) FROM shortlist').fetchone()[0], 1)
                    db.execute('DELETE FROM discovered_places')
                self.assertEqual(client.post('/api/shortlist?place_id=never-returned').status_code, 404)
            with TestClient(create_app(path)) as client:
                self.assertEqual(client.get('/api/shortlist').json()[0]['name'], 'Fixture Hotel A')
                self.assertEqual(client.delete(url).status_code, 204)
            with TestClient(create_app(path)) as client:
                self.assertEqual(client.get('/api/shortlist').json(), [])
                self.assertEqual(len(client.get('/api/users').json()), 6)

    def test_route_errors(self):
        with TemporaryDirectory() as folder, TestClient(create_app(Path(folder) / 'test.sqlite3')) as client:
            with patch('main.search_hotels') as search:
                self.assertEqual(client.get('/api/hotels?postcode=bad').status_code, 422)
                search.assert_not_called()
            for side_effect, expected in [(ZipLookupError('private'), 502), (ZipRateLimitError('private'), 429)]:
                with patch('main.search_hotels', side_effect=side_effect):
                    response = client.get('/api/hotels?postcode=16802')
                    self.assertEqual(response.status_code, expected)
                    self.assertNotIn('private', response.text)


if __name__ == '__main__':
    unittest.main()
