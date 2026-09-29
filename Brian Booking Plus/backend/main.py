"""Brian Booking Plus: SQLite hotel search and simulated booking CRUD."""
from contextlib import asynccontextmanager
from datetime import date
import os
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field

from config import geoapify_key_status
from database import DEFAULT_DB_PATH, connect, initialize
from zip_lookup import ZipConfigurationError, ZipLookupError, ZipRateLimitError, lookup_zip
from places import search_hotels
import shortlist

STAY_SELECT = """SELECT h.hotel_id, h.hotel_name, h.city, h.state, h.nightly_rate_usd,
    t.trip_id, t.trip_name, t.check_in, t.check_out
    FROM trips t JOIN hotels h ON h.hotel_id = t.hotel_id"""
BOOKING_SELECT = """SELECT b.*, u.display_name, h.hotel_id, h.hotel_name, h.city, h.state,
    h.nightly_rate_usd, t.trip_name, t.check_in, t.check_out
    FROM bookings b JOIN users u ON u.user_id = b.user_id
    JOIN trips t ON t.trip_id = b.trip_id JOIN hotels h ON h.hotel_id = t.hotel_id"""


class Stay(BaseModel):
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: int
    trip_id: str
    trip_name: str
    check_in: date
    check_out: date
    nights: int
    stay_price_usd: int


class Traveler(BaseModel):
    user_id: str
    display_name: str


class Booking(Stay):
    booking_id: str
    user_id: str
    display_name: str
    booked_on: date
    status: Literal["confirmed", "cancelled"]


class NewBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(min_length=1, max_length=100)
    trip_id: str = Field(min_length=1, max_length=100)


class CancelBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["cancelled"]


def with_price(row):
    result = dict(row)
    result["nights"] = (date.fromisoformat(result["check_out"]) - date.fromisoformat(result["check_in"])).days
    result["stay_price_usd"] = result["nights"] * result["nightly_rate_usd"]
    return result


def create_app(db_path: Path | None = None):
    path = Path(db_path or os.environ.get("TRAVEL_DB_PATH") or DEFAULT_DB_PATH).resolve()

    @asynccontextmanager
    async def lifespan(app):
        initialize(path)
        shortlist.initialize_shortlist(path)
        yield

    app = FastAPI(title="Brian Booking Plus", version="2.0.0", lifespan=lifespan)

    @app.get('/api/hotels')
    def hotels(postcode: str = Query(pattern=r'^[0-9]{5}$', min_length=5, max_length=5)):
        try:
            result = search_hotels(postcode)
        except ZipConfigurationError:
            raise HTTPException(503, 'Hotel search is not configured.') from None
        except ZipRateLimitError:
            raise HTTPException(429, 'Service limit reached. Try again later.') from None
        except ZipLookupError:
            raise HTTPException(502, 'Hotel search failed. Please try again.') from None
        if result is None:
            raise HTTPException(404, f'ZIP {postcode} could not be resolved.')
        shortlist.remember_results(path, result['hotels'])
        return result

    @app.get('/api/shortlist')
    def saved_hotels():
        return shortlist.list_saved(path)

    @app.post('/api/shortlist')
    def save_hotel(place_id: str = Query(min_length=1, max_length=2048)):
        try:
            created = shortlist.save_place(path, place_id)
        except LookupError:
            raise HTTPException(404, 'Search for this hotel before saving it.') from None
        return {'created': created, 'shortlist': shortlist.list_saved(path)}

    @app.delete('/api/shortlist', status_code=204)
    def remove_hotel(place_id: str = Query(min_length=1, max_length=2048)):
        shortlist.remove_place(path, place_id)
        return Response(status_code=204)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "geoapify": geoapify_key_status()}

    @app.get("/api/demo/zip-location")
    def demo_zip_location(postcode: str = Query(default="16802", pattern=r"^[0-9]{5}$", min_length=5, max_length=5)):
        try:
            location = lookup_zip(postcode)
        except ZipConfigurationError:
            raise HTTPException(503, "ZIP lookup is not configured.") from None
        except ZipLookupError:
            raise HTTPException(502, "ZIP lookup provider request failed.") from None
        if location is None:
            raise HTTPException(404, f"ZIP {postcode} could not be resolved.")
        return location

    @app.get("/api/stays", response_model=list[Stay])
    def search_stays(hotel_name: str = Query(default="", max_length=200)):
        query = hotel_name.strip().casefold()
        with connect(path) as db:
            db.create_function("casefold", 1, str.casefold)
            rows = db.execute(STAY_SELECT + " WHERE instr(casefold(h.hotel_name), ?) > 0 ORDER BY t.trip_id", (query,)).fetchall()
        return [with_price(row) for row in rows]

    @app.get("/api/users", response_model=list[Traveler])
    def list_users():
        with connect(path) as db:
            return [dict(row) for row in db.execute("SELECT * FROM users ORDER BY user_id")]

    @app.get("/api/bookings", response_model=list[Booking])
    def list_bookings(user_id: str = Query(min_length=1, max_length=100)):
        with connect(path) as db:
            if not db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone():
                raise HTTPException(404, "Traveler not found.")
            rows = db.execute(BOOKING_SELECT + " WHERE b.user_id = ? ORDER BY b.booked_on DESC, b.rowid DESC", (user_id,)).fetchall()
        return [with_price(row) for row in rows]

    @app.post("/api/bookings", response_model=Booking, status_code=201)
    def create_booking(payload: NewBooking):
        booking_id = "B-" + uuid4().hex
        with connect(path) as db:
            db.execute("BEGIN IMMEDIATE")
            if not db.execute("SELECT 1 FROM users WHERE user_id = ?", (payload.user_id,)).fetchone():
                raise HTTPException(404, "Traveler not found.")
            if not db.execute("SELECT 1 FROM trips WHERE trip_id = ?", (payload.trip_id,)).fetchone():
                raise HTTPException(404, "Stay not found.")
            db.execute("INSERT INTO bookings VALUES (?, ?, ?, ?, 'confirmed')", (booking_id, payload.user_id, payload.trip_id, date.today().isoformat()))
            result = db.execute(BOOKING_SELECT + " WHERE b.booking_id = ?", (booking_id,)).fetchone()
        return with_price(result)

    @app.patch("/api/bookings/{booking_id}", response_model=Booking)
    def cancel_booking(booking_id: str, payload: CancelBooking):
        with connect(path) as db:
            changed = db.execute("UPDATE bookings SET status = ? WHERE booking_id = ?", (payload.status, booking_id))
            if changed.rowcount == 0:
                raise HTTPException(404, "Booking not found.")
            result = db.execute(BOOKING_SELECT + " WHERE b.booking_id = ?", (booking_id,)).fetchone()
        return with_price(result)

    @app.delete("/api/bookings/{booking_id}", status_code=204)
    def delete_booking(booking_id: str):
        with connect(path) as db:
            changed = db.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
            if changed.rowcount == 0:
                raise HTTPException(404, "Booking not found.")
        return Response(status_code=204)

    return app


app = create_app()
