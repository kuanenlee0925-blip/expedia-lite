# Brian Booking Plus

## Assignment 2: nearby hotels and shortlist

The new **Nearby hotels** panel accepts a five-digit ZIP string and calls
`GET /api/hotels?postcode=16802`. The backend verifies the U.S. postcode, then
requests Geoapify `accommodation.hotel` places within 5,000 meters of the
returned point. Results are capped at 20 and are not an exhaustive inventory.
Invalid or outside-radius coordinates and duplicate IDs are omitted. Missing
names and addresses have explicit fallback labels. No prices or availability
are inferred from this data. Selecting a list item or map marker shares the
same place ID. Leaflet 1.9.4 uses OpenStreetMap tiles with visible attribution;
no private key is sent to the tile provider or embedded in Vue.

`backend/places.py` owns provider lookup and normalization. Errors are 422 for
invalid ZIP input, 404 for an unresolved ZIP, 503 for absent configuration,
429 for provider rate limiting, and 502 for other provider failures. An empty
successful result is distinct from these errors. Each backend provider call
uses a 10-second timeout; Vue stops waiting after 30 seconds.

`backend/shortlist.py` stores returned places in additive `discovered_places`
and `shortlist` SQLite tables. Existing sample tables are preserved. A place
snapshot contains `provider`, `place_id`, available `name` and `address`,
`latitude`, `longitude`, originating search `postcode`, and `distance_m`.
Saved entries also contain `saved_at`. Geoapify is the only supported provider;
its place ID is the primary key. Saved snapshots remain independent of future
searches. This local shortlist is shared across demo travelers.

- `GET /api/shortlist`: saved snapshots.
- `POST /api/shortlist?place_id=...`: save a previously returned place;
  repeated saves return `created: false` without adding another row.
- `DELETE /api/shortlist?place_id=...`: remove a saved place, returning 204.

Use the startup commands below. Changes to backend Python or `.env` require
a backend restart with those commands. Keep `backend/storage/expedia.sqlite3`
to retain the shortlist. No new Python packages are required. Leaflet was
installed after student approval with
`npm.cmd --prefix frontend install leaflet@1.9.4 --save-exact`.

Run all backend checks without live provider requests:

```powershell
Push-Location backend
.\.venv\Scripts\python.exe -m unittest discover -v
Pop-Location
npm.cmd --prefix frontend run build
```

See the [Assignment 2 report draft](docs/assignment2-report.md),
[verification record](docs/assignment2-verification.md), and
[research and early design](docs/assignment2-research-and-design.md).
The earlier recording and published checkpoint below cover the previous
booking assignment, not this new hotel-map/shortlist work.

A local classroom travel application: Vue frontend, Python/FastAPI API, and SQLite hotel search with simulated booking CRUD. The supplied fictional CSV data is preserved in backend/data/ and imported once. No real reservations are made.

## Part 2 demonstration video

[Watch the Part 2 demonstration (MP4, approximately 21 MB)](https://github.com/kuanenlee0925-blip/expedia-lite/raw/refs/heads/main/media/part2-demonstration.mp4)

This recording was made before the application was renamed from Expedia Lite to Brian Booking Plus, so the earlier name appears in the video. The link opens or downloads the recording, depending on your browser; no GitHub sign-in is required.

## Setup (Windows PowerShell)

Open a terminal in this `Brian Booking Plus` folder. Python 3.10+ and Node 22.12+ are required (verified here with Python 3.14.7 and Node 24.20.0).

Check first: `python --version`, `node --version`, and `npm.cmd --version`. For an existing environment, check `backend\.venv\Scripts\python.exe -m pip show fastapi uvicorn` and `npm.cmd --prefix frontend ls --depth=0` before installing.

For a fresh checkout:

```powershell
python -m venv backend/.venv
backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm.cmd --prefix frontend ci
```

Verify:

```powershell
backend\.venv\Scripts\python.exe -c "import fastapi, uvicorn; print(fastapi.__version__, uvicorn.__version__)"
npm.cmd --prefix frontend run build
```

## Run

### Backend ZIP controller contract

`backend/zip_lookup.py` exposes `lookup_zip(postcode: str) -> dict | None`.
The input must be a five-digit ASCII ZIP string, preserving leading zeros.
`GET /api/demo/zip-location?postcode=16802` calls this controller with the
entered ZIP and returns the location as JSON. Omitting `postcode` retains the
original fixed `16802` demonstration. Invalid input returns HTTP 422 before
any provider request. Missing configuration
returns HTTP 503, an unresolved ZIP returns HTTP 404, and provider failure
returns HTTP 502, each with a safe `detail` message. The Vue app's
"ZIP lookup demonstration" panel calls this local route through the existing
`/api` proxy when the ZIP form is submitted with "Look up ZIP". It displays
loading feedback, then a table with postcode, country code, locality, latitude,
and longitude, or a backend error. The input and button are disabled while
loading, and an earlier result is cleared at the start of a new lookup.
The controller uses Python's built-in `urllib.request` with a 10-second socket
timeout and the key from `backend/config.py`. It calls Geoapify's
[forward geocoding API](https://apidocs.geoapify.com/docs/geocoding/) with
`postcode`, `type=postcode`, `filter=countrycode:us`, and `format=json`.
The key is supplied only in the backend request and is never logged or returned.

A successful result contains `postcode`, `country_code` (`"us"`), `latitude`,
`longitude`, and optional `locality` (city, town, or village). Only an exact
postcode match in the US with finite numeric coordinates in valid latitude
and longitude ranges is accepted. This location response is separate from
the sample hotel/stay model and has no price.

`None` means no acceptable location was resolved, including mismatched
locations or invalid coordinates. `ZipLookupError` means configuration is
missing, the provider request failed (including HTTP errors or timeouts), or
the response is malformed. Its messages omit credentials, request URLs, and
raw provider exception text. Invalid input raises `ValueError` before HTTP.
Mocked checks: from `backend/`, run
`.\.venv\Scripts\python.exe -m unittest -v test_zip_lookup test_zip_route`.
These checks make no live provider calls.

### Local startup

Backend configuration lives in `.env` in this project root, beside `frontend/`
and `backend/`. Set `GEOAPIFY_API_KEY` there. `backend/config.py` loads that
explicit path at startup, independent of the working directory; an existing
process environment variable takes precedence. After editing `.env`, stop and
restart the backend (Ctrl+C, then rerun the backend command below). Restart is
required because configuration is read once when the backend process starts.
`GET /api/health` returns `status: "ok"` and a `geoapify` field containing
`"key is configured"` or `"key is not configured"`; absent, empty, and
whitespace-only values count as not configured. It never returns the key or
calls Geoapify, and configuration status does not verify key validity.

Terminal 1, from this folder:

```powershell
backend\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Terminal 2, from this folder:

```powershell
npm.cmd --prefix frontend run dev
```

Open http://127.0.0.1:5173. Stop each server with Ctrl+C. API documentation: http://127.0.0.1:8000/docs. Vite forwards `/api` requests to FastAPI; use the development server for the complete local app. The build check creates frontend/dist but is not a standalone backend deployment.

## Search and verification

Search `Harbor Lantern Hotel`: expect T001 and T009, each two nights at $150/night ($300/stay). Search `No Such Hotel`: expect a clear empty result. Partial names and capitalization are ignored; blank input lists all 12 stays. Search is by hotel name, not city. Dates are fixed offered stays; sample dates are not filtered against today's date.

See [report.md](report.md) for observed browser checks and screenshots. The Part 2 recording has been supplied and the Part 2 report is published. A separate confirmation of the required Part 2 VS Code source scan has not been recorded. See [the review checklist](docs/review-checklist.md). Repository: [expedia-lite](https://github.com/kuanenlee0925-blip/expedia-lite). The `part1` tag preserves the reviewed Part 1 application checkpoint; the report records its exact hash. The repository is public, so the instructor can open the report and evidence links without an invitation.

## Project context

- [Agent instructions](AGENTS.md)
- [Design](docs/design.md)
- [Selected prompts](prompts/selected.md)
- [Current handoff](handoffs/current.md)
- [Original data guide](backend/data/README.md)

## Part 2: bookings and storage

Select a demo traveler, search for a hotel, and click **Book stay**. The new confirmed booking appears in that traveler's history. **Cancel booking** retains its row with status cancelled. **Delete booking → Confirm delete** removes a test booking. Refresh history after a connection error before retrying a mutation; a lost response does not prove that the server rejected it.

The database is `backend/storage/expedia.sqlite3`, excluded from Git. First startup imports 8 hotels, 12 trips, 6 users, and 6 bookings in one transaction. Later startups check a saved seed marker and reopen the database without reading CSVs. New IDs use a `B-` prefix plus a UUID and a database primary-key constraint. Keep this database file to preserve your changes. An optional `TRAVEL_DB_PATH` environment variable selects a different database; use an absolute path.

Browser refresh resets the traveler selector to Traveler 1. Select your traveler again to see their saved history. This does not reset the database. The September 15 agent checks retained two U006 records (one confirmed and one cancelled). Later personal demonstrations may have added records. A fresh checkout begins with the six supplied bookings; local databases are not uploaded.

## Automated verification

The runtime dependencies are in backend/requirements.txt. API tests additionally need httpx, checked before installation and pinned in requirements-dev.txt:

```powershell
backend\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
Push-Location backend
.\.venv\Scripts\python.exe -m unittest -v test_app
Pop-Location
npm.cmd --prefix frontend run build
```

The seven tests create disposable databases and check seeding, joins, all CRUD actions, validation, concurrent ID uniqueness, rollback, and persistence across application restarts. They do not change the student's saved database. The installed Starlette version emits a deprecation notice for httpx in its test client; tests pass with the pinned dependency.

## Review and submission status

The Part 2 publication contains SQLite booking CRUD, screenshots, and the student video link. The application checkpoint is [0743984](https://github.com/kuanenlee0925-blip/expedia-lite/commit/0743984eb768de1605ff62ed8fd0b4b33a4f35e3); all seven backend tests and the frontend build passed after merging into main on September 29, 2026. The existing GitHub repository keeps its `expedia-lite` URL; the `part1` tag preserves the original checkpoint. See [report.md](report.md) for the exact published application commit and actual checks. The required student VS Code source scan has not been separately confirmed. Upload report.md to Canvas after completing that review; GitHub publication is not Canvas submission. [Part 1 report archive](docs/part1-report.md) preserves the prior report. Newer Assignment 2 ZIP/nearby-hotel work is outside this checkpoint.

This local working folder also contains newer ZIP lookup, nearby-hotel, and shortlist work. Those additions were preserved locally and are not included in the Part 2 GitHub checkpoint.
