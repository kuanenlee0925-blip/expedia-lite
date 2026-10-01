"""Automated fixtures only: mutations always use temporary databases."""
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from database import connect, initialize
from main import create_app
from shortlist import remember_results
import local_hotels

CENTER = {'postcode': '16802', 'country_code': 'us', 'latitude': 40.80, 'longitude': -77.86, 'locality': 'Fixture center'}
HOTEL = {'place_id': 'fixture-provider-01', 'provider': 'geoapify', 'name': 'Fixture hotel',
         'address': None, 'latitude': 40.81, 'longitude': -77.86, 'postcode': '16802', 'distance_m': 1112}


class LocalHotelTests(unittest.TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'fixture.sqlite3'
        initialize(self.path)
        with connect(self.path) as db:
            self.original = {t: [tuple(r) for r in db.execute(f'SELECT * FROM {t} ORDER BY 1')]
                             for t in ('hotels', 'trips', 'users', 'bookings')}
        self.client = self.enterContext(TestClient(create_app(self.path)))
        remember_results(self.path, [HOTEL, {**HOTEL, 'place_id': 'fixture-provider-02'}])

    def add(self, hotel_id=HOTEL['place_id'], center=CENTER):
        return self.client.post('/api/local-hotels', json={'hotel_id': hotel_id, 'center': center})

    def local(self):
        return self.client.get('/api/local-hotels?postcode=16802')

    def test_repeatable_migration_defaults_keys_and_original_records(self):
        local_hotels.initialize_local_hotels(self.path)
        self.assertTrue(self.add().json()['created'])
        with connect(self.path) as db:
            for table, original in self.original.items():
                self.assertEqual([tuple(r) for r in db.execute(f'SELECT * FROM {table} ORDER BY 1')], original)
            columns = {r['name']: r for r in db.execute('PRAGMA table_info(demo_hotel_nights)')}
            self.assertEqual(columns['hotel_id']['pk'], 1)
            self.assertEqual(columns['stay_date']['pk'], 2)
            self.assertEqual(columns['nightly_rate_cents']['dflt_value'], '10000')
            self.assertEqual(columns['rooms_available']['dflt_value'], '20')
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            nights = [tuple(r) for r in db.execute('SELECT stay_date,nightly_rate_cents,rooms_available FROM demo_hotel_nights ORDER BY stay_date')]
            self.assertEqual(nights, [(d, 10000, 20) for d in local_hotels.DEMO_DATES])

    def test_duplicate_save_preserves_committed_values_and_reopen(self):
        self.add()
        with connect(self.path) as db:
            db.execute('UPDATE demo_hotel_nights SET nightly_rate_cents=12345,rooms_available=7 WHERE hotel_id=? AND stay_date=?',
                       (HOTEL['place_id'], '2026-10-10'))
        self.assertFalse(self.add().json()['created'])
        with TestClient(create_app(self.path)) as reopened:
            hotel = reopened.get('/api/local-hotels?postcode=16802').json()['hotels'][0]
            self.assertEqual(hotel['nights'][0], {'stay_date': '2026-10-10', 'nightly_rate_cents': 12345, 'rooms_available': 7})
            self.assertEqual(len(hotel['nights']), 5)
            self.assertEqual(reopened.get('/api/local-hotels/status').json()['hotel_ids'], [HOTEL['place_id']])
        with connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM saved_hotels').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM saved_hotel_zips').fetchone()[0], 1)

    def test_remove_cascades_multiple_zip_associations_preserves_other_records(self):
        self.add()
        self.add('fixture-provider-02')
        another = {**CENTER, 'postcode': '16801'}
        remember_results(self.path, [{**HOTEL, 'postcode': '16801'}])
        self.add(center=another)
        response = self.client.delete('/api/local-hotels', params={'hotel_id': HOTEL['place_id']})
        self.assertEqual(response.status_code, 204)
        with connect(self.path) as db:
            for table in ('saved_hotels', 'saved_hotel_zips', 'demo_hotel_nights'):
                self.assertEqual(db.execute(f'SELECT COUNT(*) FROM {table} WHERE hotel_id=?', (HOTEL['place_id'],)).fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM demo_hotel_nights').fetchone()[0], 5)
            self.assertEqual([r[0] for r in db.execute('SELECT postcode FROM saved_zip_locations')], ['16802'])
            self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM bookings ORDER BY 1')], self.original['bookings'])
        self.assertEqual(self.local().json()['hotels'][0]['place_id'], 'fixture-provider-02')

    def test_constraints_reject_invalid_dates_values_foreign_keys_and_coordinates(self):
        self.add()
        statements = [
            ("INSERT INTO demo_hotel_nights(hotel_id,stay_date) VALUES (?,?)", ('unknown', '2026-10-10')),
            ("INSERT INTO demo_hotel_nights(hotel_id,stay_date) VALUES (?,?)", (HOTEL['place_id'], '2026-02-30')),
            ("UPDATE demo_hotel_nights SET nightly_rate_cents=-1", ()),
            ("UPDATE demo_hotel_nights SET rooms_available=1.5", ()),
            ("UPDATE saved_hotels SET latitude=91", ()),
            ("INSERT INTO demo_hotel_nights(hotel_id,stay_date) VALUES (?,?)", (HOTEL['place_id'], '2026-10-10')),
        ]
        for sql, args in statements:
            with self.subTest(sql=sql), self.assertRaises(sqlite3.IntegrityError), connect(self.path) as db:
                db.execute(sql, args)

    def test_atomic_save_and_remove_on_database_failure(self):
        with connect(self.path) as db:
            db.execute("""CREATE TRIGGER fixture_save_failure BEFORE INSERT ON demo_hotel_nights
                WHEN NEW.stay_date='2026-10-12' BEGIN SELECT RAISE(ABORT,'fixture'); END""")
        self.assertEqual(self.add().status_code, 503)
        self.assertEqual(self.local().json()['hotels'], [])
        with connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM saved_hotels').fetchone()[0], 0)
            db.execute('DROP TRIGGER fixture_save_failure')
        self.add()
        with connect(self.path) as db:
            db.execute("CREATE TRIGGER fixture_remove_failure BEFORE DELETE ON demo_hotel_nights BEGIN SELECT RAISE(ABORT,'fixture'); END")
        self.assertEqual(self.client.delete('/api/local-hotels', params={'hotel_id': HOTEL['place_id']}).status_code, 503)
        self.assertEqual(len(self.local().json()['hotels'][0]['nights']), 5)

    def test_local_failure_empty_and_part1_contract(self):
        with patch('main.search_hotels') as provider:
            self.assertEqual(self.local().json(), {'center': None, 'hotels': [], 'radius_m': 5000})
            self.assertEqual(self.client.get('/api/local-hotels?postcode=123').status_code, 422)
            provider.assert_not_called()
        with patch('local_hotels.local_results', side_effect=sqlite3.OperationalError('private database details')):
            response = self.local()
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('private', response.text)
        expected = {'center': CENTER, 'hotels': [HOTEL], 'limit': 20, 'radius_m': 5000, 'omitted': 0}
        with patch('main.search_hotels', return_value=expected):
            self.assertEqual(self.client.get('/api/hotels?postcode=16802').json(), expected)

    def test_unknown_id_and_wrong_context_are_rejected(self):
        self.assertEqual(self.add('never-returned').status_code, 404)
        self.assertEqual(self.add(center={**CENTER, 'postcode': '00000'}).status_code, 409)
        self.assertEqual(self.add(center={**CENTER, 'country_code': 'ca'}).status_code, 422)
        self.assertEqual(self.add(center={**CENTER, 'latitude': 100}).status_code, 422)


if __name__ == '__main__':
    unittest.main()
