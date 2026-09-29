"""SQLite connections and transactional, one-time import of the course CSVs."""
from contextlib import contextmanager
import csv
from pathlib import Path
import sqlite3

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "storage" / "expedia.sqlite3"


@contextmanager
def connect(path: Path):
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path: Path, data_dir: Path = DATA_DIR):
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version == 1:
            return
        if version != 0:
            raise RuntimeError(f"Unsupported database version: {version}")
        statements = [
            """CREATE TABLE hotels (
                hotel_id TEXT PRIMARY KEY, hotel_name TEXT NOT NULL,
                city TEXT NOT NULL, state TEXT NOT NULL,
                nightly_rate_usd INTEGER NOT NULL CHECK(nightly_rate_usd >= 0))""",
            """CREATE TABLE trips (
                trip_id TEXT PRIMARY KEY, hotel_id TEXT NOT NULL REFERENCES hotels(hotel_id),
                trip_name TEXT NOT NULL, check_in TEXT NOT NULL, check_out TEXT NOT NULL,
                CHECK(check_out > check_in))""",
            """CREATE TABLE users (
                user_id TEXT PRIMARY KEY, display_name TEXT NOT NULL)""",
            """CREATE TABLE bookings (
                booking_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id),
                trip_id TEXT NOT NULL REFERENCES trips(trip_id), booked_on TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('confirmed', 'cancelled')))""",
            "CREATE INDEX bookings_user_idx ON bookings(user_id)",
        ]
        for statement in statements:
            db.execute(statement)
        columns = {
            "hotels": "hotel_id,hotel_name,city,state,nightly_rate_usd",
            "trips": "trip_id,hotel_id,trip_name,check_in,check_out",
            "users": "user_id,display_name",
            "bookings": "booking_id,user_id,trip_id,booked_on,status",
        }
        for table, names in columns.items():
            with (data_dir / f"{table}.csv").open(encoding="utf-8-sig", newline="") as file:
                placeholders = ",".join(f":{name}" for name in names.split(","))
                db.executemany(f"INSERT INTO {table} ({names}) VALUES ({placeholders})", csv.DictReader(file))
        # The seed marker commits with all records; any failed import rolls back.
        db.execute("PRAGMA user_version = 1")
