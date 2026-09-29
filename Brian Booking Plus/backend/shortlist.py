"""Persistent external-place snapshots, independent of sample Hotel prices."""
import json
from database import connect


def initialize_shortlist(path):
    # Additive, idempotent extension; the original CSV seed and its marker stay intact.
    with connect(path) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS discovered_places (
            place_id TEXT PRIMARY KEY, snapshot TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS shortlist (
            place_id TEXT PRIMARY KEY, snapshot TEXT NOT NULL,
            saved_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')))''')


def remember_results(path, hotels):
    with connect(path) as db:
        db.executemany('INSERT INTO discovered_places VALUES (?, ?) ON CONFLICT(place_id) DO UPDATE SET snapshot=excluded.snapshot',
                       [(h['place_id'], json.dumps(h)) for h in hotels])


def list_saved(path):
    with connect(path) as db:
        rows = db.execute('SELECT snapshot, saved_at FROM shortlist ORDER BY saved_at DESC, place_id').fetchall()
    return [{**json.loads(r['snapshot']), 'saved_at': r['saved_at']} for r in rows]


def save_place(path, place_id):
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        existing = db.execute('SELECT 1 FROM shortlist WHERE place_id=?', (place_id,)).fetchone()
        if existing:
            return False
        candidate = db.execute('SELECT snapshot FROM discovered_places WHERE place_id=?', (place_id,)).fetchone()
        if candidate is None:
            raise LookupError('Search for this hotel before saving it.')
        db.execute('INSERT INTO shortlist(place_id,snapshot) VALUES (?,?)', (place_id, candidate['snapshot']))
    return True


def remove_place(path, place_id):
    with connect(path) as db:
        return db.execute('DELETE FROM shortlist WHERE place_id=?', (place_id,)).rowcount > 0
