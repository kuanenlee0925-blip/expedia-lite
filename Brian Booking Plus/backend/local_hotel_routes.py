"""Local-storage routes; the frozen Part 1 provider routes stay unchanged."""
import sqlite3
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
import local_hotels


class SearchCenter(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    postcode: str = Field(pattern=r'^[0-9]{5}$', min_length=5, max_length=5)
    country_code: Literal['us']
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    locality: str | None = Field(default=None, max_length=1000)


class AddLocalHotel(BaseModel):
    hotel_id: str = Field(min_length=1, max_length=2048)
    center: SearchCenter


def local_router(path):
    router = APIRouter(prefix='/api/local-hotels')

    def run(operation, *args):
        try:
            return operation(path, *args)
        except sqlite3.Error:
            raise HTTPException(503, 'Local hotel storage is unavailable. Please try again.') from None

    @router.get('/status')
    def status():
        return {'hotel_ids': run(local_hotels.saved_ids)}

    @router.get('')
    def lookup(postcode: str = Query(pattern=r'^[0-9]{5}$', min_length=5, max_length=5)):
        return run(local_hotels.local_results, postcode)

    @router.post('')
    def add(body: AddLocalHotel):
        try:
            created = run(local_hotels.add_local, body.hotel_id, body.center.model_dump())
        except LookupError:
            raise HTTPException(404, 'Search for this API hotel before adding it locally.') from None
        except ValueError:
            raise HTTPException(409, 'Search this ZIP again before adding the hotel.') from None
        return {'hotel_id': body.hotel_id, 'created': created}

    @router.delete('', status_code=204)
    def remove(hotel_id: str = Query(min_length=1, max_length=2048)):
        run(local_hotels.remove_local, hotel_id)
        return Response(status_code=204)

    return router
