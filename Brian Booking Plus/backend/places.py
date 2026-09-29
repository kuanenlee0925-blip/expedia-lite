"""Geoapify hotel controller. No prices, bookings, or client credentials."""
import json
import math
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import config
from zip_lookup import lookup_zip, ZipLookupError, ZipRateLimitError

LIMIT = 20
RADIUS = 5000


def distance_m(lat1, lon1, lat2, lon2):
    a, b = math.radians(lat1), math.radians(lat2)
    h = math.sin((b-a)/2)**2 + math.cos(a)*math.cos(b)*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371000 * 2 * math.asin(min(1, math.sqrt(h)))


def search_hotels(postcode):
    center = lookup_zip(postcode)
    if center is None:
        return None
    lat, lon = center['latitude'], center['longitude']
    params = urlencode({'categories': 'accommodation.hotel',
                        'filter': f'circle:{lon},{lat},{RADIUS}',
                        'bias': f'proximity:{lon},{lat}', 'limit': LIMIT,
                        'apiKey': config.GEOAPIFY_API_KEY})
    try:
        with urlopen('https://api.geoapify.com/v2/places?' + params, timeout=10) as response:
            payload = json.load(response)
    except HTTPError as error:
        status = error.code
        error.close()
        if status == 429:
            raise ZipRateLimitError('Service limit reached. Try again later.') from None
        raise ZipLookupError('Hotel provider request failed.') from None
    except (URLError, OSError, HTTPException, ValueError):
        raise ZipLookupError('Hotel provider request failed.') from None
    if not isinstance(payload, dict) or not isinstance(payload.get('features'), list):
        raise ZipLookupError('Hotel provider returned an invalid response.')
    hotels, seen = [], set()
    for feature in payload['features'][:LIMIT]:
        p = feature.get('properties') if isinstance(feature, dict) else None
        if not isinstance(p, dict):
            raise ZipLookupError('Hotel provider returned an invalid response.')
        identifier, y, x = p.get('place_id'), p.get('lat'), p.get('lon')
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            continue
        if not all(type(v) in (int, float) and math.isfinite(v) for v in (y, x)):
            continue
        if not (-90 <= y <= 90 and -180 <= x <= 180):
            continue
        distance = distance_m(lat, lon, y, x)
        if distance > RADIUS:
            continue
        seen.add(identifier)
        clean = lambda value: value.strip() if isinstance(value, str) and value.strip() else None
        hotels.append({'place_id': identifier, 'provider': 'geoapify',
                       'name': clean(p.get('name')), 'address': clean(p.get('formatted')),
                       'latitude': y, 'longitude': x, 'postcode': postcode,
                       'distance_m': round(distance)})
    return {'center': center, 'hotels': hotels, 'radius_m': RADIUS, 'limit': LIMIT,
            'omitted': len(payload['features'][:LIMIT]) - len(hotels)}
