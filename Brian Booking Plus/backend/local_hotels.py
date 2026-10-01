"""Local API-hotel snapshots and dated, simulated classroom inventory."""
import json
from database import connect
from places import distance_m

DEMO_DATES = tuple(f'2026-10-{day:02}' for day in range(10, 15))


def initialize_local_hotels(path):
    # Separate additive migration: never alter/reseed Assignment 1 tables.
    statements = [
        '''CREATE TABLE IF NOT EXISTS saved_hotels (
            hotel_id TEXT PRIMARY KEY NOT NULL,
            name TEXT, address TEXT,
            latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
            longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180))''',
        '''CREATE TABLE IF NOT EXISTS demo_hotel_nights (
            hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id) ON DELETE CASCADE,
            stay_date TEXT NOT NULL CHECK(
                stay_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
                AND date(stay_date, '+0 days') IS NOT NULL
                AND date(stay_date, '+0 days') = stay_date),
            nightly_rate_cents INTEGER NOT NULL DEFAULT 10000
                CHECK(typeof(nightly_rate_cents) = 'integer' AND nightly_rate_cents >= 0),
            rooms_available INTEGER NOT NULL DEFAULT 20
                CHECK(typeof(rooms_available) = 'integer' AND rooms_available >= 0),
            PRIMARY KEY(hotel_id, stay_date))''',
        '''CREATE TABLE IF NOT EXISTS saved_zip_locations (
            postcode TEXT PRIMARY KEY NOT NULL CHECK(postcode GLOB '[0-9][0-9][0-9][0-9][0-9]'),
            country_code TEXT NOT NULL CHECK(country_code = 'us'),
            latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
            longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
            locality TEXT)''',
        '''CREATE TABLE IF NOT EXISTS saved_hotel_zips (
            hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id) ON DELETE CASCADE,
            postcode TEXT NOT NULL REFERENCES saved_zip_locations(postcode),
            PRIMARY KEY(hotel_id, postcode))''',
    ]
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        for statement in statements:
            db.execute(statement)


def saved_ids(path):
    with connect(path) as db:
        return [r['hotel_id'] for r in db.execute('SELECT hotel_id FROM saved_hotels ORDER BY hotel_id')]


def local_results(path, postcode):
    # One fresh read transaction for center, hotels and nights on every search.
    with connect(path) as db:
        db.execute('BEGIN')
        center = db.execute('SELECT * FROM saved_zip_locations WHERE postcode=?', (postcode,)).fetchone()
        rows = db.execute('''SELECT h.* FROM saved_hotels h JOIN saved_hotel_zips z
            ON z.hotel_id=h.hotel_id WHERE z.postcode=? ORDER BY h.hotel_id''', (postcode,)).fetchall()
        hotels = []
        for row in rows:
            nights = db.execute('''SELECT stay_date, nightly_rate_cents, rooms_available
                FROM demo_hotel_nights WHERE hotel_id=? ORDER BY stay_date''', (row['hotel_id'],)).fetchall()
            hotels.append({
                'place_id': row['hotel_id'], 'provider': 'geoapify',
                'name': row['name'], 'address': row['address'],
                'latitude': row['latitude'], 'longitude': row['longitude'], 'postcode': postcode,
                'distance_m': round(distance_m(center['latitude'], center['longitude'], row['latitude'], row['longitude'])),
                'nights': [dict(n) for n in nights],
            })
    return {'center': dict(center) if center else None, 'hotels': hotels, 'radius_m': 5000}


def add_local(path, hotel_id, center):
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        # Reuse server-observed Part 1 data, not client-supplied hotel fields.
        candidate = db.execute('SELECT snapshot FROM discovered_places WHERE place_id=?', (hotel_id,)).fetchone()
        if candidate is None:
            raise LookupError('Search for this API hotel before adding it locally.')
        hotel = json.loads(candidate['snapshot'])
        if hotel['postcode'] != center['postcode']:
            raise ValueError('Search this ZIP again before adding the hotel.')
        if distance_m(center['latitude'], center['longitude'], hotel['latitude'], hotel['longitude']) > 5000:
            raise ValueError('Hotel does not match this search location.')
        created = db.execute('''INSERT INTO saved_hotels(hotel_id,name,address,latitude,longitude)
            VALUES (?,?,?,?,?) ON CONFLICT(hotel_id) DO NOTHING''',
            (hotel_id, hotel.get('name'), hotel.get('address'), hotel['latitude'], hotel['longitude'])).rowcount > 0
        db.execute('''INSERT INTO saved_zip_locations(postcode,country_code,latitude,longitude,locality)
            VALUES (?,?,?,?,?) ON CONFLICT(postcode) DO NOTHING''',
            (center['postcode'], center['country_code'], center['latitude'], center['longitude'], center.get('locality')))
        db.execute('INSERT INTO saved_hotel_zips VALUES (?,?) ON CONFLICT DO NOTHING', (hotel_id, center['postcode']))
        # Defaults belong to the schema. Never replace manually edited nightly values.
        db.executemany('''INSERT INTO demo_hotel_nights(hotel_id,stay_date) VALUES (?,?)
            ON CONFLICT(hotel_id,stay_date) DO NOTHING''', [(hotel_id, day) for day in DEMO_DATES])
    return created


def remove_local(path, hotel_id):
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        postcodes = [r[0] for r in db.execute('SELECT postcode FROM saved_hotel_zips WHERE hotel_id=?', (hotel_id,))]
        db.execute('DELETE FROM saved_hotels WHERE hotel_id=?', (hotel_id,))
        for postcode in postcodes:
            db.execute('''DELETE FROM saved_zip_locations WHERE postcode=? AND NOT EXISTS
                (SELECT 1 FROM saved_hotel_zips WHERE postcode=?)''', (postcode, postcode))
