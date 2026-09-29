# Brian Booking Plus

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

See [report.md](report.md) for observed browser checks and screenshots. The student supplied the Part 2 demonstration recording; a separate confirmation of the Part 2 VS Code source scan has not been recorded. See [the review checklist](docs/review-checklist.md). Repository: [expedia-lite](https://github.com/kuanenlee0925-blip/expedia-lite). The `part1` tag preserves the reviewed Part 1 application checkpoint; the report records its exact hash. The repository is public, so the instructor can open the report and evidence links without an invitation.

## Project context

- [Agent instructions](AGENTS.md)
- [Design](docs/design.md)
- [Selected prompts](prompts/selected.md)
- [Current handoff](handoffs/current.md)
- [Original data guide](backend/data/README.md)

## Part 2: bookings and storage

Select a demo traveler, search for a hotel, and click **Book stay**. The new confirmed booking appears in that traveler's history. **Cancel booking** retains its row with status cancelled. **Delete booking → Confirm delete** removes a test booking. Refresh history after a connection error before retrying a mutation; a lost response does not prove that the server rejected it.

The database is `backend/storage/expedia.sqlite3`, excluded from Git. First startup imports 8 hotels, 12 trips, 6 users, and 6 bookings in one transaction. Later startups check a saved seed marker and reopen the database without reading CSVs. New IDs use a `B-` prefix plus a UUID and a database primary-key constraint. Keep this database file to preserve your changes. An optional `TRAVEL_DB_PATH` environment variable selects a different database; use an absolute path.

Browser refresh resets the traveler selector to Traveler 1. Select your traveler again to see their saved history. This does not reset the database. The September 15 agent checks retained two U006 records (one confirmed and one cancelled). A fresh checkout starts with the six supplied bookings; personal demo records and the local database are not uploaded.

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

The Part 2 publication contains SQLite booking CRUD, screenshots, and the student video link. The existing GitHub repository keeps its `expedia-lite` URL; the `part1` tag preserves the original checkpoint. See [report.md](report.md) for the exact published application commit and actual checks. The required student VS Code source scan has not been separately confirmed. Upload report.md to Canvas after completing that review; GitHub publication is not Canvas submission. [Part 1 report archive](docs/part1-report.md) preserves the prior report. Newer Assignment 2 ZIP/nearby-hotel work is outside this checkpoint.
