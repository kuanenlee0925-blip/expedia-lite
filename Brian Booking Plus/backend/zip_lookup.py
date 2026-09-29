"""Small Geoapify postcode controller, independent of routes and hotel data."""
import json
import math
import re
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import config


class ZipLookupError(RuntimeError):
    """Configuration or provider failure, with a credential-free message."""


class ZipConfigurationError(ZipLookupError):
    """The backend has no configured Geoapify key."""


class ZipRateLimitError(ZipLookupError):
    """The provider refused a request because of a service limit."""


def lookup_zip(postcode: str) -> dict | None:
    """Return a matching US location, None if unresolved, or raise ZipLookupError."""
    if not isinstance(postcode, str) or not re.fullmatch(r"[0-9]{5}", postcode):
        raise ValueError("Postcode must be a five-digit ZIP string.")
    if not config.GEOAPIFY_API_KEY:
        raise ZipConfigurationError("ZIP lookup is not configured.")

    params = urlencode({
        "postcode": postcode,
        "type": "postcode",
        "filter": "countrycode:us",
        "format": "json",
        "apiKey": config.GEOAPIFY_API_KEY,
    })
    try:
        with urlopen("https://api.geoapify.com/v1/geocode/search?" + params, timeout=10) as response:
            if response.status != 200:
                raise ZipLookupError("ZIP lookup provider request failed.")
            payload = json.load(response)
    except HTTPError as error:
        status = error.code
        error.close()
        if status == 429:
            raise ZipRateLimitError("Service limit reached. Try again later.") from None
        raise ZipLookupError("ZIP lookup provider request failed.") from None
    except (URLError, OSError, HTTPException, ValueError):
        # Provider exceptions can contain the credential-bearing URL.
        raise ZipLookupError("ZIP lookup provider request failed.") from None

    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ZipLookupError("ZIP lookup provider returned an invalid response.")
    for result in payload["results"]:
        if not isinstance(result, dict):
            raise ZipLookupError("ZIP lookup provider returned an invalid response.")
        if result.get("postcode") != postcode or str(result.get("country_code", "")).lower() != "us":
            continue
        lat, lon = result.get("lat"), result.get("lon")
        if not all(type(value) in (int, float) and math.isfinite(value) for value in (lat, lon)):
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        location = {"postcode": postcode, "country_code": "us", "latitude": lat, "longitude": lon}
        locality = result.get("city") or result.get("town") or result.get("village")
        if isinstance(locality, str) and locality.strip():
            location["locality"] = locality.strip()
        return location
    return None
