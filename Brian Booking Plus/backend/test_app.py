"""API and persistence checks; every test uses a disposable database."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from fastapi.testclient import TestClient

from database import DATA_DIR, connect, initialize
from main import create_app


class TravelTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.client = TestClient(create_app(self.path))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def book(self, trip_id="T001"):
        response = self.client.post("/api/bookings", json={"user_id": "U006", "trip_id": trip_id})
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def history(self, user_id="U006"):
        response = self.client.get("/api/bookings", params={"user_id": user_id})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_seed_search_and_joined_history(self):
        with connect(self.path) as db:
            counts = {table: db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                      for table in ("hotels", "trips", "users", "bookings")}
        self.assertEqual(counts, {"hotels": 8, "trips": 12, "users": 6, "bookings": 6})
        self.assertEqual(len(self.client.get("/api/users").json()), 6)
        stays = self.client.get("/api/stays", params={"hotel_name": "  hArBoR  "}).json()
        self.assertEqual([s["trip_id"] for s in stays], ["T001", "T009"])
        self.assertTrue(all(s["nights"] == 2 and s["stay_price_usd"] == 300 for s in stays))
        self.assertEqual(len(self.client.get("/api/stays").json()), 12)
        for query in ("No Such Hotel", "%", "_", "' OR 1=1 --"):
            self.assertEqual(self.client.get("/api/stays", params={"hotel_name": query}).json(), [])
        self.assertEqual(self.history(), [])
        history = {b["booking_id"]: b for b in self.history("U001")}
        self.assertEqual(set(history), {"B001", "B002"})
        self.assertEqual(history["B001"]["hotel_name"], "Harbor Lantern Hotel")
        self.assertEqual(history["B002"]["status"], "cancelled")

    def test_crud_and_reopen_preserve_changes_without_reseeding(self):
        cancelled, retained, deleted = self.book(), self.book("T009"), self.book("T005")
        response = self.client.patch(f"/api/bookings/{cancelled['booking_id']}", json={"status": "cancelled"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "cancelled")
        self.assertEqual(self.client.delete(f"/api/bookings/{deleted['booking_id']}").status_code, 204)
        self.assertEqual(self.client.delete("/api/bookings/B006").status_code, 204)
        self.client.__exit__(None, None, None)
        # Startup of an initialized database must work even without the CSVs.
        initialize(self.path, Path(self.temp.name) / "missing-csv-folder")
        self.client = TestClient(create_app(self.path))
        self.client.__enter__()
        rows = {b["booking_id"]: b for b in self.history()}
        self.assertEqual(set(rows), {cancelled["booking_id"], retained["booking_id"]})
        self.assertEqual(rows[cancelled["booking_id"]]["status"], "cancelled")
        self.assertEqual(rows[retained["booking_id"]]["status"], "confirmed")
        self.assertEqual(self.history("U005"), [])  # Deleted seed record stays deleted.
        with connect(self.path) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM bookings").fetchone()[0], 7)

    def test_reads_use_sqlite_after_seed(self):
        with connect(self.path) as db:
            db.execute("UPDATE hotels SET hotel_name = ?, nightly_rate_usd = ? WHERE hotel_id = ?", ("Stored Hotel", 180, "H001"))
        self.assertEqual(self.client.get("/api/stays", params={"hotel_name": "Harbor Lantern"}).json(), [])
        rows = self.client.get("/api/stays", params={"hotel_name": "Stored Hotel"}).json()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["stay_price_usd"], 360)
        self.assertEqual(next(b for b in self.history("U001") if b["booking_id"] == "B001")["hotel_name"], "Stored Hotel")

    def test_invalid_references_status_and_missing_records(self):
        for payload in ({"user_id": "missing", "trip_id": "T001"}, {"user_id": "U006", "trip_id": "missing"}):
            self.assertEqual(self.client.post("/api/bookings", json=payload).status_code, 404)
        self.assertEqual(self.client.post("/api/bookings", json={"user_id": "U006"}).status_code, 422)
        self.assertEqual(self.client.patch("/api/bookings/B001", json={"status": "paid"}).status_code, 422)
        self.assertEqual(self.client.patch("/api/bookings/missing", json={"status": "cancelled"}).status_code, 404)
        self.assertEqual(self.client.delete("/api/bookings/missing").status_code, 404)
        self.assertEqual(self.client.get("/api/bookings", params={"user_id": "missing"}).status_code, 404)
        self.assertEqual(self.history(), [])

    def test_unique_ids_for_concurrent_bookings(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            responses = list(pool.map(lambda _: self.client.post("/api/bookings", json={"user_id": "U006", "trip_id": "T001"}), range(12)))
        self.assertTrue(all(r.status_code == 201 for r in responses))
        ids = {r.json()["booking_id"] for r in responses}
        self.assertEqual(len(ids), 12)
        self.assertEqual(len(self.history()), 12)

    def test_database_rejects_orphan_and_invalid_status(self):
        with self.assertRaises(sqlite3.IntegrityError):
            with connect(self.path) as db:
                db.execute("INSERT INTO bookings VALUES ('bad', 'U006', 'missing', '2026-09-15', 'confirmed')")
        with self.assertRaises(sqlite3.IntegrityError):
            with connect(self.path) as db:
                db.execute("UPDATE bookings SET status = 'paid' WHERE booking_id = 'B001'")

    def test_failed_seed_rolls_back_and_can_retry(self):
        path = Path(self.temp.name) / "failed.sqlite3"
        partial = Path(self.temp.name) / "partial"
        partial.mkdir()
        shutil.copyfile(DATA_DIR / "hotels.csv", partial / "hotels.csv")
        with self.assertRaises(FileNotFoundError):
            initialize(path, partial)
        with connect(path) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table'").fetchone()[0], 0)
        initialize(path)
        with connect(path) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM bookings").fetchone()[0], 6)


if __name__ == "__main__":
    unittest.main()
