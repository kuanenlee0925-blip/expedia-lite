"""CSV-backed hotel search for Expedia Lite, Part 1."""
import csv
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Query
from pydantic import BaseModel

DATA_DIR = Path(__file__).resolve().parent / "data"
app = FastAPI(title="Expedia Lite", version="1.0.0")


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


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


@app.get("/api/stays", response_model=list[Stay])
def search_stays(hotel_name: str = Query(default="", max_length=200)):
    """Join hotels and trips by hotel_id; blank input lists all stays."""
    query = hotel_name.strip().casefold()
    hotels = {
        hotel["hotel_id"]: hotel
        for hotel in read_csv("hotels.csv")
        if query in hotel["hotel_name"].casefold()
    }
    results = []
    for trip in read_csv("trips.csv"):
        hotel = hotels.get(trip["hotel_id"])
        if hotel is None:
            continue
        nights = (date.fromisoformat(trip["check_out"]) - date.fromisoformat(trip["check_in"])).days
        rate = int(hotel["nightly_rate_usd"])
        results.append(Stay(**(hotel | trip | {
            "nightly_rate_usd": rate,
            "nights": nights,
            "stay_price_usd": nights * rate,
        })))
    return results
