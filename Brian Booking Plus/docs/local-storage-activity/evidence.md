# Local Hotel Storage and Manual Verification — evidence

Prepared October 1, 2026. This is a template plus agent verification record,
not a claim that the student's five manual benchmarks are complete.

## Implementation and environment

- Frontend http://127.0.0.1:5173/; backend http://127.0.0.1:8000.
- Database `backend/storage/expedia.sqlite3`; absolute path in the
  [manual checklist](manual-checklist.md).
- Published pre-activity checkpoint: `7afcdf2` (application foundation
  `2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e`). The named feature branch
  `assignment2_part2_in_class` is prepared in the isolated checkout at
  `C:/Users/kuane/AppData/Local/Temp/brian-booking-plus-assignment2-publish-20260929`.
  The running application stays in the existing Documents folder and uses
  the existing database. Activity application checkpoint [7a0b188f3dc3d385f1a9f520ba28cc4f091d7160](https://github.com/kuanenlee0925-blip/expedia-lite/commit/7a0b188f3dc3d385f1a9f520ba28cc4f091d7160)
  was committed and pushed to `assignment2_part2_in_class` on October 1 at the student's request. The older original checkout's
  branch was not switched over its existing working changes.
- New additive tables preserve Assignment 1 data; Part 1 provider endpoints,
  request/response contract, ZIP controller, and Leaflet component are preserved.
- No packages installed. No chatbot or model integration added.

## Student manual evidence — complete these fields

Observation date/time: **pending**. Searched ZIP: **pending**.
Comparison hotel name/provider ID: **pending**. Stay date: **pending**.
Before cents/rooms: **pending**. After cents/rooms and displayed dollars: **pending**.
Demonstrated to instructor/TA: **not confirmed**.

| Benchmark | Expected | Student observation / evidence |
| --- | --- | --- |
| 1. Schema | Saved hotel fields, hotel/date key, foreign key, 10000/20 defaults; Assignment 1 rows preserved | Pending DB Browser inspection and screenshot |
| 2. Add and retain | One hotel, searched ZIP association, five nights October 10–14; Add disabled; retained after refresh/search; no duplicate/overwrite | Pending |
| 3. Remove | Selected saved hotel and related rows removed; other records remain; UI updates | Pending |
| 4. Local-first | Saved ZIP uses only local hotel lookup; successful empty local lookup falls back; failure shows error | Pending Network-panel evidence |
| 5. Edit and reread | After Write Changes, same hotel/date shows committed dollars and rooms | Pending student edit and before/after screenshots |

## Automated checks (separate from manual observations)

Observed October 1: **31 backend tests**, **5 frontend lookup tests**, and
the Vite production build passed. Existing Starlette TestClient deprecation
warning remains. Tests use temporary databases and synthetic provider responses.

Repeat from the app root:

```powershell
Push-Location backend
.\.venv\Scripts\python.exe -m unittest discover -v
Pop-Location
node --test frontend/src/localHotelSearch.test.js
npm.cmd --prefix frontend run build
```

Checks cover migration repeatability, defaults, primary/foreign keys, invalid
dates/values, preserved original records, duplicate saves, committed edits and
restart reread, multiple ZIP associations, cascading removal, rollback on
failure, API contract preservation, leading zeros, and the local lookup/fallback
decision. The first build attempt hit a sandbox parent-directory permission
error; the same build passed with permitted execution. No package update was used.

[Before-migration fingerprints](before-migration.json) and
[migration comparison](migration-check.json) show unchanged Assignment 1,
shortlist, and discovered-place rows immediately after migration, plus no
foreign-key violations. These are agent read-only SQLite checks, not DB Browser
screenshots or student observations.

## Agent browser observations — FIXTURES, not live provider evidence

A temporary fixture backend served the built frontend at port 8001, with a
separate disposable SQLite database. It used `backend/data/places-fixture.json`;
no live geocoding/Places calls were made. Standard map tiles loaded normally.

| Action | Expected | Agent observed |
| --- | --- | --- |
| Search fixture ZIP 16802 with empty local DB | Local then status then Part 1 endpoint | API results with two synthetic hotels; server access log confirms sequence |
| Add Fixture Hotel A | Confirm save, disable Add, offer Remove | Observed |
| Repeat search | Saved locally, five $100/20 dated rows | Observed October 10–14; no Part 1 request in server access log |
| Commit fixture edit with Python, refresh and search | 2026-10-10 shows $123.45 / 7 | Observed; other four dates remained $100 / 20 |
| Keyboard Enter on Remove | Local card/map and related rows removed | Observed; all four related tables empty; eight starter hotels and six fixture bookings remained |
| Simulated local DB error | Error, no provider fallback | Observed safe storage-error message and local HTTP 503 only |
| Restore fixture storage | Successful empty fallback resumes | Observed; failure simulation removed afterward |
| Select list item 2, then marker 1 | Matching map/list selection both ways | Observed |

[Fixture defaults screenshot](fixture-defaults.png) and
[fixture reread screenshot](fixture-reread.png) are labeled synthetic examples.
The fixture server was stopped after checks. **The Python fixture edit is not
the student's DB Browser edit or Write Changes demonstration.** Live searches,
manual database edits, Network-panel inspection, and instructor review remain
for the student. No screenshots or test output expose credentials.
