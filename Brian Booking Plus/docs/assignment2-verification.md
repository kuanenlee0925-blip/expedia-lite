# Assignment 2 verification — September 29, 2026

## Repeatable checks

From the project root, run:

```powershell
Push-Location backend
.\.venv\Scripts\python.exe -m unittest discover -v
Pop-Location
npm.cmd --prefix frontend run build
```

Observed: all 24 backend tests passed; the final Vue/Vite build passed.
Starlette reports its existing TestClient/httpx deprecation warning.
The tests use temporary databases and mocked HTTP calls, not live provider quota.
[Fixed JSON sample](../backend/data/places-fixture.json) is synthetic test data,
not evidence of live hotel results. Repeat only its checks with
`backend\.venv\Scripts\python.exe -m unittest discover -s backend -p test_places.py -v`.

| Input/action | Expected | Observed |
| --- | --- | --- |
| Fixed fixture | Two usable nearby places; far-away record omitted; missing fields retained honestly | Passed |
| Empty features / malformed payload | Empty success / safe provider error | Passed |
| Unresolved ZIP | No Places request | Passed |
| Simulated HTTP 500 / 429 | Safe failure / rate-limit response | Passed; raw exception text excluded |
| Duplicate save | One SQLite row | Passed; second POST reports created=false |
| Delete discovered snapshot, restart test app | Saved snapshot remains recognizable | Passed |
| Remove, restart test app | Empty shortlist; six starter users preserved | Passed |
| Invalid route input | 422 without calling provider controller | Passed |
| Live ZIP 16802 | Usable real hotels within requested radius, map markers matching list | Observed 20 returned hotels on September 29; count is not a future assertion |
| Click list item 2 | Map identifies Hotel State College | Popup and selected list state matched |
| Click marker 3 | List identifies Nittany Lion Inn | Selected list state and popup matched |
| Save Hotel State College, refresh page, restart backend | Same snapshot and saved timestamp | Observed; screenshots and SQLite snapshot linked below |
| Keyboard Enter on Remove | Saved test entry disappears | Observed removal and empty shortlist |
| Existing search: Harbor Lantern Hotel | T001 and T009, each $300 | Observed both rows with expected prices |

## Evidence

- [Live list and map](screenshots/assignment2/01-live-map.png)
- [Saved entry after backend restart and page reload](screenshots/assignment2/02-after-restart.png)
- [SQLite saved snapshot before restart](screenshots/assignment2/sqlite-before-restart.json)

The demonstration entry created by the agent was removed afterward. No original
booking or starter record was removed. Provider calls were not repeated for
failure scenarios. The existing backend was restarted only to load this work
and verify persistence; unrelated processes were preserved.

## Corrections and remaining checks

- Corrected an extra closing parenthesis in the new test before rerunning it.
- Closed simulated HTTPError objects to avoid resource warnings that could
  otherwise include credential-bearing URLs.
- Limited list height after the live 20-result screen made the page too long.
- Clarified the footer so fictional sample bookings are distinct from real
  provider locations.

Not verified here: full browser-process close/reopen, every control through a
keyboard-only journey, narrow mobile layout, UI rendering under mocked provider
failure/empty/quota responses, browser Network-panel credential inspection,
or a screen-recorded Assignment 2 demonstration. Backend fixtures cover the
provider error cases; they are not a claim of browser-level verification.
The tests do not prove future provider coverage or availability. Following verification, application commit `2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e` was published to GitHub
at the student's explicit request. No Canvas submission or instructor review
was performed.
